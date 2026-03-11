# Supplementary Skills Guide

How to discover and recommend complementary skills for any skill being created, imported, or reviewed.

## Why Supplementary Skills Matter

Skills are composable — Claude can load multiple skills simultaneously. A skill that works well alone becomes more powerful when paired with complementary skills. Recommending the right supplements increases value without the user having to discover them on their own.

## Discovery Sources

### 1. User's Installed Skills

Check what's already installed:
```bash
# Personal skills
ls ~/.claude/skills/

# Project skills
ls .claude/skills/

# Plugin skills
ls .claude/plugins/*/skills/ 2>/dev/null
```

Cross-reference the new skill's domain against installed skills. If they overlap or complement, suggest linking them.

### 2. Anthropic Official Skills (github.com/anthropics/skills)

Curated, Apache-2.0 licensed skills from Anthropic. High quality baseline.

**Document skills:** docx, pdf, pptx, xlsx — production-grade document creation
**Example skills:** Various workflow patterns for learning and adaptation

**When to recommend:** If the user's skill involves document generation, data processing, or workflow automation, check if an Anthropic official skill covers part of the need.

### 3. SkillHub (skillhub.club)

24,000+ community skills with AI-graded quality ratings.

**Quality grades:**
- **S-rank (9.0+):** Exceptional — safe to recommend
- **A-rank (8.0+):** Excellent — recommend with confidence
- **B-rank (7.0+):** Good — recommend with note about quality
- **Below B:** Don't recommend without user explicitly asking

**How to search:**
```bash
npx @skill-hub/cli search "<keyword>"
```

Or guide user to browse: `https://www.skillhub.club/`

**Categories to check:**
- Development, Frontend, Backend
- Data, AI/ML
- Security, DevOps, Testing
- Productivity, Documentation

### 4. Community Repositories

Notable community skill collections:
- `github.com/mhattingpete/claude-skills-marketplace` — Git automation, testing, code review
- `github.com/daymade/claude-code-skills` — 42 production-ready skills

**IMPORTANT:** Community skills MUST go through the import-audit-workflow security scan before recommending.

## Recommendation Strategy

### Matching by Domain

| Skill Domain | Likely Supplements |
|-------------|-------------------|
| Smart contract / Solidity | `solidity-auditor`, `token-integration-analyzer`, `defi-protocol-templates` |
| Frontend development | `frontend-design`, `senior-frontend`, `webapp-testing` |
| Backend / API | `senior-backend`, `api-integration-specialist`, `senior-architect` |
| Security / Auditing | `senior-security`, `security-compliance`, `nemesis-auditor` |
| DevOps / Infrastructure | `senior-architect`, `security-compliance` |
| Documentation / Writing | `ui-design-system` (for design docs), document skills (docx, pdf) |
| Data analysis | `xlsx` skill, custom visualization skills |
| Code quality | `requesting-code-review`, `senior-fullstack` |

### Matching by Capability Gap

Analyze what the skill does NOT cover that users might need:

1. **Skill creates output** → Recommend a validation/review skill
2. **Skill analyzes code** → Recommend a testing/fixing skill
3. **Skill uses MCP** → Recommend the MCP server's companion skill (if exists)
4. **Skill automates workflow** → Recommend a monitoring/logging skill
5. **Skill is domain-specific** → Recommend a general-purpose skill for context

### Matching by Workflow Stage

If the skill covers one stage of a workflow, suggest skills for adjacent stages:

```
Plan → Implement → Test → Review → Deploy
 |        |          |       |        |
 v        v          v       v        v
senior-   senior-   webapp- request-  skill for
architect fullstack testing code-     deployment
                            review
```

## How to Present Recommendations

### For CREATE Mode

After drafting the skill, present 2-4 recommendations:

> "Your skill handles [X]. Here are skills that complement it:
>
> **Already installed:**
> - `senior-security` — You already have this. Your skill could cross-reference its `references/security_architecture_patterns.md` for [specific topic].
>
> **From the ecosystem:**
> - `[skill-name]` (SkillHub, A-rank) — Does [Y], which your skill doesn't cover. Users doing [X] often also need [Y].
> - `[skill-name]` (anthropics/skills) — Official Anthropic skill for [Z]. Could be added as a reference.
>
> Want me to:
> 1. Add cross-references to any of these in your SKILL.md?
> 2. Install any that aren't already installed?"

### For IMPORT Mode

After security scan passes:

> "This skill does [X]. Pairing suggestions:
>
> - `[installed-skill]` — Already installed, works well with this for [reason]
> - `[new-skill]` — Would fill [gap]. Want me to audit and install it too?
>
> Note: Any new skill from the ecosystem will go through the same security scan."

### For REVIEW Mode

After quality assessment:

> "This skill could be enhanced with:
> - Adding a cross-reference to `[skill]` for [topic] its references/ don't cover
> - Linking to `[skill]`'s scripts/ for [capability]"

## Cross-Referencing Best Practices

When adding references to other skills:

**In SKILL.md body:**
```markdown
## Related Skills
- For security auditing, see the `senior-security` skill
- For testing generated output, pair with `webapp-testing`
```

**Do NOT force-load with @:**
```markdown
# BAD — burns context immediately
@~/.claude/skills/senior-security/SKILL.md

# GOOD — Claude loads when needed
See the `senior-security` skill for security architecture patterns.
```

**As reference file links:**
```markdown
For detailed security patterns, consult your `senior-security` skill's
`references/security_architecture_patterns.md`.
```
