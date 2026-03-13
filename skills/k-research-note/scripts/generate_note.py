#!/usr/bin/env python3
"""
연구노트 생성 CLI — JSON 설정 파일 기반 원스텝 생성

임시 Python 스크립트를 작성하지 않고, JSON 설정 파일 하나로
연구노트를 생성할 수 있는 엔트리 포인트.

Usage:
    # JSON 설정 파일로 생성
    python generate_note.py config.json

    # stdin으로 JSON 전달
    echo '{"format":"markdown",...}' | python generate_note.py --stdin

    # 파이프라인: 데이터 처리 + 문서 생성
    python generate_note.py config.json --data file1.csv file2.json

JSON 설정 형식:
{
  "format": "hwpx",              // hwpx | markdown | docx_spec | pdf_spec
  "output": "./연구노트.hwpx",          // 출력 경로 (생략 시 자동)
  "metadata": {
    "과제명": "AI 기반 연구",
    "연구제목": "성능 평가",
    "기록자": "김연구",
    "작성일자": "2026-03-13",
    "과제번호": null,             // 선택
    "연구책임자": null,           // 선택
    "주관연구기관": null           // 선택
  },
  "font": {
    "name": "맑은 고딕",          // 생략 시 기본값
    "size": 11                    // 생략 시 기본값
  },
  "sections": [
    {"title": "연구 목적 / 배경", "content": "본 연구는..."},
    {"title": "연구 내용 및 방법", "content": "..."},
    {"title": "결과", "content": "..."},
    {"title": "고찰 및 결론", "content": "..."}
  ],
  "signature": {
    "기록자": "김연구",
    "점검자": "박검토"            // 선택
  },
  "header_footer": {
    "mode": 1,                    // 1=both, 2=header, 3=footer, 4=none
    "과제명": "AI 기반 연구",
    "기관명": null                // 선택
  }
}
"""

import json
import os
import sys
from datetime import date

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)

from data_processor import DataProcessor
from research_note_builder import ResearchNoteBuilder


def generate_from_config(config: dict, data_files: list[str] = None) -> str:
    """JSON 설정 딕셔너리로 연구노트를 생성하고 저장 경로를 반환."""

    fmt = config.get("format", "hwpx")
    meta = config.get("metadata", {})
    font = config.get("font", {})
    sections = config.get("sections", [])
    sig = config.get("signature", {})
    hf = config.get("header_footer", {})

    # 출력 경로 결정
    output = config.get("output")
    if not output:
        today = meta.get("작성일자", date.today().isoformat())
        ext_map = {"hwpx": ".hwpx", "markdown": ".md", "docx": ".docx", "pdf": ".pdf", "docx_spec": ".json", "pdf_spec": ".json"}
        output = f"./연구노트_{today}{ext_map.get(fmt, '.hwpx')}"

    # 빌더 생성
    note = ResearchNoteBuilder(output_format=fmt)

    # 메타데이터
    note.set_metadata(
        과제명=meta.get("과제명", ""),
        기록자=meta.get("기록자", ""),
        작성일자=meta.get("작성일자", date.today().isoformat()),
        연구제목=meta.get("연구제목"),
        과제번호=meta.get("과제번호"),
        연구책임자=meta.get("연구책임자"),
        주관연구기관=meta.get("주관연구기관"),
    )

    # 폰트
    if font:
        note.set_font(
            font_name=font.get("name", "맑은 고딕"),
            font_size=font.get("size", 11),
        )

    # 섹션
    for sec in sections:
        title = sec.get("title", "")
        content = sec.get("content", "")
        if title and content:
            note.add_section(title, content)

    # 데이터 첨부
    if data_files:
        proc = DataProcessor()
        for fpath in data_files:
            fpath = fpath.strip()
            if fpath and os.path.isfile(fpath):
                result = proc.process(fpath)
                note.add_data_attachment(result.to_dict())
            else:
                print(f"[경고] 파일을 찾을 수 없습니다: {fpath}", file=sys.stderr)

    # 인라인 데이터 첨부 (config에 포함된 경우)
    for att in config.get("data_attachments", []):
        note.add_data_attachment(att)

    # 서명란
    if sig.get("기록자"):
        note.add_signature_block(
            기록자=sig["기록자"],
            점검자=sig.get("점검자"),
        )

    # 머리글/바닥글
    if hf:
        note.set_header_footer(
            mode=hf.get("mode", 1),
            과제명=hf.get("과제명"),
            기관명=hf.get("기관명"),
        )

    return note.save(output)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="연구노트 생성 CLI")
    parser.add_argument("config", nargs="?", help="JSON 설정 파일 경로")
    parser.add_argument("--stdin", action="store_true", help="stdin에서 JSON 읽기")
    parser.add_argument("--data", nargs="*", help="첨부할 데이터 파일 경로")
    args = parser.parse_args()

    # JSON 설정 읽기
    if args.stdin or (not args.config and not sys.stdin.isatty()):
        config = json.loads(sys.stdin.read())
    elif args.config:
        with open(args.config, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        parser.error("JSON 설정 파일 경로 또는 --stdin 필요")

    saved = generate_from_config(config, args.data or [])
    print(f"생성 완료: {saved}")


if __name__ == "__main__":
    main()
