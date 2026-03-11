# {Skill Name}

> {One-line description of what this skill does}

## What It Does

{2-3 sentences explaining the skill's purpose and value. Focus on outcomes, not implementation.}

## Quick Start

### Installation

**Claude Code:**
```bash
# Clone into your personal skills directory
git clone https://github.com/{username}/{repo-name}.git ~/.claude/skills/{skill-name}
```

**Claude.ai:**
1. Download this repository as a ZIP
2. Go to Settings > Capabilities > Skills
3. Upload the ZIP file
4. Enable the skill

### Usage

{Show 2-3 example invocations}

```
# Automatic (Claude detects when relevant)
"Your natural language trigger phrase here"

# Direct invocation
/{skill-name} [arguments]
```

## What's Included

```
{skill-name}/
├── SKILL.md              # Main instructions
├── references/            # Detailed documentation (loaded on demand)
│   └── ...
├── scripts/               # Utility scripts
│   └── ...
└── assets/                # Templates and resources
    └── ...
```

## How It Works

{Brief explanation of the skill's approach — enough for someone to understand if this skill fits their needs. 3-5 bullet points.}

## Requirements

- {Any system requirements, e.g., "Python 3.8+"}
- {Any MCP server dependencies}
- {Any environment variables needed}

{If no special requirements: "No special requirements. Works with any Claude Code or Claude.ai setup."}

## Compatibility

| Platform | Supported |
|----------|-----------|
| Claude Code | Yes |
| Claude.ai | Yes |
| Claude API | Yes (requires Code Execution beta) |
| Codex CLI | Yes (Agent Skills compatible) |

## Contributing

{If open source:}
Contributions welcome! Please:
1. Fork this repository
2. Create a feature branch
3. Test your changes with real usage scenarios
4. Submit a pull request

## License

MIT License — see [LICENSE](LICENSE) for details.

---

Built with [skill-master](https://github.com/{username}/skill-master) | Compatible with the [Agent Skills](https://agentskills.io) open standard
