# Skills

A collection of agent skills loaded on demand by AI coding tools (Claude Code, skills.sh).
Each skill is a self-contained folder under `skills/` with a `SKILL.md` that holds the
metadata and instructions an agent reads at invocation time.

Background:
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Creating custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Agent Skills Specification](https://agentskills.io/specification)

## Available Skills

| Skill | Description |
|-------|-------------|
| [commit-message](./skills/commit-message/) | Generate well-structured commit messages from the current git state. Also produces IDE-specific commit-message prompts (IntelliJ, VS Code, Xcode, …) using each editor's native template variables. |
| [css-design-system](./skills/css-design-system/) | Generate a CSS design-token styleguide — palette, typography, spacing, radius, light/dark theme, per-component CSS, and an HTML preview. Ships ready-to-copy systems: Minimal, Material 3, IBM Carbon, Fluent 2, Maximal. |
| [hwpx](./skills/hwpx/) | HWPX(한글/한컴오피스) 문서 생성·읽기·편집. 한국 정부/공공기관 제출용 한글 문서 처리. |
| [k-research-note](./skills/k-research-note/) | 대한민국 정부 R&D 과제 연구노트 작성. 국가연구개발혁신법 및 연구노트 지침에 부합하는 연구노트를 DOCX, HWPX, PDF, Markdown으로 생성. |
| [kotlin-springboot-hexagonal](./skills/kotlin-springboot-hexagonal/) | Kotlin + Spring Boot 헥사고날(ports & adapters) 모듈러 모놀리스 아키텍처 가이드. |

## Installation

### Claude Code (Plugin)

Register this repo as a plugin marketplace:

```
/plugin marketplace add ujon/skills
```

Then install via `/plugin` → *Browse and install plugins*, or directly:

```
/plugin install kotlin-springboot-hexagonal@ujon
/plugin install k-research-note@ujon            # bundles the hwpx skill
/plugin install hwpx@ujon
```

> `commit-message`와 `css-design-system`은 아직 Claude Code 플러그인으로 등록되어 있지 않습니다 — 아래 skills.sh CLI로 설치하세요.

### skills.sh (CLI)

```bash
npx skills add ujon/skills --skill commit-message
npx skills add ujon/skills --skill css-design-system
npx skills add ujon/skills --skill hwpx
npx skills add ujon/skills --skill k-research-note
npx skills add ujon/skills --skill kotlin-springboot-hexagonal
```

### k-research-note dependencies

DOCX/PDF 출력은 [`anthropics/skills`](https://github.com/anthropics/skills)의 `docx`·`pdf` 스킬이 필요합니다.

```
# Claude Code
/plugin marketplace add anthropics/skills
/plugin install document-skills@anthropic-agent-skills
```

```bash
# skills.sh CLI
npx skills add anthropics/skills --skill docx
npx skills add anthropics/skills --skill pdf
```
