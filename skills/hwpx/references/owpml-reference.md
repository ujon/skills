# OWPML XML 레퍼런스

HWPX 문서의 XML 구조 상세 가이드.

## 네임스페이스

| 접두사 | URI | 용도 |
|--------|-----|------|
| `hs` | `http://www.hancom.co.kr/hwpml/2011/section` | 섹션 (본문) |
| `hp` | `http://www.hancom.co.kr/hwpml/2011/paragraph` | 문단, 테이블 |
| `hc` | `http://www.hancom.co.kr/hwpml/2011/core` | 코어 속성 |
| `hh` | `http://www.hancom.co.kr/hwpml/2011/head` | 헤더 (스타일 정의) |
| `hv` | `http://www.hancom.co.kr/hwpml/2011/version` | 버전 |
| `ha` | `http://www.hancom.co.kr/hwpml/2011/app` | 앱 설정 |
| `hpf` | `http://www.hancom.co.kr/hwpml/2011/packagefile` | 패키지 |
| `ofc` | `urn:oasis:names:tc:opendocument:xmlns:container` | ODF 컨테이너 |
| `odf` | `urn:oasis:names:tc:opendocument:xmlns:manifest:1.0` | ODF 매니페스트 |

## 보일러플레이트 파일들

### mimetype
```
application/hwpx
```
(개행 없음, ZIP 내 첫 번째, 비압축)

### version.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<hv:HWPVersion xmlns:hv="http://www.hancom.co.kr/hwpml/2011/version" 
  Major="1" Minor="2" Micro="0" BuildNumber="0"/>
```

### settings.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ha:HWPApplicationSetting xmlns:ha="http://www.hancom.co.kr/hwpml/2011/app"/>
```

### META-INF/container.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<ofc:container xmlns:ofc="urn:oasis:names:tc:opendocument:xmlns:container">
  <ofc:rootfiles>
    <ofc:rootfile full-path="Contents/content.hpf" media-type="application/hwpx+xml"/>
  </ofc:rootfiles>
</ofc:container>
```

### META-INF/manifest.xml
```xml
<?xml version="1.0" encoding="UTF-8"?>
<odf:manifest xmlns:odf="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
  <odf:file-entry odf:full-path="Contents/section0.xml" odf:media-type="application/xml"/>
</odf:manifest>
```

### Contents/content.hpf
```xml
<?xml version="1.0" encoding="UTF-8"?>
<hpf:package xmlns:hpf="http://www.hancom.co.kr/hwpml/2011/packagefile">
  <hpf:compItem id="header" href="Contents/header.xml"/>
  <hpf:compItem id="sec0" href="Contents/section0.xml"/>
</hpf:package>
```

## header.xml 상세

### 글꼴 정의
```xml
<hh:faceNameMap>
  <hh:fontface lang="HANGUL">
    <hh:font face="함초롬돋움" type="TTF"/>
    <hh:font face="맑은 고딕" type="TTF"/>
  </hh:fontface>
  <hh:fontface lang="LATIN">
    <hh:font face="함초롬돋움" type="TTF"/>
    <hh:font face="맑은 고딕" type="TTF"/>
  </hh:fontface>
  <hh:fontface lang="HANJA">
    <hh:font face="함초롬돋움" type="TTF"/>
  </hh:fontface>
</hh:faceNameMap>
```

글꼴 참조 시 `fontRef`의 `hangul`, `latin` 등은 해당 `fontface` 내 `font` 요소의 0-based 인덱스이다.

### 글자 속성 (charPr)

```xml
<hh:charPrMap>
  <!-- 기본 본문 -->
  <hh:charPr id="0">
    <hc:fontRef hangul="0" latin="0"/>
    <hc:charSz val="2200"/>  <!-- 약 11pt -->
  </hh:charPr>
  
  <!-- 볼드 제목 -->
  <hh:charPr id="1">
    <hc:fontRef hangul="1" latin="1"/>
    <hc:charSz val="3600"/>  <!-- 약 18pt -->
    <hc:bold/>
  </hh:charPr>
  
  <!-- 컬러 텍스트 -->
  <hh:charPr id="2">
    <hc:fontRef hangul="0" latin="0"/>
    <hc:charSz val="2200"/>
    <hc:color val="0000FF"/>
  </hh:charPr>
  
  <!-- 이탤릭 -->
  <hh:charPr id="3">
    <hc:fontRef hangul="0" latin="0"/>
    <hc:charSz val="2200"/>
    <hc:italic/>
  </hh:charPr>
  
  <!-- 밑줄 -->
  <hh:charPr id="4">
    <hc:fontRef hangul="0" latin="0"/>
    <hc:charSz val="2200"/>
    <hc:underline type="BOTTOM"/>
  </hh:charPr>
</hh:charPrMap>
```

### 문단 속성 (paraPr)

```xml
<hh:paraPrMap>
  <!-- 기본 문단 -->
  <hh:paraPr id="0">
    <hc:lnSpc type="PERCENT" val="160"/>
    <hc:spacing before="0" after="100"/>
  </hh:paraPr>
  
  <!-- 가운데 정렬 -->
  <hh:paraPr id="1">
    <hc:align horizontal="CENTER"/>
    <hc:lnSpc type="PERCENT" val="160"/>
    <hc:spacing before="200" after="200"/>
  </hh:paraPr>
  
  <!-- 들여쓰기 -->
  <hh:paraPr id="2">
    <hc:lnSpc type="PERCENT" val="160"/>
    <hc:margin left="800" right="0"/>
    <hc:indent val="400"/>
    <hc:spacing before="0" after="100"/>
  </hh:paraPr>
  
  <!-- 오른쪽 정렬 -->
  <hh:paraPr id="3">
    <hc:align horizontal="RIGHT"/>
    <hc:lnSpc type="PERCENT" val="160"/>
  </hh:paraPr>
</hh:paraPrMap>
```

정렬 옵션: `LEFT`, `CENTER`, `RIGHT`, `JUSTIFY`
줄간격 type: `PERCENT` (160 = 160%), `FIXED` (HU 단위)

### 페이지 설정 (secPr)

```xml
<hh:secPr>
  <!-- A4 용지 -->
  <hc:pgSz width="59528" height="84188"/>
  
  <!-- 여백 (HU 단위, 1cm = 2835 HU) -->
  <hc:pgMar left="8504" right="8504" top="5668" bottom="4252" 
            header="4252" footer="4252"/>
</hh:secPr>
```

용지 크기 참조:
- A4: 59528 × 84188
- Letter: 61200 × 79200
- B5: 51024 × 72852
- Legal: 61200 × 100800

## section0.xml 요소

### 문단 (paragraph)

```xml
<hp:p id="[순번]" paraPrIDRef="[paraPr id]" styleIDRef="0">
  <hp:run charPrIDRef="[charPr id]">
    <hp:t>텍스트 내용</hp:t>
  </hp:run>
</hp:p>
```

### 테이블

```xml
<hp:p id="0" paraPrIDRef="0" styleIDRef="0">
  <hp:tbl rowCnt="[행수]" colCnt="[열수]">
    <hp:tr>
      <hp:tc rowSpan="1" colSpan="1">
        <hp:p id="0" paraPrIDRef="0" styleIDRef="0">
          <hp:run charPrIDRef="0"><hp:t>셀 내용</hp:t></hp:run>
        </hp:p>
      </hp:tc>
      <!-- 나머지 셀들 -->
    </hp:tr>
    <!-- 나머지 행들 -->
  </hp:tbl>
</hp:p>
```

셀 병합:
- `rowSpan="2"`: 2행 세로 병합
- `colSpan="3"`: 3열 가로 병합

### 빈 줄
```xml
<hp:p id="0" paraPrIDRef="0" styleIDRef="0"/>
```

## Python 스크립트

XML 생성과 ZIP 패키징은 `skills/hwpx/scripts/` 에 미리 작성된 스크립트를 사용한다:

- **`hwpx_builder.py`** — `HwpxBuilder` 클래스: 문단, 제목, 테이블, 커스텀 스타일, ZIP 패키징 모두 처리
- **`hwpx_reader.py`** — `HwpxReader`, `unpack()`, `repack()`: 읽기, 텍스트 추출, 편집

```python
import sys; sys.path.insert(0, "skills/hwpx/scripts")
from hwpx_builder import HwpxBuilder

doc = HwpxBuilder()
doc.add_heading("제목", level=1)
doc.add_paragraph("본문 텍스트")
doc.add_table([["열1", "열2"], ["값1", "값2"]], header=True)
doc.save("./문서.hwpx")
```

직접 XML을 조작해야 할 경우 위의 XML 요소 레퍼런스를 참고하여 `add_raw_xml()`로 삽입한다.

## 트러블슈팅

### 한컴오피스에서 열리지 않음
- mimetype이 첫 번째 파일이며 비압축인지 확인
- 네임스페이스 URI가 정확한지 확인
- header.xml 내 charPrMap에서 참조하는 fontRef 인덱스가 faceNameMap에 존재하는지 확인

### 글자가 깨짐
- 글꼴명이 시스템에 설치된 글꼴과 일치하는지 확인
- 추천 글꼴: 맑은 고딕 (Windows), 함초롬돋움 (한컴 내장)

### 편집 후 레이아웃 깨짐
- `linesegarray` 제거했는지 확인
- 한컴오피스에서 다시 열면 자동으로 재계산됨
