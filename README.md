# skill-master

**The skill for building, importing, and auditing agent skills.**

skill-master is a meta-skill for [Claude Code](https://claude.ai/code) that guides you through creating new skills from scratch, importing skills from external sources with security vetting, and reviewing existing skills for quality. Built primarily on [**The Complete Guide to Building Skills for Claude**](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) by Anthropic, with security hardening from real-world threat research.

---

## Why This Exists

The agent skills ecosystem is growing fast. [SkillHub](https://www.skillhub.club/) alone hosts 24,000+ skills. [Snyk's ToxicSkills research](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) found that **13% of community skills contain critical security flaws**, including credential theft, prompt injection, and hidden malware. Creating a well-structured skill from scratch means knowing the spec, best practices, and dozens of small decisions.

skill-master solves both problems:

- **Creating skills** — Interactive guided workflow that explains every decision in plain English, generates spec-compliant output, and recommends complementary skills from the ecosystem.
- **Importing skills** — Automated security scanning before installation. Every skill gets checked against 40+ threat patterns derived from real malware samples.
- **Reviewing skills** — Quality assessment against [Anthropic's official best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) with actionable improvement suggestions.

---

## Quick Start

### Install

```bash
git clone https://github.com/hexcantcode/skill-master.git ~/.claude/skills/skill-master
```

### Use

skill-master activates automatically when you ask Claude to create, import, or review a skill. You can also invoke it directly:

```
/skill-master
```

**Create a skill:**
```
"Help me create a skill for reviewing pull requests"
```

**Import a skill from a URL:**
```
"Import this skill: https://github.com/trailofbits/skills"
```

**Review an existing skill:**
```
"Review my solidity-auditor skill for quality and security"
```

---

## What's Inside

```
skill-master/
├── SKILL.md                          # Main entry — mode detection + routing
│
├── references/
│   ├── creation-workflow.md          # 7-step interactive creation guide
│   ├── import-audit-workflow.md      # Fetch → Scan → Gate → Install
│   ├── security-checklist.md         # 5 threat categories, 40+ patterns
│   ├── quality-checklist.md          # Anthropic best practices evaluation
│   ├── spec-quick-reference.md       # Agent Skills spec condensed
│   └── supplementary-skills-guide.md # How to find complementary skills
│
├── scripts/
│   ├── validate_skill.py             # Structure + frontmatter validator
│   └── security_scan.py              # ToxicSkills-based threat scanner
│
├── assets/
│   ├── skill-template.md             # Starter SKILL.md template
│   └── github-readme-template.md     # README template for hosting skills
│
└── LICENSE                           # MIT
```

---

## Three Modes

### CREATE — Build a new skill

Walks you through an interactive flow:

1. **Understand** — Asks about purpose, audience, and use cases
2. **Decide** — Presents 4 critical architectural decisions, each explained in plain English for non-technical users:
   - Who can trigger it? (auto vs manual)
   - Where should it run? (inline vs sandboxed)
   - What tools can it access? (unrestricted vs locked down)
   - How complex is it? (single file vs full toolkit)
3. **Draft** — Generates spec-compliant SKILL.md with proper frontmatter
4. **Supplement** — Recommends complementary skills from SkillHub, Anthropic's official repo, and your installed skills
5. **Validate** — Runs automated structure and security checks
6. **Scaffold** — Creates the full directory
7. **Ship** — Optionally generates a GitHub README and guides you through publishing

### IMPORT — Audit and install external skills

```
Security scan → Gate → Validate → Quality check → Supplement → Install
```

Every imported skill passes through the security scanner first. The scanner produces one of three ratings:

| Rating | Score | Action |
|--------|-------|--------|
| **SAFE** | 0-1 | Proceed with installation |
| **CAUTION** | 2-5 | Each finding explained in plain English, requires your explicit approval |
| **DANGER** | 6+ | Installation blocked, with explanation of what was found |

### REVIEW — Check an existing skill

Combines both scanners on a skill you already have installed, plus a manual quality assessment against Anthropic's best practices checklist. Outputs a rating (EXCELLENT / GOOD / NEEDS WORK / POOR) with specific fixes.

---

## Security Scanner

The security scanner checks for **5 threat categories** based on [Snyk's ToxicSkills study](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) of 3,984 community skills:

| Category | What It Detects | Real-World Prevalence |
|----------|----------------|----------------------|
| **Prompt Injection** | Role overrides, safety suppression, instruction hijacking | 91% of malicious skills |
| **Malicious Code** | Download-and-execute, obfuscated payloads, privilege escalation | 100% of confirmed malware |
| **Credential Theft** | Env var harvesting, SSH/AWS/Docker credential access | 63% of malicious skills |
| **Security Disablement** | Firewall disabling, history clearing, shell profile backdoors | Common in destructive skills |
| **Data Exfiltration** | Outbound POST with local data, DNS exfiltration, encoded transmission | 54% use third-party fetching |

The scanner is **code-fence aware** — it won't flag patterns that appear inside markdown code blocks (documentation examples), only actual instructions and executable code.

### Run it standalone

```bash
# Security scan
python3 ~/.claude/skills/skill-master/scripts/security_scan.py /path/to/skill

# Structure validation
python3 ~/.claude/skills/skill-master/scripts/validate_skill.py /path/to/skill
```

---

## Compatibility

| Platform | Status |
|----------|--------|
| [Claude Code](https://claude.ai/code) | Fully supported |
| [Codex CLI](https://github.com/openai/codex) | Agent Skills compatible |
| [Gemini CLI](https://geminicli.com) | Agent Skills compatible |
| [OpenCode](https://opencode.ai) | Agent Skills compatible |
| [Cursor](https://cursor.com) | Agent Skills compatible |

The skill follows the [Agent Skills open standard](https://agentskills.io), so it works with any compatible agent. The Python scripts require Python 3.8+ (stdlib only, no dependencies).

---

## Sources & Acknowledgments

Built on research and specifications from:

- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) — Anthropic (2026)
- [Agent Skills Specification](https://agentskills.io/specification) — Open standard
- [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Anthropic
- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills) — Anthropic
- [ToxicSkills: Agent Skills Supply Chain Compromise](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) — Snyk (2026)
- [SkillHub](https://www.skillhub.club/) — Community marketplace (24,000+ skills)

---

## License

MIT — see [LICENSE](LICENSE) for details.
