#!/usr/bin/env python3
"""
데이터 파일 프로세서 — 연구노트 삽입용 데이터 변환

사용자가 제공한 데이터 파일(CSV, JSON, XML, 텍스트/로그, 이미지 등)을
연구노트에 삽입하기 적합한 표준 구조로 변환한다.

Usage:
    from data_processor import DataProcessor

    proc = DataProcessor()
    result = proc.process("experiment_data.csv")
    print(result.format)   # "table"
    print(result.data)     # [["col1","col2"], ["v1","v2"], ...]
    print(result.summary)  # "3열 100행 CSV 데이터 (20행 발췌)"

CLI:
    python data_processor.py <filepath>
    python data_processor.py <filepath> --json
"""

import csv
import io
import json
import os
import re
import statistics
import struct
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


# ── DataResult ──────────────────────────────────────────────

@dataclass
class DataResult:
    """데이터 처리 결과 표준 구조."""
    format: str            # "table" | "code_block" | "summary" | "image_ref"
    data: Any              # 2D list (table), str (code_block/summary), dict (image_ref)
    summary: str           # 사람이 읽을 수 있는 요약
    row_count: int = 0     # 원본 행 수 (해당 없으면 0)
    truncated: bool = False  # 데이터가 발췌/요약되었는지
    source_path: str = ""  # 원본 파일 경로
    source_format: str = ""  # "csv"|"tsv"|"json"|"yaml"|"xml"|"text"|"image"

    def to_dict(self) -> dict:
        return asdict(self)


# ── DataProcessor ───────────────────────────────────────────

class DataProcessor:
    """데이터 파일을 연구노트 삽입용 구조로 변환."""

    # 행 발췌 기준
    MAX_TABLE_ROWS = 20
    EXCERPT_HEAD = 10
    EXCERPT_TAIL = 5

    # 텍스트/로그 발췌 기준
    MAX_TEXT_LINES = 50
    EXCERPT_TEXT_HEAD = 20
    MAX_LOG_EXCERPTS = 30

    # 확장자 → 포맷 매핑
    _EXT_MAP = {
        ".csv": "csv", ".tsv": "tsv",
        ".json": "json", ".jsonl": "json",
        ".yaml": "yaml", ".yml": "yaml",
        ".xml": "xml",
        ".png": "image", ".jpg": "image", ".jpeg": "image",
        ".gif": "image", ".bmp": "image", ".tiff": "image", ".tif": "image",
        ".webp": "image", ".svg": "image",
    }

    def process(self, filepath: str) -> DataResult:
        """파일을 처리하여 DataResult 반환."""
        filepath = os.path.abspath(filepath)
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {filepath}")

        fmt = self._detect_format(filepath)
        encoding = "binary" if fmt == "image" else self._detect_encoding(filepath)

        handler = {
            "csv": self._process_csv,
            "tsv": self._process_csv,
            "json": self._process_json,
            "yaml": self._process_yaml,
            "xml": self._process_xml,
            "image": self._process_image,
            "text": self._process_text,
        }.get(fmt, self._process_text)

        if fmt == "image":
            result = handler(filepath)
        else:
            result = handler(filepath, encoding)

        result.source_path = filepath
        result.source_format = fmt
        return result

    # ── 포맷 감지 ──

    def _detect_format(self, filepath: str) -> str:
        ext = os.path.splitext(filepath)[1].lower()
        return self._EXT_MAP.get(ext, "text")

    def _detect_encoding(self, filepath: str) -> str:
        """UTF-8 → CP949 → EUC-KR 순으로 인코딩 감지."""
        with open(filepath, "rb") as f:
            raw = f.read(8192)

        # BOM 체크
        if raw[:3] == b"\xef\xbb\xbf":
            return "utf-8-sig"

        for enc in ("utf-8", "cp949", "euc-kr"):
            try:
                raw.decode(enc)
                return enc
            except (UnicodeDecodeError, ValueError):
                continue
        return "utf-8"

    # ── CSV / TSV ──

    def _process_csv(self, filepath: str, encoding: str) -> DataResult:
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            sample = f.read(8192)

        # 구분자 감지
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",\t;|")
        except csv.Error:
            ext = os.path.splitext(filepath)[1].lower()
            delimiter = "\t" if ext == ".tsv" else ","
            dialect = None

        with open(filepath, "r", encoding=encoding, errors="replace", newline="") as f:
            if dialect:
                reader = csv.reader(f, dialect)
            else:
                reader = csv.reader(f, delimiter=delimiter)
            rows = list(reader)

        if not rows:
            return DataResult(
                format="summary", data="빈 파일입니다.",
                summary="빈 CSV/TSV 파일", row_count=0,
            )

        # 빈 행 제거
        rows = [r for r in rows if any(cell.strip() for cell in r)]
        if not rows:
            return DataResult(
                format="summary", data="유효한 데이터가 없습니다.",
                summary="빈 CSV/TSV 파일", row_count=0,
            )

        header = rows[0]
        data_rows = rows[1:]
        col_count = len(header)
        total_rows = len(data_rows)

        truncated = total_rows > self.MAX_TABLE_ROWS
        if truncated:
            excerpt = data_rows[: self.EXCERPT_HEAD] + data_rows[-self.EXCERPT_TAIL :]
            table_data = [header] + excerpt
            stats = self._compute_column_stats(header, data_rows)
            summary = (
                f"{col_count}열 {total_rows}행 CSV 데이터 "
                f"(상위 {self.EXCERPT_HEAD}행 + 하위 {self.EXCERPT_TAIL}행 발췌)\n"
                f"통계: {stats}"
            )
        else:
            table_data = [header] + data_rows
            summary = f"{col_count}열 {total_rows}행 CSV 데이터"

        return DataResult(
            format="table", data=table_data, summary=summary,
            row_count=total_rows, truncated=truncated,
        )

    def _compute_column_stats(self, header: list[str], rows: list[list[str]]) -> str:
        """숫자 열의 기초 통계를 계산."""
        stats_parts = []
        for i, col_name in enumerate(header):
            values = []
            for row in rows:
                if i < len(row):
                    try:
                        values.append(float(row[i].replace(",", "")))
                    except (ValueError, AttributeError):
                        continue
            if len(values) >= 2:
                stats_parts.append(
                    f"{col_name}(min={min(values):.4g}, max={max(values):.4g}, "
                    f"avg={statistics.mean(values):.4g})"
                )
        return ", ".join(stats_parts) if stats_parts else "숫자 열 없음"

    # ── JSON ──

    def _process_json(self, filepath: str, encoding: str) -> DataResult:
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            content = f.read()

        # JSONL 지원
        if filepath.endswith(".jsonl"):
            lines = [l.strip() for l in content.strip().split("\n") if l.strip()]
            try:
                data = [json.loads(l) for l in lines]
            except json.JSONDecodeError as e:
                return DataResult(
                    format="code_block", data=content[:3000],
                    summary=f"JSONL 파싱 오류: {e}", row_count=0,
                )
        else:
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                return DataResult(
                    format="code_block", data=content[:3000],
                    summary=f"JSON 파싱 오류: {e}", row_count=0,
                )

        # 리스트 of 딕트 → 테이블 변환
        if isinstance(data, list) and data and isinstance(data[0], dict):
            keys = list(data[0].keys())
            rows = [[str(item.get(k, "")) for k in keys] for item in data]
            total_rows = len(rows)
            truncated = total_rows > self.MAX_TABLE_ROWS
            if truncated:
                excerpt = rows[: self.EXCERPT_HEAD] + rows[-self.EXCERPT_TAIL :]
                table_data = [keys] + excerpt
            else:
                table_data = [keys] + rows
            return DataResult(
                format="table", data=table_data,
                summary=f"{len(keys)}열 {total_rows}행 JSON 배열 데이터",
                row_count=total_rows, truncated=truncated,
            )

        # 딕트 → 키-값 테이블
        if isinstance(data, dict):
            flat = self._flatten_dict(data)
            table_data = [["키", "값"]] + [[k, str(v)] for k, v in flat.items()]
            return DataResult(
                format="table", data=table_data,
                summary=f"JSON 객체 ({len(flat)}개 필드)",
                row_count=len(flat),
            )

        # 기타 → 코드 블록
        formatted = json.dumps(data, ensure_ascii=False, indent=2)
        if len(formatted) > 3000:
            formatted = formatted[:3000] + "\n... (truncated)"
        return DataResult(
            format="code_block", data=formatted,
            summary=f"JSON 데이터 ({type(data).__name__})",
        )

    def _flatten_dict(self, d: dict, prefix: str = "") -> dict:
        """중첩 딕트를 평탄화 (최대 2단계)."""
        result = {}
        for k, v in d.items():
            key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict) and not prefix:
                result.update(self._flatten_dict(v, key))
            elif isinstance(v, list):
                if len(v) <= 5:
                    result[key] = ", ".join(str(x) for x in v)
                else:
                    result[key] = f"[{len(v)}개 항목] {', '.join(str(x) for x in v[:3])}, ..."
            else:
                result[key] = v
        return result

    # ── YAML (경량 파서) ──

    def _process_yaml(self, filepath: str, encoding: str) -> DataResult:
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            content = f.read()

        parsed = self._parse_simple_yaml(content)
        if parsed:
            table_data = [["키", "값"]] + [[k, str(v)] for k, v in parsed.items()]
            return DataResult(
                format="table", data=table_data,
                summary=f"YAML 데이터 ({len(parsed)}개 필드)",
                row_count=len(parsed),
            )

        # 파싱 실패 시 코드 블록으로
        if len(content) > 3000:
            content = content[:3000] + "\n... (truncated)"
        return DataResult(
            format="code_block", data=content,
            summary="YAML 파일 (구조화 텍스트)",
        )

    def _parse_simple_yaml(self, text: str) -> Optional[dict]:
        """단순 key: value YAML 파싱 (중첩 미지원)."""
        result = {}
        current_key = None
        current_list = None

        for line in text.split("\n"):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped == "---":
                continue

            # key: value
            m = re.match(r'^([A-Za-z0-9_\-\uac00-\ud7a3]+)\s*:\s*(.*)', stripped)
            if m:
                if current_key and current_list is not None:
                    result[current_key] = ", ".join(current_list)
                current_key = m.group(1)
                value = m.group(2).strip()
                if value:
                    result[current_key] = value
                    current_list = None
                else:
                    current_list = []
                continue

            # - item (리스트)
            if stripped.startswith("- ") and current_key:
                if current_list is None:
                    current_list = []
                current_list.append(stripped[2:].strip())
                continue

        if current_key and current_list is not None:
            result[current_key] = ", ".join(current_list)

        return result if result else None

    # ── XML ──

    def _process_xml(self, filepath: str, encoding: str) -> DataResult:
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
        except ET.ParseError as e:
            with open(filepath, "r", encoding=encoding, errors="replace") as f:
                content = f.read()[:3000]
            return DataResult(
                format="code_block", data=content,
                summary=f"XML 파싱 오류: {e}",
            )

        # 태그에서 네임스페이스 제거
        def strip_ns(tag):
            return tag.split("}")[-1] if "}" in tag else tag

        # 구조 분석
        elements = []
        for child in root:
            tag = strip_ns(child.tag)
            text = (child.text or "").strip()[:100]
            attrs = {k: v for k, v in child.attrib.items()}
            children_count = len(list(child))
            elements.append({
                "tag": tag, "text": text,
                "attrs": attrs, "children": children_count,
            })

        if not elements:
            text = (root.text or "").strip()
            return DataResult(
                format="summary",
                data=f"루트 요소: <{strip_ns(root.tag)}>, 내용: {text[:500]}",
                summary=f"XML 문서 (루트: {strip_ns(root.tag)})",
            )

        # 반복 요소가 있으면 테이블로 변환
        tag_counts = {}
        for el in elements:
            tag_counts[el["tag"]] = tag_counts.get(el["tag"], 0) + 1

        most_common_tag = max(tag_counts, key=tag_counts.get)
        if tag_counts[most_common_tag] >= 2:
            # 반복 요소의 하위 요소를 열로
            sample_elements = [
                child for child in root if strip_ns(child.tag) == most_common_tag
            ]
            sub_tags = set()
            for el in sample_elements[:5]:
                for sub in el:
                    sub_tags.add(strip_ns(sub.tag))
            sub_tags = sorted(sub_tags)

            if sub_tags:
                header = sub_tags
                rows = []
                for el in sample_elements:
                    row = []
                    for tag in sub_tags:
                        sub_el = el.find(f".//{{{root.tag.split('}')[0][1:]}}}{tag}" if "}" in root.tag else tag)
                        if sub_el is None:
                            # 네임스페이스 없이 재시도
                            for child in el:
                                if strip_ns(child.tag) == tag:
                                    sub_el = child
                                    break
                        row.append((sub_el.text or "").strip() if sub_el is not None else "")
                    rows.append(row)

                total_rows = len(rows)
                truncated = total_rows > self.MAX_TABLE_ROWS
                if truncated:
                    rows = rows[: self.EXCERPT_HEAD] + rows[-self.EXCERPT_TAIL :]
                return DataResult(
                    format="table", data=[header] + rows,
                    summary=f"XML 데이터 ({most_common_tag} × {total_rows}행)",
                    row_count=total_rows, truncated=truncated,
                )

        # 일반 구조 요약
        table_data = [["요소", "내용", "속성", "하위요소"]]
        for el in elements[:30]:
            table_data.append([
                el["tag"],
                el["text"][:80] if el["text"] else "",
                ", ".join(f'{k}={v}' for k, v in el["attrs"].items()) if el["attrs"] else "",
                str(el["children"]) if el["children"] else "",
            ])
        return DataResult(
            format="table", data=table_data,
            summary=f"XML 문서 (루트: {strip_ns(root.tag)}, {len(elements)}개 요소)",
            row_count=len(elements), truncated=len(elements) > 30,
        )

    # ── 텍스트 / 로그 ──

    def _process_text(self, filepath: str, encoding: str) -> DataResult:
        with open(filepath, "r", encoding=encoding, errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        if total_lines == 0:
            return DataResult(
                format="summary", data="빈 파일입니다.",
                summary="빈 텍스트 파일", row_count=0,
            )

        # 로그 패턴 감지
        log_pattern = re.compile(
            r'(ERROR|WARN(?:ING)?|FAIL(?:ED)?|CRITICAL|FATAL)',
            re.IGNORECASE,
        )
        log_lines = []
        for i, line in enumerate(lines):
            if log_pattern.search(line):
                # 전후 2줄 컨텍스트
                start = max(0, i - 2)
                end = min(total_lines, i + 3)
                for j in range(start, end):
                    if j not in [idx for idx, _ in log_lines]:
                        log_lines.append((j, lines[j]))

        is_log = len(log_lines) >= 1 and total_lines > 10

        if total_lines <= self.MAX_TEXT_LINES:
            # 짧은 파일은 전체 포함
            content = "".join(lines)
            return DataResult(
                format="code_block", data=content.rstrip(),
                summary=f"텍스트 파일 ({total_lines}줄)",
                row_count=total_lines,
            )

        if is_log:
            # 로그: 주요 이벤트 발췌
            excerpted = log_lines[: self.MAX_LOG_EXCERPTS]
            content_parts = []
            for idx, line in excerpted:
                content_parts.append(f"[L{idx + 1}] {line.rstrip()}")
            content = "\n".join(content_parts)
            return DataResult(
                format="code_block", data=content,
                summary=f"로그 파일 ({total_lines}줄, ERROR/WARN {len(log_lines)}건 발췌)",
                row_count=total_lines, truncated=True,
            )

        # 일반 텍스트: 앞부분 발췌
        content = "".join(lines[: self.EXCERPT_TEXT_HEAD])
        content += f"\n... ({total_lines - self.EXCERPT_TEXT_HEAD}줄 생략)"
        return DataResult(
            format="code_block", data=content.rstrip(),
            summary=f"텍스트 파일 ({total_lines}줄, 상위 {self.EXCERPT_TEXT_HEAD}줄 발췌)",
            row_count=total_lines, truncated=True,
        )

    # ── 이미지 ──

    def _process_image(self, filepath: str) -> DataResult:
        file_size = os.path.getsize(filepath)
        ext = os.path.splitext(filepath)[1].lower()
        width, height = 0, 0

        try:
            with open(filepath, "rb") as f:
                header = f.read(512)

            if ext == ".png" and header[:8] == b"\x89PNG\r\n\x1a\n":
                width, height = struct.unpack(">II", header[16:24])
            elif ext in (".jpg", ".jpeg") and header[:2] == b"\xff\xd8":
                width, height = self._parse_jpeg_dimensions(filepath)
            elif ext == ".gif" and header[:3] in (b"GIF", ):
                width, height = struct.unpack("<HH", header[6:10])
            elif ext == ".bmp" and header[:2] == b"BM":
                width, height = struct.unpack("<ii", header[18:26])
        except (struct.error, IndexError, IOError):
            pass

        size_str = self._format_file_size(file_size)
        dim_str = f"{width}×{height}" if width and height else "크기 미확인"

        return DataResult(
            format="image_ref",
            data={
                "path": filepath,
                "width": width,
                "height": height,
                "size_bytes": file_size,
                "size_human": size_str,
                "ext": ext.lstrip("."),
            },
            summary=f"이미지 ({ext.lstrip('.')} {dim_str}, {size_str})",
        )

    def _parse_jpeg_dimensions(self, filepath: str) -> tuple[int, int]:
        """JPEG SOF 마커에서 크기 추출."""
        with open(filepath, "rb") as f:
            f.read(2)  # SOI
            while True:
                marker = f.read(2)
                if len(marker) < 2:
                    break
                if marker[0] != 0xFF:
                    break
                marker_type = marker[1]
                if marker_type in (0xC0, 0xC1, 0xC2):  # SOF0, SOF1, SOF2
                    f.read(3)  # length (2) + precision (1)
                    h, w = struct.unpack(">HH", f.read(4))
                    return w, h
                else:
                    length = struct.unpack(">H", f.read(2))[0]
                    f.read(length - 2)
        return 0, 0

    def _format_file_size(self, size: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if size < 1024:
                return f"{size:.1f}{unit}" if unit != "B" else f"{size}B"
            size /= 1024
        return f"{size:.1f}TB"


# ── CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="데이터 파일 → 연구노트 삽입용 변환")
    parser.add_argument("filepath", help="처리할 파일 경로")
    parser.add_argument("--json", action="store_true", help="JSON 형태로 출력")
    args = parser.parse_args()

    proc = DataProcessor()
    result = proc.process(args.filepath)

    if args.json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"포맷: {result.format}")
        print(f"원본: {result.source_format} ({result.source_path})")
        print(f"요약: {result.summary}")
        print(f"행 수: {result.row_count}, 발췌: {result.truncated}")
        print("---")
        if result.format == "table":
            for row in result.data[:25]:
                print(" | ".join(str(c) for c in row))
            if len(result.data) > 25:
                print(f"... ({len(result.data) - 25}행 생략)")
        elif result.format == "code_block":
            print(result.data[:2000])
        elif result.format == "image_ref":
            for k, v in result.data.items():
                print(f"  {k}: {v}")
        else:
            print(result.data)
