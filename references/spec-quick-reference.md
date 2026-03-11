# Agent Skills Specification — Quick Reference

Condensed from the official Agent Skills open standard (agentskills.io) and Claude Code extensions (code.claude.com/docs/en/skills).

## Core Specification (agentskills.io)

### Required File
Every skill MUST have a `SKILL.md` file with YAML frontmatter + markdown body.

### Frontmatter Fields

| Field | Required | Constraints |
|-------|----------|-------------|
| `name` | Yes | 1-64 chars, lowercase + hyphens, no `--`, must match directory name |
| `description` | Yes | 1-1024 chars, non-empty, no XML tags |
| `license` | No | License name or reference to bundled LICENSE file |
| `compatibility` | No | 1-500 chars, environment requirements |
| `metadata` | No | Arbitrary key-value map (strings only) |
| `allowed-tools` | No | Space-delimited tool list (experimental) |

### Name Rules
```
Valid:   pdf-processing, data-analysis, code-review
Invalid: PDF-Processing (uppercase), -pdf (starts with -), pdf--proc (consecutive --)
```

### Description Rules
- Third person: "Analyzes..." not "I analyze..."
- Include WHAT + WHEN
- Include keywords users would say
- No `<` or `>` characters

### Directory Structure
```
skill-name/
├── SKILL.md           # Required
├── scripts/           # Optional: executable code
├── references/        # Optional: documentation
└── assets/            # Optional: templates, resources
```

### Progressive Disclosure (3 levels)
1. **Metadata** (~100 tokens): `name` + `description` loaded at startup for all skills
2. **Instructions** (<5000 tokens): SKILL.md body loaded when skill activates
3. **Resources** (as needed): scripts/, references/, assets/ loaded on demand

## Claude Code Extensions

Claude Code adds these frontmatter fields beyond the base spec:

| Field | Purpose |
|-------|---------|
| `disable-model-invocation` | `true` = only user can trigger (not Claude) |
| `user-invocable` | `false` = hidden from `/` menu (Claude-only) |
| `context` | `fork` = run in isolated subagent |
| `agent` | Subagent type when `context: fork` (`Explore`, `Plan`, `general-purpose`) |
| `model` | Model override for this skill |
| `hooks` | Lifecycle hooks scoped to this skill |
| `argument-hint` | Autocomplete hint (e.g., `[issue-number]`) |

### String Substitutions
| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed to the skill |
| `$ARGUMENTS[N]` or `$N` | Argument by 0-based index |
| `${CLAUDE_SESSION_ID}` | Current session ID |
| `${CLAUDE_SKILL_DIR}` | Directory containing SKILL.md |

### Dynamic Context Injection
`` !`command` `` syntax runs shell commands before skill content is sent to Claude. Output replaces the placeholder.

### Skill Locations (priority order)
| Level | Path | Scope |
|-------|------|-------|
| Enterprise | Managed settings | All org users |
| Personal | `~/.claude/skills/<name>/SKILL.md` | All your projects |
| Project | `.claude/skills/<name>/SKILL.md` | This project |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Where plugin enabled |

Higher priority wins when names conflict.

### Invocation Matrix
| Frontmatter | User can invoke | Claude can invoke |
|-------------|----------------|-------------------|
| (default) | Yes | Yes |
| `disable-model-invocation: true` | Yes | No |
| `user-invocable: false` | No | Yes |

### Tool Permissions
```yaml
# Read-only mode
allowed-tools: Read, Grep, Glob

# Specific bash commands
allowed-tools: Bash(git *) Bash(python *)

# Permission rules (in /permissions)
Skill(name)        # Exact match
Skill(name *)      # Prefix match
```

## Validation

Use the reference library to validate:
```bash
npx skills-ref validate ./my-skill
```

Or use skill-master's built-in validator:
```bash
python ~/.claude/skills/skill-master/scripts/validate_skill.py ./my-skill
```
