# Quality Checklist

Evaluate skills against Anthropic's official best practices. Rate each section and provide specific improvement suggestions.

## Frontmatter Quality

### Name
- [ ] Kebab-case only (lowercase, hyphens)
- [ ] No consecutive hyphens
- [ ] Doesn't start or end with hyphen
- [ ] Max 64 characters
- [ ] Matches parent directory name
- [ ] Descriptive — tells you what it does at a glance
- [ ] Preferably gerund form (e.g., `processing-pdfs`, `analyzing-data`)
- [ ] Doesn't contain "claude" or "anthropic" (reserved)

### Description
- [ ] Non-empty, max 1024 characters
- [ ] Third-person voice ("Analyzes..." not "I can help you...")
- [ ] Includes WHAT the skill does
- [ ] Includes WHEN to use it (trigger conditions)
- [ ] Includes specific phrases users would say
- [ ] Mentions relevant file types (if applicable)
- [ ] No XML tags (`<` or `>`)
- [ ] Doesn't summarize the workflow (just triggers)
- [ ] Specific enough to avoid over-triggering ("Helps with documents" = fail)

**Description formula:** `[What it does] + [When to use it] + [Key trigger phrases]`

## Structure Quality

### Progressive Disclosure
- [ ] SKILL.md body under 500 lines
- [ ] Detailed reference material in separate files (not inlined)
- [ ] References are one level deep (SKILL.md → ref.md, not ref.md → another.md)
- [ ] Long reference files (100+ lines) have a table of contents

### File Organization
- [ ] No README.md inside skill directory
- [ ] All referenced files actually exist
- [ ] File names are descriptive (`form_validation.md` not `doc2.md`)
- [ ] Directories organized by domain or feature
- [ ] Forward slashes in all paths (no backslashes)

### Directory Structure
- [ ] `SKILL.md` exists (exact case, exact spelling)
- [ ] `scripts/` only if executable code is needed
- [ ] `references/` only if separate docs are needed
- [ ] `assets/` only if templates/resources are needed
- [ ] No unnecessary nesting

## Instruction Quality

### Clarity
- [ ] Instructions are specific and actionable
- [ ] "Run `python scripts/validate.py --input {file}`" NOT "validate things properly"
- [ ] Critical instructions at the top, not buried
- [ ] Uses `## Important` or `## Critical` headers for must-follow rules
- [ ] Key points repeated if necessary

### Conciseness
- [ ] Only adds context Claude doesn't already have
- [ ] No explaining what PDFs are to Claude
- [ ] No explaining how libraries work
- [ ] Every paragraph justifies its token cost
- [ ] Default assumption: Claude is already very smart

### Degrees of Freedom
- [ ] Matches specificity to task fragility:
  - High freedom for flexible tasks (code review, analysis)
  - Low freedom for fragile tasks (deployments, migrations)
- [ ] Provides a default approach, with escape hatch for alternatives
- [ ] Doesn't offer too many options ("use pypdf or pdfplumber or PyMuPDF or...")

### Examples
- [ ] At least one concrete example (not abstract)
- [ ] Shows input → action → result
- [ ] One excellent example, not many mediocre ones
- [ ] Examples from real scenarios, not contrived

### Error Handling
- [ ] Common errors documented with causes and solutions
- [ ] Scripts handle errors explicitly (don't punt to Claude)
- [ ] Validation steps included for critical operations
- [ ] Feedback loops for quality-critical tasks (run → check → fix → repeat)

## Content Quality

### Terminology
- [ ] Consistent terms throughout (not mixing "endpoint" / "URL" / "route")
- [ ] Technical terms defined if domain-specific

### Time Sensitivity
- [ ] No "if before [date], do X" patterns
- [ ] Deprecated patterns in collapsible sections, not inline

### Workflows
- [ ] Complex tasks broken into numbered steps
- [ ] Dependencies between steps are explicit
- [ ] Validation at each stage
- [ ] Checklist format for multi-step processes

## Script Quality (if scripts/ exists)

- [ ] Scripts are self-contained or document dependencies
- [ ] Error handling is explicit with helpful messages
- [ ] No "voodoo constants" — all values justified with comments
- [ ] Required packages listed in instructions
- [ ] Clear whether Claude should execute vs. read as reference
- [ ] Forward slashes in all paths
- [ ] Scripts handle edge cases gracefully

## Testing Readiness

- [ ] At least 3 test scenarios identified
- [ ] "Should trigger" examples listed
- [ ] "Should NOT trigger" examples listed
- [ ] Tested with real usage (not just hypothetical)
- [ ] Works with intended model(s) — Haiku needs more guidance than Opus

## Overall Rating

| Rating | Criteria |
|--------|----------|
| **EXCELLENT** | All checks pass, well-tested, clear descriptions, proper progressive disclosure |
| **GOOD** | Minor issues (e.g., description could be more specific, missing 1-2 examples) |
| **NEEDS WORK** | Structural issues (SKILL.md too long, missing error handling, vague description) |
| **POOR** | Fundamental problems (broken frontmatter, no clear purpose, security concerns) |
