#!/usr/bin/env python3
"""
HWPX 문서 빌더 — 검증된 OWPML 템플릿 기반

templates/ 디렉토리의 실제 한컴오피스 호환 XML 템플릿을 기반으로
본문 콘텐츠를 삽입하여 유효한 HWPX 파일을 생성한다.

Usage:
    from hwpx_builder import HwpxBuilder

    doc = HwpxBuilder()
    doc.add_heading("문서 제목", level=1)
    doc.add_paragraph("본문 텍스트입니다.")
    doc.add_table([["열1", "열2"], ["값1", "값2"]], header=True)
    doc.save("./document.hwpx")
"""

import os
import zipfile
import io
import re
from xml.sax.saxutils import escape as _esc
from typing import Optional
from dataclasses import dataclass

# ── 경로 ─────────────────────────────────────────────────────

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_TEMPLATE_DIR = os.path.join(_SCRIPT_DIR, "templates")

# ── OWPML 상수 ──────────────────────────────────────────────

A4_WIDTH = 59528
A4_HEIGHT = 84188
HU_PER_CM = 2835

# 기본 charPr id 매핑 (header.xml 템플릿 기준)
#   id=0: 바탕글 (함초롬바탕 10pt)
#   id=1: 함초롬돋움 10pt
#   id=5: 함초롬돋움 16pt, 파란색 (#2E74B5) — 제목용
#   id=6: 함초롬돋움 11pt
CHAR_BODY = 0       # 본문
CHAR_GOTHIC = 1     # 돋움체 본문
CHAR_TITLE = 5      # 16pt 파란 제목

# borderFill id 매핑
BORDER_NONE = 1          # 테두리 없음
BORDER_SOLID = 3         # 실선 테두리
BORDER_SOLID_FILL = 4    # 실선 테두리 + 회색 배경
CHAR_BODY_11 = 6    # 11pt 본문

# 기본 paraPr id 매핑
#   id=0: 바탕글 (양쪽정렬, 줄간격 160%)
PARA_BODY = 0

# ── 네임스페이스 ─────────────────────────────────────────────

_ALL_NS = (
    'xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app" '
    'xmlns:hp="http://www.hancom.co.kr/hwpml/2011/paragraph" '
    'xmlns:hp10="http://www.hancom.co.kr/hwpml/2016/paragraph" '
    'xmlns:hs="http://www.hancom.co.kr/hwpml/2011/section" '
    'xmlns:hc="http://www.hancom.co.kr/hwpml/2011/core" '
    'xmlns:hh="http://www.hancom.co.kr/hwpml/2011/head" '
    'xmlns:hhs="http://www.hancom.co.kr/hwpml/2011/history" '
    'xmlns:hm="http://www.hancom.co.kr/hwpml/2011/master-page" '
    'xmlns:hpf="http://www.hancom.co.kr/schema/2011/hpf" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/" '
    'xmlns:opf="http://www.idpf.org/2007/opf/" '
    'xmlns:ooxmlchart="http://www.hancom.co.kr/hwpml/2016/ooxmlchart" '
    'xmlns:hwpunitchar="http://www.hancom.co.kr/hwpml/2016/HwpUnitChar" '
    'xmlns:epub="http://www.idpf.org/2007/ops" '
    'xmlns:config="urn:oasis:names:tc:opendocument:xmlns:config:1.0"'
)


# ── HwpxBuilder ──────────────────────────────────────────────

class HwpxBuilder:
    """HWPX 문서 빌더. 검증된 OWPML 템플릿 기반."""

    def __init__(self):
        self._body_parts: list[str] = []
        self._p_id_counter = 1000000000  # 문단 고유 ID

    def _next_p_id(self) -> str:
        self._p_id_counter += 1
        return str(self._p_id_counter)

    # ── 본문 요소 추가 ──

    def add_paragraph(
        self, text: str, char_pr: int = CHAR_BODY, para_pr: int = PARA_BODY
    ) -> "HwpxBuilder":
        """문단 추가."""
        self._body_parts.append(_make_paragraph(text, char_pr, para_pr, self._next_p_id()))
        return self

    def add_heading(self, text: str, level: int = 1) -> "HwpxBuilder":
        """제목 추가 (level 1~3). level 1은 16pt 파란색, 2~3은 11pt."""
        if level == 1:
            cs, ps = CHAR_TITLE, PARA_BODY
        else:
            cs, ps = CHAR_BODY_11, PARA_BODY
        self._body_parts.append(_make_paragraph(text, cs, ps, self._next_p_id()))
        return self

    def add_empty_line(self) -> "HwpxBuilder":
        """빈 줄."""
        pid = self._next_p_id()
        self._body_parts.append(
            f'<hp:p id="{pid}" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="0"><hp:t/></hp:run></hp:p>'
        )
        return self

    def add_table(
        self, rows: list[list[str]], header: bool = True,
        header_char_pr: int = CHAR_GOTHIC, body_char_pr: int = CHAR_BODY,
    ) -> "HwpxBuilder":
        """테이블 추가."""
        if not rows:
            return self
        col_cnt = max(len(r) for r in rows)
        row_cnt = len(rows)

        lines = []
        pid = self._next_p_id()
        # 열 너비 균등 분배 (A4 본문 영역 기준)
        content_width = A4_WIDTH - 8504 * 2  # 좌우 여백 제외
        col_width = content_width // col_cnt
        row_height = 850  # 기본 행 높이

        lines.append(f'<hp:p id="{pid}" paraPrIDRef="0" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">')
        lines.append(f'<hp:run charPrIDRef="0">')
        lines.append(f'<hp:tbl id="" zOrder="0" numberingType="TABLE" textWrap="TOP_AND_BOTTOM" '
                     f'textFlow="BOTH_SIDES" lock="0" dropcapstyle="None" pageBreak="CELL" '
                     f'repeatHeader="1" rowCnt="{row_cnt}" colCnt="{col_cnt}" cellSpacing="0" '
                     f'borderFillIDRef="{BORDER_SOLID}" noAdjust="0">')

        # gridCol: 열 너비 정의 (필수)
        for _ in range(col_cnt):
            lines.append(f'<hp:gridCol width="{col_width}"/>')

        for i, row in enumerate(rows):
            is_hdr = header and i == 0
            cs = header_char_pr if is_hdr else body_char_pr
            cell_border = BORDER_SOLID_FILL if is_hdr else BORDER_SOLID
            lines.append('<hp:tr>')
            for j, cell in enumerate(row):
                cell_pid = self._next_p_id()
                lines.append(f'<hp:tc name="" header="{1 if is_hdr else 0}" hasMargin="0" protect="0" '
                             f'editable="0" dirty="0" borderFillIDRef="{cell_border}">')
                lines.append(f'<hp:subList id="" textDirection="HORIZONTAL" lineWrap="BREAK" '
                             f'vertAlign="CENTER" linkListIDRef="0" linkListNextIDRef="0" '
                             f'textWidth="0" textHeight="0" hasTextRef="0" hasNumRef="0">')
                lines.append(_make_paragraph(cell, cs, 0, cell_pid))
                lines.append('</hp:subList>')
                lines.append(f'<hp:cellAddr colAddr="{j}" rowAddr="{i}"/>')
                lines.append(f'<hp:cellSpan colSpan="1" rowSpan="1"/>')
                lines.append(f'<hp:cellSz width="{col_width}" height="{row_height}"/>')
                lines.append(f'<hp:cellMargin left="510" right="510" top="141" bottom="141"/>')
                lines.append('</hp:tc>')
            lines.append('</hp:tr>')

        lines.append('</hp:tbl>')
        lines.append('</hp:run>')
        lines.append('</hp:p>')
        self._body_parts.append("\n".join(lines))
        return self

    def add_multi_run(
        self, runs: list[tuple[str, int]], para_pr: int = PARA_BODY
    ) -> "HwpxBuilder":
        """한 문단에 여러 스타일 런 추가. runs: [(text, char_pr_id), ...]"""
        pid = self._next_p_id()
        run_xml = "".join(
            f'<hp:run charPrIDRef="{cs}"><hp:t>{_esc(t)}</hp:t></hp:run>'
            for t, cs in runs
        )
        self._body_parts.append(
            f'<hp:p id="{pid}" paraPrIDRef="{para_pr}" styleIDRef="0" '
            f'pageBreak="0" columnBreak="0" merged="0">{run_xml}</hp:p>'
        )
        return self

    def add_raw_xml(self, xml: str) -> "HwpxBuilder":
        """section0.xml에 직접 XML 삽입."""
        self._body_parts.append(xml)
        return self

    # ── 빌드 & 저장 ──

    def _build_section_xml(self) -> str:
        """section0.xml 생성: 템플릿의 첫 번째 문단(secPr 포함) + 사용자 본문."""
        template = _read_template("Contents/section0.xml")

        # 템플릿에서 첫 번째 <hp:p ...>...</hp:p> (secPr 포함) 추출
        # 이 문단은 페이지 설정을 포함하므로 반드시 첫 번째여야 함
        match = re.search(
            r'(<hp:p\s+id="[^"]*"[^>]*>.*?</hp:p>)',
            template,
            re.DOTALL,
        )
        if not match:
            raise RuntimeError("section0.xml 템플릿에서 첫 번째 문단을 찾을 수 없습니다")

        first_para = match.group(1)
        body = "\n".join(self._body_parts)

        return (
            f'<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n'
            f'<hs:sec {_ALL_NS}>\n'
            f'{first_para}\n'
            f'{body}\n'
            f'</hs:sec>'
        )

    def save(self, path: str) -> str:
        """HWPX 파일로 저장. 디렉토리가 없으면 자동 생성. 저장된 절대 경로를 반환."""
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

        # Preview 텍스트 생성 (본문 텍스트 추출)
        preview_text = _extract_preview(self._body_parts)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            # mimetype — 비압축, 첫 번째 (OWPML 필수)
            zf.writestr(
                zipfile.ZipInfo("mimetype"),
                _read_template("mimetype"),
                compress_type=zipfile.ZIP_STORED,
            )
            # 보일러플레이트 (템플릿 그대로)
            for name in [
                "version.xml",
                "settings.xml",
                "META-INF/container.xml",
                "META-INF/manifest.xml",
                "META-INF/container.rdf",
                "Contents/content.hpf",
                "Contents/header.xml",
            ]:
                zf.writestr(name, _read_template(name))

            # 본문
            zf.writestr("Contents/section0.xml", self._build_section_xml())

            # 미리보기
            zf.writestr("Preview/PrvText.txt", preview_text)

        with open(path, "wb") as f:
            f.write(buf.getvalue())

        return os.path.abspath(path)


# ── 유틸 ─────────────────────────────────────────────────────

def _read_template(name: str) -> str:
    """템플릿 파일 읽기."""
    path = os.path.join(_TEMPLATE_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _make_paragraph(text: str, char_pr: int, para_pr: int, p_id: str) -> str:
    """OWPML 문단 XML 생성."""
    if not text:
        return (
            f'<hp:p id="{p_id}" paraPrIDRef="{para_pr}" styleIDRef="0" '
            f'pageBreak="0" columnBreak="0" merged="0">'
            f'<hp:run charPrIDRef="{char_pr}"><hp:t/></hp:run></hp:p>'
        )
    return (
        f'<hp:p id="{p_id}" paraPrIDRef="{para_pr}" styleIDRef="0" '
        f'pageBreak="0" columnBreak="0" merged="0">'
        f'<hp:run charPrIDRef="{char_pr}"><hp:t>{_esc(text)}</hp:t></hp:run></hp:p>'
    )


def _extract_preview(body_parts: list[str]) -> str:
    """본문에서 텍스트만 추출하여 미리보기 생성."""
    texts = []
    for part in body_parts:
        for m in re.finditer(r'<hp:t>([^<]*)</hp:t>', part):
            if m.group(1):
                texts.append(m.group(1))
    return "\n".join(texts)


# ── CLI ──────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HWPX 샘플 문서 생성")
    parser.add_argument("-o", "--output", default="./sample.hwpx", help="출력 경로")
    args = parser.parse_args()

    doc = HwpxBuilder()
    doc.add_heading("샘플 문서 제목", level=1)
    doc.add_empty_line()
    doc.add_paragraph("이 문서는 hwpx_builder.py로 생성된 샘플입니다.")
    doc.add_empty_line()
    doc.add_heading("테이블 예시", level=2)
    doc.add_table([
        ["항목", "내용", "비고"],
        ["첫 번째", "테스트 데이터", "정상"],
        ["두 번째", "샘플 값", "-"],
    ])
    doc.add_empty_line()
    doc.add_paragraph("문서 끝.")

    saved = doc.save(args.output)
    print(f"생성 완료: {saved}")
