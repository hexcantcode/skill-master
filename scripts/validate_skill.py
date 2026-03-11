#!/usr/bin/env python3
"""
Validate an Agent Skill's structure and frontmatter against the official specification.

Usage:
    python validate_skill.py <path-to-skill-directory>

Exit codes:
    0 = valid (all checks pass)
    1 = errors found (must fix)
    2 = warnings only (recommended fixes)
"""

import re
import sys
import os
from pathlib import Path

# ─── Constants ───────────────────────────────────────────────────────────────

MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
MAX_SKILL_MD_LINES = 500
RESERVED_PREFIXES = ("claude", "anthropic")
NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def parse_frontmatter(content: str) -> tuple[dict | None, str, list[str]]:
    """Parse YAML frontmatter from SKILL.md content.
    Returns (frontmatter_dict, body, errors).
    Uses manual parsing to avoid PyYAML dependency."""
    errors = []
    lines = content.split("\n")

    if not lines or lines[0].strip() != "---":
        errors.append("ERROR: SKILL.md must start with YAML frontmatter (--- delimiter)")
        return None, content, errors

    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break

    if end_idx is None:
        errors.append("ERROR: YAML frontmatter missing closing --- delimiter")
        return None, content, errors

    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:])
    fm = {}
    current_key = None
    current_value_lines = []

    for line in fm_lines:
        if line.strip() == "" or line.strip().startswith("#"):
            continue

        # Check for new key: value pair (not indented)
        kv_match = re.match(r'^([a-z_-]+)\s*:\s*(.*)', line)
        if kv_match and not line.startswith(" ") and not line.startswith("\t"):
            if current_key:
                fm[current_key] = "\n".join(current_value_lines).strip()
            current_key = kv_match.group(1)
            current_value_lines = [kv_match.group(2).strip().strip('"').strip("'")]
        elif current_key and (line.startswith("  ") or line.startswith("\t")):
            current_value_lines.append(line.strip())
        elif current_key:
            # Continuation of multiline value
            current_value_lines.append(line.strip())

    if current_key:
        fm[current_key] = "\n".join(current_value_lines).strip()

    return fm, body, errors


def validate_name(name: str, dir_name: str) -> list[str]:
    """Validate the name field against spec requirements."""
    issues = []

    if not name:
        issues.append("ERROR: 'name' field is empty")
        return issues

    if len(name) > MAX_NAME_LENGTH:
        issues.append(f"ERROR: 'name' is {len(name)} chars (max {MAX_NAME_LENGTH})")

    if not NAME_PATTERN.match(name):
        if name != name.lower():
            issues.append("ERROR: 'name' must be lowercase only")
        elif "--" in name:
            issues.append("ERROR: 'name' must not contain consecutive hyphens (--)")
        elif name.startswith("-") or name.endswith("-"):
            issues.append("ERROR: 'name' must not start or end with a hyphen")
        elif " " in name:
            issues.append("ERROR: 'name' must not contain spaces (use hyphens)")
        elif "_" in name:
            issues.append("ERROR: 'name' must not contain underscores (use hyphens)")
        else:
            issues.append("ERROR: 'name' may only contain lowercase letters, numbers, and hyphens")

    for prefix in RESERVED_PREFIXES:
        if name.startswith(prefix):
            issues.append(f"ERROR: 'name' must not start with reserved prefix '{prefix}'")

    if name != dir_name:
        issues.append(f"WARNING: 'name' ({name}) does not match directory name ({dir_name})")

    return issues


def validate_description(desc: str) -> list[str]:
    """Validate the description field against spec requirements."""
    issues = []

    if not desc:
        issues.append("ERROR: 'description' field is empty")
        return issues

    if len(desc) > MAX_DESCRIPTION_LENGTH:
        issues.append(f"ERROR: 'description' is {len(desc)} chars (max {MAX_DESCRIPTION_LENGTH})")

    if "<" in desc or ">" in desc:
        issues.append("ERROR: 'description' must not contain XML tags (< or >)")

    # Quality warnings
    if desc.startswith("I ") or "I can" in desc or "I help" in desc:
        issues.append("WARNING: 'description' should be third-person ('Analyzes...' not 'I analyze...')")

    if desc.startswith("You ") or "You can" in desc:
        issues.append("WARNING: 'description' should be third-person, not second-person")

    lower = desc.lower()
    vague_descriptions = [
        "helps with", "does stuff", "processes data", "helps you",
        "a tool for", "utility for"
    ]
    for vague in vague_descriptions:
        if lower.startswith(vague) or lower == vague:
            issues.append(f"WARNING: 'description' is too vague (starts with '{vague}')")
            break

    trigger_phrases = ["use when", "use for", "trigger", "invoke", "ask"]
    has_trigger = any(phrase in lower for phrase in trigger_phrases)
    if not has_trigger:
        issues.append("WARNING: 'description' should include when to use it (e.g., 'Use when...')")

    return issues


def validate_structure(skill_dir: Path) -> list[str]:
    """Validate the skill directory structure."""
    issues = []

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        # Check for common mistakes
        for variant in ["skill.md", "SKILL.MD", "Skill.md", "skill.MD"]:
            if (skill_dir / variant).exists():
                issues.append(f"ERROR: Found '{variant}' but must be exactly 'SKILL.md' (case-sensitive)")
                return issues
        issues.append("ERROR: SKILL.md not found in skill directory")
        return issues

    # Check for README.md inside skill dir (should be at repo level, not skill level)
    if (skill_dir / "README.md").exists():
        issues.append("WARNING: README.md found inside skill directory. "
                       "README should be at the GitHub repo level, not inside the skill folder.")

    # Check for hidden/dotfiles
    for item in skill_dir.rglob("*"):
        if item.name.startswith(".") and item.name != ".gitkeep":
            issues.append(f"WARNING: Hidden file found: {item.relative_to(skill_dir)}")

    # Check SKILL.md line count
    try:
        with open(skill_md) as f:
            lines = f.readlines()
        line_count = len(lines)
        if line_count > MAX_SKILL_MD_LINES:
            issues.append(f"WARNING: SKILL.md is {line_count} lines (recommended max {MAX_SKILL_MD_LINES}). "
                          "Consider moving detailed content to references/.")
    except Exception as e:
        issues.append(f"ERROR: Could not read SKILL.md: {e}")

    # Check referenced files exist
    try:
        content = skill_md.read_text()
        # Find markdown links: [text](path)
        link_pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
        for match in link_pattern.finditer(content):
            link_path = match.group(2)
            # Skip URLs
            if link_path.startswith("http") or link_path.startswith("#"):
                continue
            # Resolve relative to skill_md's parent
            ref_path = skill_dir / link_path
            if not ref_path.exists():
                issues.append(f"ERROR: Referenced file not found: {link_path}")
    except Exception:
        pass

    # Check scripts are executable (Unix only)
    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for script in scripts_dir.iterdir():
            if script.is_file() and script.suffix in (".py", ".sh", ".bash"):
                if not os.access(script, os.X_OK):
                    issues.append(f"WARNING: Script not executable: scripts/{script.name} "
                                  f"(run: chmod +x {script})")

    return issues


def validate_compatibility(compat: str) -> list[str]:
    """Validate the optional compatibility field."""
    issues = []
    if compat and len(compat) > MAX_COMPATIBILITY_LENGTH:
        issues.append(f"WARNING: 'compatibility' is {len(compat)} chars (max {MAX_COMPATIBILITY_LENGTH})")
    return issues


def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_skill.py <path-to-skill-directory>")
        print("  Validates an Agent Skill against the official specification.")
        sys.exit(1)

    skill_dir = Path(sys.argv[1]).resolve()

    if not skill_dir.is_dir():
        print(f"ERROR: {skill_dir} is not a directory")
        sys.exit(1)

    print(f"Validating skill: {skill_dir.name}")
    print("=" * 60)

    all_issues = []

    # 1. Structure validation
    print("\n[1/3] Checking directory structure...")
    struct_issues = validate_structure(skill_dir)
    all_issues.extend(struct_issues)
    for issue in struct_issues:
        print(f"  {issue}")
    if not struct_issues:
        print("  All structure checks passed.")

    # 2. Frontmatter validation
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        print("\n[2/3] Checking frontmatter...")
        content = skill_md.read_text()
        fm, body, parse_errors = parse_frontmatter(content)
        all_issues.extend(parse_errors)
        for err in parse_errors:
            print(f"  {err}")

        if fm is not None:
            # Validate name
            name = fm.get("name", "")
            if not name:
                all_issues.append("ERROR: 'name' field is missing from frontmatter")
                print("  ERROR: 'name' field is missing from frontmatter")
            else:
                name_issues = validate_name(name, skill_dir.name)
                all_issues.extend(name_issues)
                for issue in name_issues:
                    print(f"  {issue}")

            # Validate description
            desc = fm.get("description", "")
            if not desc:
                all_issues.append("ERROR: 'description' field is missing from frontmatter")
                print("  ERROR: 'description' field is missing from frontmatter")
            else:
                desc_issues = validate_description(desc)
                all_issues.extend(desc_issues)
                for issue in desc_issues:
                    print(f"  {issue}")

            # Validate compatibility
            compat = fm.get("compatibility", "")
            if compat:
                compat_issues = validate_compatibility(compat)
                all_issues.extend(compat_issues)
                for issue in compat_issues:
                    print(f"  {issue}")

            if not any("ERROR" in i or "WARNING" in i for i in all_issues if "frontmatter" not in i.lower()):
                print("  All frontmatter checks passed.")

        print("\n[3/3] Checking content quality...")
        # Check for backslash paths
        if "\\" in content and "\\n" not in content and "\\t" not in content:
            issue = "WARNING: Backslash paths detected. Use forward slashes for cross-platform compatibility."
            all_issues.append(issue)
            print(f"  {issue}")

        # Check for deeply nested references (references that link to other references)
        refs_dir = skill_dir / "references"
        if refs_dir.exists():
            for ref_file in refs_dir.glob("*.md"):
                try:
                    ref_content = ref_file.read_text()
                    ref_links = re.findall(r'\[([^\]]*)\]\(([^)]+\.md)\)', ref_content)
                    for _, link in ref_links:
                        if not link.startswith("http") and not link.startswith("#"):
                            issue = (f"WARNING: Nested reference in {ref_file.name} → {link}. "
                                     "Keep references one level deep from SKILL.md.")
                            all_issues.append(issue)
                            print(f"  {issue}")
                except Exception:
                    pass

    else:
        print("\n[2/3] Skipping frontmatter check (SKILL.md not found)")
        print("\n[3/3] Skipping content check (SKILL.md not found)")

    # Summary
    errors = [i for i in all_issues if i.startswith("ERROR")]
    warnings = [i for i in all_issues if i.startswith("WARNING")]

    print("\n" + "=" * 60)
    print(f"Results: {len(errors)} error(s), {len(warnings)} warning(s)")

    if errors:
        print("\nERRORS (must fix):")
        for e in errors:
            print(f"  {e}")

    if warnings:
        print("\nWARNINGS (recommended fixes):")
        for w in warnings:
            print(f"  {w}")

    if not errors and not warnings:
        print("\nSKILL VALID — All checks passed!")
        sys.exit(0)
    elif errors:
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
