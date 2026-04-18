# IDE Template Variables Reference

This file documents the template variables and configuration methods for each major IDE's AI commit message feature. Read this when the user asks for an IDE-specific commit message prompt.

## Table of Contents

1. [JetBrains IDEs (IntelliJ, WebStorm, PyCharm, etc.)](#jetbrains)
2. [VS Code](#vscode)
3. [Xcode](#xcode)
4. [GitHub Desktop](#github-desktop)
5. [Sublime Merge](#sublime-merge)
6. [Neovim / Vim](#neovim)
7. [Emacs (Magit)](#emacs)
8. [Prompt Generation Guidelines](#prompt-generation-guidelines)

---

## JetBrains IDEs (IntelliJ, WebStorm, PyCharm, etc.) {#jetbrains}

### Where to configure

Settings → Version Control → Commit → AI Commit Message prompt (or custom AI Assistant prompt)

### Available variables

| Variable              | Description                                |
| --------------------- | ------------------------------------------ |
| `$GIT_BRANCH_NAME`    | Current branch name                        |
| `$GIT_DIFF`           | Staged diff content                        |
| `$GIT_COMMIT_MESSAGE` | Previous commit message (useful for amend) |
| `$GIT_LOG`            | Recent commit log                          |
| `$FILE_LIST`          | List of changed files                      |

### Configuration format

Plain text prompt pasted into the AI commit message prompt field.

---

## VS Code {#vscode}

### Where to configure

- GitHub Copilot: `settings.json` → `github.copilot.chat.commitMessageGeneration.instructions`
- Other AI extensions: Check extension-specific settings

### Available variables

| Variable       | Description           |
| -------------- | --------------------- |
| `${gitDiff}`   | Staged diff content   |
| `${gitBranch}` | Current branch name   |
| `${gitLog}`    | Recent commit history |
| `${fileList}`  | Changed file list     |

### Configuration format

JSON array in `settings.json`:

```json
{
	"github.copilot.chat.commitMessageGeneration.instructions": [
		{
			"text": "Your prompt here"
		}
	]
}
```

---

## Xcode {#xcode}

### Where to configure

- Source Control preferences → Git → Commit template
- Or use a `.gitmessage` template file
- Or integrate via git hooks (`prepare-commit-msg`)

### Available variables

Xcode does not have built-in AI commit template variables. Use shell commands:
| Command | Description |
|---------|-------------|
| `$(git diff --cached)` | Staged diff |
| `$(git branch --show-current)` | Current branch |
| `$(git log --oneline -10)` | Recent commits |

### Notes

For AI-powered commit messages in Xcode, recommend setting up a `prepare-commit-msg` git hook or using a companion CLI tool.

---

## GitHub Desktop {#github-desktop}

### Where to configure

- Uses `.gitmessage` file in the repository root
- No built-in AI commit message feature

### Available variables

None — GitHub Desktop doesn't support template variables.

### Recommendation

Set up a `.gitmessage` file with a structural template:

```
# <verb> <description> (#<issue>)
#
# ## Summary
# - Why:
# - What:
#
# ## Changes
# ### <Layer>
# - `Class`: detail
```

---

## Sublime Merge {#sublime-merge}

### Where to configure

- Preferences → Commit Message Template
- Or `.gitmessage` file

### Available variables

None built-in. Can use custom commands or git hooks.

---

## Neovim / Vim {#neovim}

### Where to configure

- AI plugins (e.g., Copilot.vim, codecompanion.nvim, etc.) — check plugin-specific config
- Git commit template: `git config commit.template`

### Common plugin variables

Varies by plugin. Most pass the staged diff as context automatically.

### Recommendation

Configure via `prepare-commit-msg` hook or plugin-specific prompt settings.

---

## Emacs (Magit) {#emacs}

### Where to configure

- Magit commit template settings
- `git-commit-setup-hook` for custom logic
- AI via gptel, ellama, or similar packages

### Available variables

Depends on the AI package. Most pass buffer content (diff) as context.

---

## Prompt Generation Guidelines {#prompt-generation-guidelines}

When generating a prompt for any IDE:

1. **Read `commit-format.md`** to get the canonical format rules
2. **Substitute the IDE's native variables** for diff, branch, log, etc.
3. **Match the IDE's configuration format** (plain text, JSON, etc.)
4. **Include these essential elements in the prompt:**
   - The diff/changes variable
   - The branch name variable (for issue number extraction)
   - Recent commit log variable (for style reference)
   - All format rules from commit-format.md condensed into the prompt
5. **End with**: "Output ONLY the commit message. No explanation."
6. **For IDEs without AI variables**: recommend git hook or CLI-based approach
