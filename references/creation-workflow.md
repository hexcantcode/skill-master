# Skill Creation Workflow

Follow these steps sequentially. Do NOT skip the decision points — each one shapes the final skill.

## Step 1: Understand the Skill's Purpose

Ask the user these questions (adapt language to their technical level):

**Required questions:**
1. "What task should this skill help with?" — Get a concrete description, not abstract
2. "Who will use it?" — Just you, your team, or the public?
3. "Give me 2-3 example scenarios where you'd want this skill to activate."

**Follow-up if needed:**
4. "Does this skill need to call any external tools or APIs?" (determines MCP integration)
5. "Are there any existing skills that do something similar?" (avoid duplication)

**From the answers, determine:**
- Skill category: Document/Asset Creation, Workflow Automation, or MCP Enhancement
- Scope: Personal (`~/.claude/skills/`), Project (`.claude/skills/`), or Plugin
- Complexity: Simple (SKILL.md only) vs. Complex (scripts, references, assets)

## Step 1b: Check for Existing Skills

Before going further, check if a skill that covers the same ground already exists.

**Scan installed skills:**
```bash
# Personal skills
ls ~/.claude/skills/

# Project skills
ls .claude/skills/ 2>/dev/null
```

Read the description of each installed skill and compare with what the user described in Step 1. Look for:
- Same domain or purpose
- Overlapping trigger phrases or scenarios
- Skills that already cover part of what the user wants

**If a match is found:**
> "You already have `<existing-skill>` installed, which does [overlapping thing]. Here's what it covers:
>
> [Brief summary of existing skill's capabilities]
>
> Options:
> 1. **Extend it** — Add the missing capabilities to the existing skill instead of creating a new one
> 2. **Create anyway** — Build a separate skill (both will be available, Claude picks the best match per task)
> 3. **Replace it** — Create the new skill and remove the old one
>
> What would you prefer?"

**If no match:** Tell the user no overlap was found and proceed to Step 2.

## Step 2: Critical Decisions (Explain Each to User)

Present each decision with a plain-English explanation. Pause for user input on each.

### Decision 1: Who Can Trigger This Skill?

> **Think of skills like tools in a workshop.**
>
> Some tools — like a tape measure — should always be within reach. Claude picks them up automatically when they're relevant. Others — like a power saw — should only run when YOU flip the switch.
>
> **Option A: Both you and Claude can trigger it** (default)
> Good for: coding conventions, style guides, reference knowledge, analysis tools
>
> **Option B: Only you can trigger it** (`disable-model-invocation: true`)
> Good for: deployments, sending messages, anything with side effects or that costs money
>
> **Option C: Only Claude can trigger it** (`user-invocable: false`)
> Good for: background knowledge that isn't a meaningful action (e.g., "legacy system context")

**Impact:** This controls the `disable-model-invocation` and `user-invocable` frontmatter fields.

### Decision 2: Where Should It Run?

> **When this skill runs, should it work inside your current conversation, or in a separate sandbox?**
>
> **Option A: Inline** (default)
> The skill's instructions blend into your conversation. Claude can see everything you've discussed. Best for reference knowledge, conventions, and lightweight tasks.
>
> **Option B: Forked / Sandboxed** (`context: fork`)
> The skill runs in isolation — like sending a specialist into a separate room with just the task description. They come back with results but don't see your conversation history. Best for: deep research, heavy analysis, tasks that might pollute your context.

**Impact:** This controls the `context` frontmatter field. If forked, also ask which agent type (`Explore`, `Plan`, `general-purpose`).

### Decision 3: What Tools Should It Access?

> **By default, Claude can use any tool when running your skill — reading files, writing code, running commands, browsing the web. You can restrict this.**
>
> **Option A: All tools** (default)
> Best for: general-purpose skills that need flexibility
>
> **Option B: Read-only** (`allowed-tools: Read, Grep, Glob`)
> Best for: analysis, research, and review skills that shouldn't modify anything
>
> **Option C: Custom list**
> You pick exactly which tools. Best for: skills where you want tight control.
>
> **Why restrict?** If someone imports your skill, restricted tools mean less risk. A "code reviewer" skill that can only read files can't accidentally delete anything.

**Impact:** This controls the `allowed-tools` frontmatter field.

### Decision 4: How Complex Is It?

> **Skills range from a single instruction file to a full toolkit with scripts and documentation.**
>
> **Simple** — Just a SKILL.md file with instructions. Good for conventions, checklists, small workflows. Most skills start here.
>
> **Medium** — SKILL.md + a few reference files in `references/`. Good when you have detailed docs that shouldn't load every time (API specs, long guides).
>
> **Complex** — SKILL.md + scripts + references + assets. Good for skills that generate visual output, validate data, or orchestrate multi-step processes.
>
> **Rule of thumb:** Start simple. You can always add complexity later. If SKILL.md is under 500 lines, you probably don't need separate files yet.

**Impact:** This determines directory structure and whether to create scripts/ and references/ directories.

## Step 3: Draft the Skill

### 3a: Generate Frontmatter

Based on decisions above, generate YAML frontmatter:

```yaml
---
name: <kebab-case-name>
description: <third-person, what + when, 100-300 chars recommended>
# Include these ONLY if needed:
# disable-model-invocation: true    # Decision 1 Option B
# user-invocable: false             # Decision 1 Option C
# context: fork                     # Decision 2 Option B
# agent: Explore                    # Only with context: fork
# allowed-tools: Read, Grep, Glob   # Decision 3 Option B/C
# license: MIT
# metadata:
#   author: <name>
#   version: "1.0"
---
```

**Validate the name:**
- Lowercase letters, numbers, hyphens only
- No consecutive hyphens (`--`)
- Doesn't start or end with hyphen
- Max 64 characters
- Can't contain "claude" or "anthropic" (reserved)
- Must match the directory name

**Validate the description:**
- Third person ("Analyzes..." not "I analyze..." or "You can use this to...")
- Includes WHAT it does AND WHEN to use it
- Includes specific trigger phrases users would say
- Max 1024 characters, no XML tags (`<` or `>`)
- Does NOT summarize the workflow (just triggers — see CSO principle)

### 3b: Write the Body

Follow this structure (adapt sections based on complexity):

```markdown
# Skill Name

Brief overview — what is this and why does it exist? Core principle in 1-2 sentences.

## When to Use
- Specific symptom or scenario 1
- Specific symptom or scenario 2
- When NOT to use (important for avoiding over-triggering)

## Instructions

### Step 1: [First Action]
Clear, specific instructions. Be actionable, not vague.

### Step 2: [Second Action]
Include validation — how to check this step succeeded.

(Continue steps as needed)

## Examples

**Example 1: [Common scenario]**
User says: "..."
Actions: ...
Result: ...

## Additional Resources
- For [detailed topic], see [reference-file.md](references/reference-file.md)
- For [utility], run `scripts/utility.py`

## Common Mistakes
- Mistake 1 → Fix
- Mistake 2 → Fix
```

**Writing principles (from Anthropic best practices):**
- Claude is already smart — only add context it doesn't already have
- Be specific and actionable (not "validate things properly" but "run `python scripts/validate.py --input {file}`")
- Use progressive disclosure — keep SKILL.md under 500 lines, move details to references/
- One excellent example beats many mediocre ones
- Use consistent terminology throughout
- Avoid time-sensitive information
- Keep references one level deep (SKILL.md → reference.md, never reference.md → another.md)

### 3c: Create Supporting Files (if Medium/Complex)

**References:** For detailed docs over 100 lines, create separate files. Add a table of contents at the top of each. Link clearly from SKILL.md.

**Scripts:** Should be self-contained, handle errors explicitly (not punt to Claude), document all constants, and include helpful error messages. Use forward slashes in all paths.

**Assets:** Templates, configuration files, icons. Reference with relative paths from SKILL.md.

## Step 4: Recommend Supplementary Skills

After drafting, analyze the skill's domain and suggest complementary skills. See [supplementary-skills-guide.md](supplementary-skills-guide.md) for the full approach.

Present recommendations like:
> "Your skill does X. Here are skills that pair well with it:
> - **[skill-name]** — does Y, which complements X because...
> - **[skill-name]** — provides Z reference that your skill could cross-reference
>
> Want me to add any of these as references or cross-links?"

## Step 5: Validate

Run both validation scripts:

```bash
python ~/.claude/skills/skill-master/scripts/validate_skill.py <path-to-skill-dir>
python ~/.claude/skills/skill-master/scripts/security_scan.py <path-to-skill-dir>
```

Fix any issues before proceeding.

## Step 6: Scaffold the Directory

Create the final directory structure. Verify:
- [ ] Directory name matches frontmatter `name`
- [ ] SKILL.md exists (exact case)
- [ ] No README.md inside the skill directory (that's for the GitHub repo, not the skill itself)
- [ ] All referenced files actually exist
- [ ] Scripts are executable (`chmod +x`)

## Step 7: Ship It (Optional)

Ask the user: "Would you like to host this skill on GitHub for others to use, or keep it local?"

If they want to keep it local, skip to the Post-Creation Checklist below. The skill is already installed and working.

### If Hosting on GitHub

Use the template at `assets/github-readme-template.md` to create a repo-level README (separate from the skill folder). This README is for human visitors, not Claude.

Guide the user:

> "To share your skill with the community:
>
> 1. **Create a GitHub repo** named after your skill (e.g., `skill-name`)
> 2. **Add the skill folder** as the root content
> 3. **Add the README.md** at the repo root (outside the skill folder)
> 4. **Add a LICENSE** file (MIT recommended for open source)
> 5. **Tag a release** so people can download a specific version
>
> Others can then install it by cloning your repo into their `~/.claude/skills/` directory.
> You can also submit it to SkillHub (skillhub.club) for wider discovery."

### Post-Creation Checklist

Ask the user:
- [ ] "Have you tested the skill with a real task? (Not hypothetical)"
- [ ] "Does it trigger when you expect? Try 3 different phrasings."
- [ ] "Does it NOT trigger on unrelated requests?"
- [ ] "Did you test with the model you'll actually use? (Haiku needs more guidance than Opus)"
