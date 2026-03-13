#!/usr/bin/env python3
"""
HWPX 문서 읽기/편집 — 표준 라이브러리만 사용

Usage:
    # 텍스트 추출
    python hwpx_reader.py read document.hwpx

    # 편집 (unpack → callback → repack)
    python hwpx_reader.py unpack document.hwpx ./unpacked
    # ... section0.xml 등 편집 ...
    python hwpx_reader.py repack ./unpacked ./output/edited.hwpx

    # 프로그래밍 사용
    from hwpx_reader import HwpxReader
    reader = HwpxReader("document.hwpx")
    print(reader.extract_text())
    print(reader.get_xml("Contents/section0.xml"))
"""

import os
import re
import zipfile
import shutil
from xml.etree import ElementTree as ET
from typing import Optional

NS = {
    "hp": "http://www.hancom.co.kr/hwpml/2011/paragraph",
    "hs": "http://www.hancom.co.kr/hwpml/2011/section",
    "hc": "http://www.hancom.co.kr/hwpml/2011/core",
    "hh": "http://www.hancom.co.kr/hwpml/2011/head",
}

# ElementTree 네임스페이스 등록
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)


class HwpxReader:
    """HWPX 파일 읽기 및 분석."""

    def __init__(self, path: str):
        self.path = path
        if not os.path.exists(path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")

    def list_files(self) -> list[str]:
        """ZIP 내 파일 목록."""
        with zipfile.ZipFile(self.path, "r") as zf:
            return zf.namelist()

    def get_raw(self, inner_path: str) -> bytes:
        """ZIP 내 파일 원본 바이트."""
        with zipfile.ZipFile(self.path, "r") as zf:
            return zf.read(inner_path)

    def get_xml(self, inner_path: str) -> str:
        """ZIP 내 XML 파일을 문자열로 반환."""
        return self.get_raw(inner_path).decode("utf-8")

    def parse_xml(self, inner_path: str) -> ET.Element:
        """ZIP 내 XML 파일을 ElementTree로 파싱."""
        return ET.fromstring(self.get_raw(inner_path))

    def extract_text(self, section: str = "Contents/section0.xml") -> str:
        """본문 텍스트 추출. hp:t 요소의 텍스트를 문단별 줄바꿈으로 결합."""
        root = self.parse_xml(section)
        paragraphs = []
        for p_elem in root.iter(f'{{{NS["hp"]}}}p'):
            texts = []
            for t_elem in p_elem.iter(f'{{{NS["hp"]}}}t'):
                if t_elem.text:
                    texts.append(t_elem.text)
            if texts:
                paragraphs.append("".join(texts))
        return "\n".join(paragraphs)

    def get_styles(self) -> dict:
        """header.xml에서 스타일 정보 추출."""
        root = self.parse_xml("Contents/header.xml")
        result = {"charPr": [], "paraPr": [], "fonts": []}

        for cp in root.iter(f'{{{NS["hh"]}}}charPr'):
            result["charPr"].append(cp.attrib)
        for pp in root.iter(f'{{{NS["hh"]}}}paraPr'):
            result["paraPr"].append(pp.attrib)
        for font in root.iter(f'{{{NS["hh"]}}}font'):
            result["fonts"].append(font.attrib)

        return result


def unpack(hwpx_path: str, dest_dir: str) -> str:
    """HWPX를 디렉토리에 풀기."""
    os.makedirs(dest_dir, exist_ok=True)
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        zf.extractall(dest_dir)
    # linesegarray 자동 제거
    _remove_linesegarray(dest_dir)
    return dest_dir


def repack(source_dir: str, output_path: str) -> str:
    """디렉토리를 HWPX로 다시 패키징."""
    import io
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype 먼저, 비압축
        mimetype_path = os.path.join(source_dir, "mimetype")
        if os.path.exists(mimetype_path):
            with open(mimetype_path, "r") as f:
                zf.writestr(
                    zipfile.ZipInfo("mimetype"), f.read(),
                    compress_type=zipfile.ZIP_STORED,
                )

        # 나머지 파일들
        for root, dirs, files in os.walk(source_dir):
            for fname in sorted(files):
                if fname == "mimetype":
                    continue
                full = os.path.join(root, fname)
                arcname = os.path.relpath(full, source_dir)
                zf.write(full, arcname)

    with open(output_path, "wb") as f:
        f.write(buf.getvalue())

    return os.path.abspath(output_path)


def _remove_linesegarray(dest_dir: str):
    """linesegarray 요소 제거 (레이아웃 캐시, 편집 시 꼬임 방지)."""
    pattern = re.compile(
        r"<hp:linesegarray>.*?</hp:linesegarray>", re.DOTALL
    )
    for root, _, files in os.walk(dest_dir):
        for fname in files:
            if fname.endswith(".xml"):
                fpath = os.path.join(root, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                cleaned = pattern.sub("", content)
                if cleaned != content:
                    with open(fpath, "w", encoding="utf-8") as f:
                        f.write(cleaned)


# ── CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HWPX 읽기/편집 도구")
    sub = parser.add_subparsers(dest="command")

    # read
    p_read = sub.add_parser("read", help="텍스트 추출")
    p_read.add_argument("file", help="HWPX 파일 경로")

    # unpack
    p_unpack = sub.add_parser("unpack", help="HWPX → 디렉토리")
    p_unpack.add_argument("file", help="HWPX 파일 경로")
    p_unpack.add_argument("dest", help="출력 디렉토리")

    # repack
    p_repack = sub.add_parser("repack", help="디렉토리 → HWPX")
    p_repack.add_argument("source", help="소스 디렉토리")
    p_repack.add_argument("output", help="출력 HWPX 경로")

    args = parser.parse_args()

    if args.command == "read":
        reader = HwpxReader(args.file)
        print(reader.extract_text())
    elif args.command == "unpack":
        unpack(args.file, args.dest)
        print(f"풀기 완료: {args.dest}")
    elif args.command == "repack":
        result = repack(args.source, args.output)
        print(f"패키징 완료: {result}")
    else:
        parser.print_help()
