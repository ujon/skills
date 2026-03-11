# Skills

Skills are folders of instructions, scripts, and resources that AI coding agents load dynamically to improve performance on specialized tasks. Skills teach agents how to complete specific tasks in a repeatable way, whether that's following architecture conventions, scaffolding new features, or reviewing code for compliance.

For more information, check out:
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Agent Skills Specification](https://agentskills.io/specification)

# About This Repository

This repository contains skills for Kotlin + Spring Boot backend development. Each skill is self-contained in its own folder with a `SKILL.md` file containing the instructions and metadata that agents use.

## Available Skills

| Skill | Description |
|-------|-------------|
| [kotlin-springboot-hexagonal](./skills/kotlin-springboot-hexagonal/) | Architecture guide for Kotlin + Spring Boot projects using hexagonal (ports & adapters) pattern with modular monolith structure. Use when creating features, modules, use cases, entities, controllers, or repositories. |

# Installation

## Claude Code

Register this repository as a Claude Code Plugin marketplace:

```
/plugin marketplace add ujon/skills
```

Then install the plugin:

1. Select `Browse and install plugins`
2. Select `kotlin-springboot-hexagonal`
3. Select `Install now`

Or directly install via:

```
/plugin install kotlin-springboot-hexagonal@ujon
```

## skills.sh (CLI)

```bash
npx skills add ujon/skills --skill kotlin-springboot-hexagonal
```
