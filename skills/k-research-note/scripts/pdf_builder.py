#!/usr/bin/env python3
"""
연구노트 PDF 빌더 — fpdf2를 사용한 직접 PDF 생성

fpdf2가 없으면 자동 설치한다. 시스템에서 한국어 폰트를 자동 탐색한다.

Usage:
    from pdf_builder import PdfNoteBuilder

    doc = PdfNoteBuilder(font_name="맑은 고딕", font_size=11)
    doc.set_doc_header(과제명="AI 기반 연구")
    doc.set_doc_footer(과제명="AI 기반 연구", 기관명="KAIST")
    doc.add_header_block("연 구 노 트", "AI 기반 연구")
    doc.add_metadata_table([["연구 제목", "성능 평가"], ["기록자", "홍길동"]])
    doc.add_section(1, "연구 목적 / 배경", "본 연구는...")
    doc.add_signature_block("홍길동", "박검토", "2026-03-16")
    doc.save("./연구노트.pdf")
"""

import os
import subprocess
import sys

# ── fpdf2 자동 설치 ───────────────────────────────────────────

try:
    from fpdf import FPDF
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-q", "fpdf2"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    from fpdf import FPDF

# ── 색상 (RGB 튜플) ──────────────────────────────────────────

_HEADER_BG = (0x1B, 0x3A, 0x5C)
_TABLE_HEADER_BG = (0x2E, 0x5A, 0x88)
_TABLE_BORDER = (0xB0, 0xC4, 0xDE)
_SIGNATURE_BG = (0xF5, 0xF8, 0xFC)
_META_LABEL_BG = (0xF0, 0xF4, 0xF8)
_WHITE = (0xFF, 0xFF, 0xFF)
_SUBHEADER = (0xB0, 0xC4, 0xDE)
_FOOTER_TEXT = (0x66, 0x66, 0x66)
_BLACK = (0, 0, 0)


# ── 한국어 폰트 탐색 ─────────────────────────────────────────

def _find_korean_font():
    """시스템에서 한국어 TTF 폰트를 찾는다. (regular, bold) 경로 반환."""
    candidates = [
        # macOS
        ("/System/Library/Fonts/Supplemental/AppleGothic.ttf", None),
        ("/Library/Fonts/NanumGothic.ttf", "/Library/Fonts/NanumGothicBold.ttf"),
        ("/Library/Fonts/NanumBarunGothic.ttf", "/Library/Fonts/NanumBarunGothicBold.ttf"),
        # Linux
        ("/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
         "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
        # Windows
        ("C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/malgunbd.ttf"),
        ("C:/Windows/Fonts/NanumGothic.ttf", "C:/Windows/Fonts/NanumGothicBold.ttf"),
    ]
    for regular, bold in candidates:
        if os.path.isfile(regular):
            return regular, bold if bold and os.path.isfile(bold) else None
    return None, None


# ── FPDF 서브클래스 (머리글/바닥글) ──────────────────────────

class _NotePDF(FPDF):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._hdr_text = ""
        self._ftr_parts = []
        self._kr_font = "Helvetica"

    def header(self):
        if not self._hdr_text:
            return
        self.set_font(self._kr_font, "", 8)
        self.set_text_color(*_FOOTER_TEXT)
        self.cell(0, 5, self._hdr_text, align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*_BLACK)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font(self._kr_font, "", 8)
        self.set_text_color(*_FOOTER_TEXT)
        parts = self._ftr_parts + [str(self.page_no())]
        self.cell(0, 10, "  |  ".join(parts), align="C")
        self.set_text_color(*_BLACK)


# ── PdfNoteBuilder ────────────────────────────────────────────

class PdfNoteBuilder:
    """연구노트 PDF 빌더."""

    def __init__(self, font_name: str = "맑은 고딕", font_size: int = 11):
        self.font_name = font_name
        self.font_size = font_size
        self.pdf = _NotePDF()
        self.pdf.set_auto_page_break(auto=True, margin=25)
        self.pdf.set_margins(25.4, 25.4, 25.4)
        self._setup_fonts()
        self._page_added = False

    def _setup_fonts(self):
        regular, bold = _find_korean_font()
        if regular:
            self.pdf.add_font("Korean", "", regular)
            self.pdf.add_font("Korean", "B", bold or regular)
            self._font = "Korean"
        else:
            self._font = "Helvetica"
        self.pdf._kr_font = self._font

    def _ensure_page(self):
        if not self._page_added:
            self.pdf.add_page()
            self._page_added = True

    def _set_font(self, style: str = "", size: int = None):
        self.pdf.set_font(self._font, style, size or self.font_size)

    # ── 머리글/바닥글 (콘텐츠 추가 전에 호출) ──

    def set_doc_header(self, 과제명: str = "", 기관명: str = ""):
        text = "연 구 노 트"
        if 과제명:
            text += f"  |  {과제명}"
        self.pdf._hdr_text = text

    def set_doc_footer(self, 과제명: str = "", 기관명: str = ""):
        parts = []
        if 기관명:
            parts.append(기관명)
        if 과제명:
            parts.append(과제명)
        self.pdf._ftr_parts = parts

    # ── 콘텐츠 ──

    def add_header_block(self, title: str, subtitle: str):
        """문서 상단 타이틀 영역 (짙은 남색 배경)."""
        self._ensure_page()
        w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        x, y = self.pdf.get_x(), self.pdf.get_y()
        block_h = 25

        self.pdf.set_fill_color(*_HEADER_BG)
        self.pdf.rect(x, y, w, block_h, "F")

        self._set_font("B", 16)
        self.pdf.set_text_color(*_WHITE)
        self.pdf.set_xy(x, y + 3)
        self.pdf.cell(w, 10, title, align="C", new_x="LMARGIN", new_y="NEXT")

        self._set_font("", 11)
        self.pdf.set_text_color(*_SUBHEADER)
        self.pdf.cell(w, 8, subtitle, align="C", new_x="LMARGIN", new_y="NEXT")

        self.pdf.set_text_color(*_BLACK)
        self.pdf.set_y(y + block_h + 5)

    def add_metadata_table(self, rows: list[list[str]]):
        """2열 메타데이터 테이블 (라벨 | 값)."""
        self._ensure_page()
        w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        lw, vw = w * 0.25, w * 0.75
        rh = 8

        self.pdf.set_draw_color(*_TABLE_BORDER)
        for label, value in rows:
            self.pdf.set_fill_color(*_META_LABEL_BG)
            self._set_font("B")
            self.pdf.cell(lw, rh, f" {label}", border=1, fill=True)

            self.pdf.set_fill_color(*_WHITE)
            self._set_font("")
            self.pdf.cell(vw, rh, f" {value}", border=1, new_x="LMARGIN", new_y="NEXT")

        self.pdf.ln(5)

    def add_section(self, number: int, title: str, content: str):
        """번호 매긴 섹션 (제목 + 본문)."""
        self._ensure_page()
        self._set_font("B", 12)
        self.pdf.cell(0, 8, f"{number}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(2)

        self._set_font("")
        for para in content.split("\n"):
            para = para.strip()
            if para:
                self.pdf.multi_cell(0, 6, para, new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(5)

    def add_data_table(self, data: list[list], summary: str = ""):
        """데이터 테이블 첨부."""
        self._ensure_page()
        if summary:
            self._set_font("")
            self.pdf.set_text_color(*_FOOTER_TEXT)
            self.pdf.cell(0, 7, f"[{summary}]", new_x="LMARGIN", new_y="NEXT")
            self.pdf.set_text_color(*_BLACK)

        if not data or not data[0]:
            return

        w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        col_cnt = len(data[0])
        cw = w / col_cnt

        self.pdf.set_draw_color(*_TABLE_BORDER)
        for i, row in enumerate(data):
            is_hdr = i == 0
            self.pdf.set_fill_color(*(_TABLE_HEADER_BG if is_hdr else _WHITE))
            self.pdf.set_text_color(*(_WHITE if is_hdr else _BLACK))
            self._set_font("B" if is_hdr else "", 9)
            for j, val in enumerate(row):
                if j >= col_cnt:
                    break
                self.pdf.cell(cw, 7, str(val), border=1, fill=is_hdr)
            self.pdf.ln()

        self.pdf.set_text_color(*_BLACK)
        self.pdf.ln(5)

    def add_code_block(self, code: str, summary: str = ""):
        """코드 블록 첨부."""
        self._ensure_page()
        if summary:
            self._set_font("")
            self.pdf.set_text_color(*_FOOTER_TEXT)
            self.pdf.cell(0, 7, f"[{summary}]", new_x="LMARGIN", new_y="NEXT")
            self.pdf.set_text_color(*_BLACK)

        self.pdf.set_font("Courier", "", 9)
        self.pdf.set_fill_color(0xF5, 0xF5, 0xF5)
        for line in code.split("\n")[:50]:
            self.pdf.cell(0, 5, line, fill=True, new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(5)

    def add_image_ref(self, info: dict):
        """이미지 참조 텍스트 추가."""
        self._ensure_page()
        self._set_font("")
        self.pdf.cell(0, 7, f"[이미지: {info.get('path', '')}]", new_x="LMARGIN", new_y="NEXT")
        dim = ""
        if info.get("width") and info.get("height"):
            dim = f" ({info['width']}×{info['height']})"
        self._set_font("", self.font_size - 1)
        self.pdf.cell(
            0, 7,
            f"  파일: {info.get('ext', '?')}{dim}, {info.get('size_human', '')}",
            new_x="LMARGIN", new_y="NEXT",
        )

    def add_signature_block(self, 기록자: str, 점검자: str = "", 날짜: str = "____-__-__"):
        """서명란 테이블."""
        self._ensure_page()
        self.pdf.ln(5)

        w = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
        cws = [w * 0.4, w * 0.3, w * 0.3]

        rows_data = [
            ["구분", "서명", "일자"],
            [f"기록자 ({기록자})", "_________", 날짜],
        ]
        if 점검자:
            rows_data.append([f"점검자 ({점검자})", "_________", "____-__-__"])
        else:
            rows_data.append(["점검자", "_________", "____-__-__"])

        self.pdf.set_draw_color(*_TABLE_BORDER)
        for i, row in enumerate(rows_data):
            is_hdr = i == 0
            self.pdf.set_fill_color(*(_TABLE_HEADER_BG if is_hdr else _SIGNATURE_BG))
            self.pdf.set_text_color(*(_WHITE if is_hdr else _BLACK))
            self._set_font("B" if is_hdr else "")
            for j, val in enumerate(row):
                self.pdf.cell(cws[j], 8, f" {val}", border=1, fill=True)
            self.pdf.ln()

        self.pdf.set_text_color(*_BLACK)

    # ── 저장 ──

    def save(self, path: str) -> str:
        """PDF 파일 저장. 절대 경로를 반환."""
        self._ensure_page()
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        self.pdf.output(path)
        return os.path.abspath(path)
