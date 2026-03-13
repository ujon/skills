# Skills

Skills are folders of instructions, scripts, and resources that AI coding agents load dynamically to improve performance on specialized tasks. Skills teach agents how to complete specific tasks in a repeatable way, whether that's following architecture conventions, scaffolding new features, or reviewing code for compliance.

For more information, check out:
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Agent Skills Specification](https://agentskills.io/specification)

# About This Repository

This repository contains reusable skills for AI coding agents. Each skill is self-contained in its own folder with a `SKILL.md` file containing the instructions and metadata that agents use.

## Available Skills

| Skill | Description |
|-------|-------------|
| [commit-message](./skills/commit-message/) | Generate well-structured commit messages by analyzing the current git state. Also generates IDE-specific commit message prompts (IntelliJ, VS Code, Xcode, etc.) with their native template variables. |
| [kotlin-springboot-hexagonal](./skills/kotlin-springboot-hexagonal/) | Architecture guide for Kotlin + Spring Boot projects using hexagonal (ports & adapters) pattern with modular monolith structure. |
| [k-research-note](./skills/k-research-note/) | 대한민국 정부 R&D 과제 연구노트 작성. 국가연구개발혁신법 및 연구노트 지침에 부합하는 연구노트를 DOCX, HWPX(한글), PDF, Markdown으로 생성. |
| [hwpx](./skills/hwpx/) | HWPX(한글/한컴오피스) 문서 생성, 읽기, 편집. 한국 정부/공공기관 제출용 한글 문서 처리. |

# Installation

## Claude Code

Register this repository as a Claude Code Plugin marketplace:

```
/plugin marketplace add ujon/skills
```

Then install the plugin:

1. Select `Browse and install plugins`
2. Select the skill you want
3. Select `Install now`

Or directly install via:

```
/plugin install commit-message@ujon
/plugin install kotlin-springboot-hexagonal@ujon
/plugin install k-research-note@ujon
/plugin install hwpx@ujon
```

> **Note:** `k-research-note` 플러그인의 DOCX/PDF 출력은 [docx](https://skills.sh/anthropics/skills/docx), [pdf](https://skills.sh/anthropics/skills/pdf) 스킬에 의존합니다. 아래 명령으로 함께 설치하세요:
> ```
> /plugin marketplace add anthropics/skills
> /plugin install document-skills@anthropic-agent-skills
> ```

## skills.sh (CLI)

```bash
npx skills add ujon/skills --skill commit-message
npx skills add ujon/skills --skill kotlin-springboot-hexagonal
npx skills add ujon/skills --skill k-research-note
npx skills add ujon/skills --skill hwpx
# k-research-note requires docx and pdf skills from anthropics/skills
npx skills add anthropics/skills --skill docx
npx skills add anthropics/skills --skill pdf
```
