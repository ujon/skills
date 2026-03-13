#!/usr/bin/env python3
"""
연구노트 문서 빌더 — 메타데이터·섹션·데이터를 조합하여 최종 문서 생성

수집된 메타데이터, 섹션 본문, 첨부 데이터를 조합하여
HWPX, Markdown, 또는 DOCX/PDF용 JSON 스펙을 생성한다.

Usage:
    from research_note_builder import ResearchNoteBuilder

    note = ResearchNoteBuilder(output_format="hwpx")
    note.set_metadata(과제명="AI 기반 연구", 기록자="홍길동", 작성일자="2026-03-13")
    note.add_section("연구 목적 / 배경", "본 연구는...")
    note.add_section("연구 내용 및 방법", "...")
    note.add_section("결과", "...")
    note.add_signature_block(기록자="홍길동")
    note.save("./output/연구노트_2026-03-13.hwpx")

CLI:
    python research_note_builder.py --format hwpx --title "과제명" --author "기록자" -o ./output/sample.hwpx
"""

import json
import os
import sys
from dataclasses import dataclass, field
from typing import Any, Optional

# ── HwpxBuilder 임포트 ─────────────────────────────────────

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_HWPX_SCRIPTS = os.path.join(_SCRIPT_DIR, "..", "..", "hwpx", "scripts")

# ── 디자인 상수 ──────────────────────────────────────────────

COLOR_HEADER_BG = "#1B3A5C"
COLOR_TABLE_HEADER = "#2E5A88"
COLOR_TABLE_BORDER = "#B0C4DE"
COLOR_SIGNATURE_BG = "#F5F8FC"
COLOR_WHITE = "#FFFFFF"
COLOR_FOOTER_TEXT = "#666666"

DEFAULT_FONT = "맑은 고딕"
DEFAULT_FONT_SIZE = 11
TITLE_FONT_SIZE = 14
SECTION_FONT_SIZE = 12


# ── ResearchNoteBuilder ─────────────────────────────────────

class ResearchNoteBuilder:
    """연구노트 문서 빌더. HWPX / Markdown / JSON 스펙 출력."""

    VALID_FORMATS = ("hwpx", "markdown", "docx_spec", "pdf_spec")

    def __init__(self, output_format: str = "hwpx"):
        if output_format not in self.VALID_FORMATS:
            raise ValueError(f"지원 포맷: {self.VALID_FORMATS}")
        self._format = output_format
        self._metadata: dict[str, str] = {}
        self._font_name = DEFAULT_FONT
        self._font_size = DEFAULT_FONT_SIZE
        self._sections: list[tuple[str, str]] = []
        self._data_attachments: list[dict] = []
        self._signature: dict[str, str] = {}
        self._hf_mode = 1  # 1=both, 2=header, 3=footer, 4=none
        self._hf_opts: dict[str, str] = {}

    # ── 메타데이터 ──

    def set_metadata(
        self,
        과제명: str,
        기록자: str,
        작성일자: str,
        연구제목: Optional[str] = None,
        과제번호: Optional[str] = None,
        연구책임자: Optional[str] = None,
        주관연구기관: Optional[str] = None,
    ) -> "ResearchNoteBuilder":
        self._metadata = {
            "과제명": 과제명,
            "기록자": 기록자,
            "작성일자": 작성일자,
        }
        if 연구제목:
            self._metadata["연구제목"] = 연구제목
        if 과제번호:
            self._metadata["과제번호"] = 과제번호
        if 연구책임자:
            self._metadata["연구책임자"] = 연구책임자
        if 주관연구기관:
            self._metadata["주관연구기관"] = 주관연구기관
        return self

    def set_font(self, font_name: str = DEFAULT_FONT, font_size: int = DEFAULT_FONT_SIZE) -> "ResearchNoteBuilder":
        self._font_name = font_name
        self._font_size = font_size
        return self

    # ── 섹션 ──

    def add_section(self, title: str, content: str) -> "ResearchNoteBuilder":
        self._sections.append((title, content))
        return self

    def add_data_attachment(self, data: dict) -> "ResearchNoteBuilder":
        """data_processor.DataResult.to_dict() 결과를 추가."""
        self._data_attachments.append(data)
        return self

    def add_signature_block(self, 기록자: str, 점검자: Optional[str] = None) -> "ResearchNoteBuilder":
        self._signature = {"기록자": 기록자}
        if 점검자:
            self._signature["점검자"] = 점검자
        return self

    def set_header_footer(
        self, mode: int = 1,
        과제명: Optional[str] = None,
        기관명: Optional[str] = None,
    ) -> "ResearchNoteBuilder":
        self._hf_mode = mode
        if 과제명:
            self._hf_opts["과제명"] = 과제명
        if 기관명:
            self._hf_opts["기관명"] = 기관명
        return self

    # ── 저장 ──

    def save(self, path: str) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)

        if self._format == "hwpx":
            return self._build_hwpx(path)
        elif self._format == "markdown":
            return self._build_markdown(path)
        else:
            return self._build_json_spec(path)

    # ── HWPX 빌더 ──

    def _build_hwpx(self, path: str) -> str:
        sys.path.insert(0, _HWPX_SCRIPTS)
        from hwpx_builder import HwpxBuilder, CHAR_BODY, CHAR_GOTHIC, CHAR_TITLE, CHAR_BODY_11

        doc = HwpxBuilder()

        # 제목
        doc.add_heading("연 구 노 트", level=1)
        doc.add_empty_line()

        # 메타데이터 테이블
        meta_rows = self._build_meta_rows()
        doc.add_table(meta_rows, header=False, header_char_pr=CHAR_GOTHIC, body_char_pr=CHAR_BODY)
        doc.add_empty_line()

        # 본문 섹션
        for i, (title, content) in enumerate(self._sections, 1):
            doc.add_paragraph(f"{i}. {title}", char_pr=CHAR_BODY_11)
            doc.add_empty_line()
            for para in self._split_paragraphs(content):
                doc.add_paragraph(para)
            doc.add_empty_line()

        # 첨부 데이터
        if self._data_attachments:
            section_num = len(self._sections) + 1
            doc.add_paragraph(f"{section_num}. 첨부 데이터", char_pr=CHAR_BODY_11)
            doc.add_empty_line()
            for att in self._data_attachments:
                self._render_attachment_hwpx(doc, att)
            doc.add_empty_line()

        # 서명란
        if self._signature:
            doc.add_empty_line()
            날짜 = self._metadata.get("작성일자", "____-__-__")
            sig_rows = [
                ["구분", "서명", "일자"],
                [f"기록자 ({self._signature['기록자']})", "_________", 날짜],
            ]
            if self._signature.get("점검자"):
                sig_rows.append(
                    [f"점검자 ({self._signature['점검자']})", "_________", "____-__-__"]
                )
            else:
                sig_rows.append(["점검자", "_________", "____-__-__"])
            doc.add_table(sig_rows, header=True)

        return doc.save(path)

    def _render_attachment_hwpx(self, doc, att: dict):
        """첨부 데이터를 HWPX 요소로 렌더링."""
        fmt = att.get("format", "summary")
        summary = att.get("summary", "")

        if summary:
            doc.add_paragraph(f"[{summary}]")

        if fmt == "table" and isinstance(att.get("data"), list):
            doc.add_table(att["data"], header=True)
        elif fmt == "code_block" and isinstance(att.get("data"), str):
            for line in att["data"].split("\n")[:50]:
                doc.add_paragraph(line)
        elif fmt == "image_ref" and isinstance(att.get("data"), dict):
            info = att["data"]
            doc.add_paragraph(f"[이미지: {info.get('path', '')}]")
            dim = ""
            if info.get("width") and info.get("height"):
                dim = f" ({info['width']}×{info['height']})"
            doc.add_paragraph(f"  파일: {info.get('ext', '?')}{dim}, {info.get('size_human', '')}")
        else:
            doc.add_paragraph(str(att.get("data", "")))

    # ── Markdown 빌더 ──

    def _build_markdown(self, path: str) -> str:
        lines = []

        # YAML 프론트매터
        lines.append("---")
        lines.append('title: "연구노트"')
        for k, v in self._metadata.items():
            lines.append(f'{k}: "{v}"')
        lines.append("---")
        lines.append("")

        # 제목
        lines.append("# 연 구 노 트")
        lines.append("")

        # 메타데이터 테이블
        meta_rows = self._build_meta_rows()
        lines.append("| 항목 | 내용 |")
        lines.append("|------|------|")
        for row in meta_rows:
            lines.append(f"| {row[0]} | {row[1]} |")
        lines.append("")

        # 본문 섹션
        for i, (title, content) in enumerate(self._sections, 1):
            lines.append(f"## {i}. {title}")
            lines.append("")
            lines.append(content)
            lines.append("")

        # 첨부 데이터
        if self._data_attachments:
            section_num = len(self._sections) + 1
            lines.append(f"## {section_num}. 첨부 데이터")
            lines.append("")
            for att in self._data_attachments:
                lines.extend(self._render_attachment_md(att))
            lines.append("")

        # 서명란
        if self._signature:
            lines.append("---")
            lines.append("")
            날짜 = self._metadata.get("작성일자", "____-__-__")
            lines.append("| 구분 | 서명 | 일자 |")
            lines.append("|------|------|------|")
            lines.append(f"| 기록자 ({self._signature['기록자']}) | _________ | {날짜} |")
            if self._signature.get("점검자"):
                lines.append(f"| 점검자 ({self._signature['점검자']}) | _________ | ____-__-__ |")
            else:
                lines.append("| 점검자 | _________ | ____-__-__ |")
            lines.append("")

        content = "\n".join(lines)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return os.path.abspath(path)

    def _render_attachment_md(self, att: dict) -> list[str]:
        lines = []
        fmt = att.get("format", "summary")
        summary = att.get("summary", "")

        if summary:
            lines.append(f"> {summary}")
            lines.append("")

        if fmt == "table" and isinstance(att.get("data"), list):
            data = att["data"]
            if data:
                header = data[0]
                lines.append("| " + " | ".join(str(c) for c in header) + " |")
                lines.append("|" + "|".join("------" for _ in header) + "|")
                for row in data[1:]:
                    # 열 수 맞추기
                    padded = list(row) + [""] * (len(header) - len(row))
                    lines.append("| " + " | ".join(str(c) for c in padded[:len(header)]) + " |")
                lines.append("")
        elif fmt == "code_block" and isinstance(att.get("data"), str):
            lines.append("```")
            lines.append(att["data"])
            lines.append("```")
            lines.append("")
        elif fmt == "image_ref" and isinstance(att.get("data"), dict):
            info = att["data"]
            lines.append(f"![이미지]({info.get('path', '')})")
            lines.append("")
        else:
            lines.append(str(att.get("data", "")))
            lines.append("")

        return lines

    # ── JSON 스펙 빌더 (DOCX/PDF용) ──

    def _build_json_spec(self, path: str) -> str:
        spec = {
            "type": "research_note",
            "format": self._format.replace("_spec", ""),
            "design": {
                "header_bg": COLOR_HEADER_BG,
                "table_header_bg": COLOR_TABLE_HEADER,
                "table_border": COLOR_TABLE_BORDER,
                "signature_bg": COLOR_SIGNATURE_BG,
                "font_name": self._font_name,
                "font_size": self._font_size,
                "title_font_size": TITLE_FONT_SIZE,
                "section_font_size": SECTION_FONT_SIZE,
            },
            "metadata": self._metadata,
            "header_footer": {
                "mode": self._hf_mode,
                **self._hf_opts,
            },
            "sections": [
                {"title": title, "content": content}
                for title, content in self._sections
            ],
            "data_attachments": self._data_attachments,
            "signature": self._signature,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(spec, f, ensure_ascii=False, indent=2)
        return os.path.abspath(path)

    # ── 유틸 ──

    def _build_meta_rows(self) -> list[list[str]]:
        """메타데이터를 2열 테이블 행으로 변환."""
        rows = []
        field_order = [
            ("연구제목", "연구 제목"),
            ("과제명", "과제명"),
            ("작성일자", "작성일자"),
            ("기록자", "기록자"),
            ("과제번호", "과제번호"),
            ("연구책임자", "연구책임자"),
            ("주관연구기관", "주관연구기관"),
        ]
        for key, label in field_order:
            if key in self._metadata:
                rows.append([label, self._metadata[key]])
        return rows

    def _split_paragraphs(self, text: str) -> list[str]:
        """텍스트를 문단 단위로 분할."""
        paras = []
        for line in text.split("\n"):
            stripped = line.strip()
            if stripped:
                paras.append(stripped)
        return paras if paras else [""]


# ── CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="연구노트 샘플 생성")
    parser.add_argument("--format", choices=["hwpx", "markdown", "docx_spec", "pdf_spec"],
                        default="markdown", help="출력 포맷")
    parser.add_argument("--title", default="AI 기반 연구 과제", help="과제명")
    parser.add_argument("--subject", default="성능 분석 실험", help="연구 제목")
    parser.add_argument("--author", default="연구원", help="기록자")
    parser.add_argument("-o", "--output", help="출력 경로")
    args = parser.parse_args()

    from datetime import date
    today = date.today().isoformat()

    if not args.output:
        ext = {"hwpx": ".hwpx", "markdown": ".md", "docx_spec": ".json", "pdf_spec": ".json"}
        args.output = f"./output/연구노트_{today}{ext[args.format]}"

    note = ResearchNoteBuilder(output_format=args.format)
    note.set_metadata(
        과제명=args.title,
        연구제목=args.subject,
        기록자=args.author,
        작성일자=today,
    )
    note.add_section("연구 목적 / 배경", "본 연구는 AI 모델의 성능을 평가하기 위한 체계적 실험을 수행하는 것을 목적으로 한다.")
    note.add_section("연구 내용 및 방법", "실험 환경을 구성하고 벤치마크 데이터셋을 활용하여 모델 성능을 측정하였다.")
    note.add_section("결과", "실험 결과 기존 대비 15% 향상된 성능을 확인하였다.")
    note.add_section("고찰 및 결론", "모델 최적화를 통해 성능 향상이 가능함을 확인하였으며, 향후 추가 실험이 필요하다.")
    note.add_signature_block(기록자=args.author)
    note.set_header_footer(mode=1, 과제명=args.title)

    saved = note.save(args.output)
    print(f"생성 완료: {saved}")
