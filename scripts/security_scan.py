#!/usr/bin/env python3
"""
Security scanner for Agent Skills.

Scans all files in a skill directory for malicious patterns based on
the ToxicSkills threat model (Snyk, 2026): prompt injection, malicious code,
credential theft, security disablement, and data exfiltration.

Usage:
    python security_scan.py <path-to-skill-directory>

Exit codes:
    0 = SAFE    (score 0-1)
    1 = CAUTION (score 2-5)
    2 = DANGER  (score 6+)
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass, field

# ─── Finding Model ───────────────────────────────────────────────────────────

@dataclass
class Finding:
    category: str          # Threat category name
    severity: str          # DANGER, CAUTION, INFO
    weight: int            # Score weight
    file: str              # Relative file path
    line_num: int          # Line number (1-based)
    line: str              # Matched line content (truncated)
    description: str       # Human-readable explanation
    pattern_name: str      # Which pattern matched


# ─── Pattern Definitions ─────────────────────────────────────────────────────
# Each pattern: (name, regex, weight, category, severity, description)

PROMPT_INJECTION_PATTERNS = [
    ("role-override", r"(?i)(you are (now |in )?|switch to |enter )(developer|admin|debug|test|unsafe|unrestricted)\s*(mode)?",
     3, "Prompt Injection", "DANGER",
     "Attempts to override the agent's role or safety mode"),
    ("ignore-instructions", r"(?i)(ignore|disregard|forget|override|bypass)\s+(previous|prior|above|safety|security)\s+(instructions?|rules?|guidelines?|warnings?|protocols?|checks?)",
     3, "Prompt Injection", "DANGER",
     "Instructs agent to ignore safety mechanisms"),
    ("suppress-warnings", r"(?i)(security|safety)\s+(warnings?|alerts?|checks?)\s+(are|is)\s+(test|fake|artifact|disabled|not needed)",
     3, "Prompt Injection", "DANGER",
     "Attempts to suppress security warnings"),
    ("pre-approved", r"(?i)(already|pre-?)\s*(approved|consented|authorized|verified)",
     2, "Prompt Injection", "CAUTION",
     "Claims pre-approval to bypass consent checks"),
    ("new-instructions", r"(?i)your (new|updated|real|actual) instructions (are|follow)",
     3, "Prompt Injection", "DANGER",
     "Attempts to inject new base instructions"),
]

MALICIOUS_CODE_PATTERNS = [
    ("curl-pipe-bash", r"curl\s+.*\|\s*(ba)?sh",
     6, "Malicious Code", "DANGER",
     "Downloads and immediately executes remote code"),
    ("wget-execute", r"wget\s+.*&&\s*(chmod\s+\+x|\.\/|bash|sh|python)",
     6, "Malicious Code", "DANGER",
     "Downloads a file and executes it"),
    ("base64-exec", r"(exec|eval)\s*\(\s*(base64|b64decode|bytes\.fromhex)",
     5, "Malicious Code", "DANGER",
     "Executes obfuscated/encoded code"),
    ("python-exec-decode", r"exec\s*\(.*decode\s*\(",
     5, "Malicious Code", "DANGER",
     "Decodes and executes hidden code"),
    ("eval-dynamic", r"eval\s*\([^)]*\b(var|input|arg|param|data|response|result)\b",
     4, "Malicious Code", "DANGER",
     "Evaluates dynamic/untrusted input"),
    ("import-os-system", r"__import__\s*\(\s*['\"]os['\"]\s*\)\s*\.\s*system",
     5, "Malicious Code", "DANGER",
     "Hidden OS command execution via dynamic import"),
    ("sudo-command", r"\bsudo\s+",
     3, "Malicious Code", "CAUTION",
     "Uses elevated privileges (sudo)"),
    ("chmod-broad", r"chmod\s+(777|a\+[rwx]|u\+s|\+s)",
     3, "Malicious Code", "CAUTION",
     "Sets overly permissive or setuid file permissions"),
    ("password-archive", r"(unzip|7z|tar)\s+.*-[pP]\s*\S+",
     4, "Malicious Code", "DANGER",
     "Uses password-protected archive (common malware evasion)"),
    ("nohup-background", r"(nohup|disown)\s+",
     2, "Malicious Code", "CAUTION",
     "Runs background process that persists after session"),
]

CREDENTIAL_THEFT_PATTERNS = [
    ("aws-creds", r"(\.aws/credentials|\.aws/config|AWS_SECRET_ACCESS_KEY|AWS_ACCESS_KEY_ID)",
     4, "Credential Theft", "DANGER",
     "Accesses AWS credential files or environment variables"),
    ("ssh-keys", r"(\.ssh/id_rsa|\.ssh/id_ed25519|\.ssh/id_dsa|\.ssh/authorized_keys)",
     4, "Credential Theft", "DANGER",
     "Accesses SSH private keys"),
    ("gnupg", r"\.gnupg/",
     3, "Credential Theft", "CAUTION",
     "Accesses GPG keyring directory"),
    ("dotenv-access", r"(cat|read|open|load)\s*.*\.(env|env\.local|env\.production|env\.development)",
     3, "Credential Theft", "CAUTION",
     "Reads .env files which typically contain secrets"),
    ("docker-config", r"\.docker/config\.json",
     3, "Credential Theft", "CAUTION",
     "Accesses Docker registry credentials"),
    ("kube-config", r"\.kube/config",
     3, "Credential Theft", "CAUTION",
     "Accesses Kubernetes cluster credentials"),
    ("npm-pypi-rc", r"\.(npmrc|pypirc)",
     3, "Credential Theft", "CAUTION",
     "Accesses package registry authentication"),
    ("gh-hosts", r"\.config/gh/hosts\.yml",
     3, "Credential Theft", "CAUTION",
     "Accesses GitHub CLI authentication tokens"),
    ("env-harvesting", r"(printenv|env\s*\||\$\(env\))\s*.*>(>)?",
     4, "Credential Theft", "DANGER",
     "Dumps all environment variables (likely exfiltration)"),
    ("hardcoded-key-pattern", r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|bearer)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{20,}['\"]",
     2, "Credential Theft", "CAUTION",
     "Contains hardcoded secret or API key"),
]

SECURITY_DISABLE_PATTERNS = [
    ("ssl-verify-off", r"(?i)(ssl[_-]?verify|verify[_-]?ssl)\s*[:=]\s*(false|0|no|off)",
     4, "Security Disablement", "DANGER",
     "Disables SSL/TLS certificate verification"),
    ("git-ssl-off", r"http\.sslVerify\s+false",
     4, "Security Disablement", "DANGER",
     "Disables Git SSL verification"),
    ("history-clear", r"(history\s+-c|rm\s+.*\.bash_history|>\s*/var/log/)",
     4, "Security Disablement", "DANGER",
     "Clears command history or logs (covering tracks)"),
    ("crontab-inject", r"(crontab|/var/spool/cron)",
     3, "Security Disablement", "CAUTION",
     "Modifies scheduled tasks (potential persistence)"),
    ("shell-profile-modify", r"(>>?\s*~/?\.(bashrc|zshrc|profile|bash_profile|zprofile))",
     4, "Security Disablement", "DANGER",
     "Modifies shell profile (persistent backdoor)"),
    ("firewall-disable", r"(ufw\s+disable|iptables\s+-F)",
     4, "Security Disablement", "DANGER",
     "Disables system firewall"),
]

EXFILTRATION_PATTERNS = [
    ("curl-post-data", r"curl\s+.*-[dX]\s*POST.*\$\(",
     3, "Data Exfiltration", "DANGER",
     "Sends local data via HTTP POST to external server"),
    ("wget-post", r"wget\s+--post-(data|file)",
     3, "Data Exfiltration", "DANGER",
     "Sends local data via wget POST"),
    ("dns-exfil", r"(nslookup|dig)\s+.*\$\(",
     4, "Data Exfiltration", "DANGER",
     "DNS-based data exfiltration (encodes data in DNS queries)"),
    ("python-urllib-post", r"urllib\.request\.(urlopen|Request)\s*\(.*data\s*=",
     2, "Data Exfiltration", "CAUTION",
     "Python HTTP POST — check if destination is legitimate"),
    ("requests-post-env", r"requests\.(post|put)\s*\(.*os\.environ",
     4, "Data Exfiltration", "DANGER",
     "Sends environment variables to external server"),
    ("base64-encode-file", r"base64\.(b64)?encode\s*\(.*open\s*\(",
     3, "Data Exfiltration", "CAUTION",
     "Base64-encodes file contents — check what file and why"),
]

TOOL_PERMISSION_PATTERNS = [
    ("broad-bash", r"allowed-tools\s*:.*Bash\s*\(\s*\*\s*\)",
     1, "Overly Broad Permissions", "CAUTION",
     "Skill requests unrestricted shell access"),
    ("all-tools", r"allowed-tools\s*:.*\*\s*$",
     1, "Overly Broad Permissions", "CAUTION",
     "Skill requests access to all tools"),
]

ALL_PATTERNS = (
    PROMPT_INJECTION_PATTERNS +
    MALICIOUS_CODE_PATTERNS +
    CREDENTIAL_THEFT_PATTERNS +
    SECURITY_DISABLE_PATTERNS +
    EXFILTRATION_PATTERNS +
    TOOL_PERMISSION_PATTERNS
)

# ─── Known Safe Domains ─────────────────────────────────────────────────────

KNOWN_SAFE_DOMAINS = {
    "github.com", "raw.githubusercontent.com",
    "pypi.org", "files.pythonhosted.org",
    "npmjs.com", "registry.npmjs.org",
    "npmjs.org", "yarnpkg.com",
    "anthropic.com", "claude.ai", "code.claude.com",
    "agentskills.io", "skillhub.club", "www.skillhub.club",
    "api.github.com", "objects.githubusercontent.com",
    # Documentation example domains (RFC 2606)
    "example.com", "example.org", "example.net",
}

# Domains that appear in security documentation as attacker examples.
# These are flagged as INFO, not DANGER, when found in .md files.
KNOWN_EXAMPLE_ATTACKER_DOMAINS = {
    "evil.com", "attacker.com", "malicious.com",
}

# ─── Scanner ─────────────────────────────────────────────────────────────────

def _is_in_code_fence(lines: list[str], target_line: int) -> bool:
    """Check if a line (0-based index) is inside a markdown code fence.
    Patterns inside code fences are documentation examples, not real threats."""
    in_fence = False
    for i in range(target_line):
        stripped = lines[i].strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
    return in_fence


def _is_in_blockquote(line: str) -> bool:
    """Check if a line is a markdown blockquote (example/documentation)."""
    return line.strip().startswith(">")


def _is_in_regex_literal(line: str) -> bool:
    """Check if the match is inside a regex pattern definition (r'...' or r\"...\")."""
    return bool(re.search(r'''r['"].*['"]''', line))


def scan_file(file_path: Path, skill_dir: Path) -> list[Finding]:
    """Scan a single file for malicious patterns.
    Skips patterns found inside markdown code fences, blockquotes,
    and regex literals (documentation examples, not real threats).
    For non-markdown files (.py, .sh, etc.), all patterns are checked."""
    findings = []
    rel_path = str(file_path.relative_to(skill_dir))
    is_markdown = file_path.suffix.lower() == ".md"
    is_python = file_path.suffix.lower() == ".py"

    try:
        content = file_path.read_text(errors="replace")
    except Exception:
        return findings

    lines = content.split("\n")

    for line_num_1based, line in enumerate(lines, 1):
        line_idx = line_num_1based - 1

        # Skip documentation examples in markdown files
        if is_markdown:
            if _is_in_code_fence(lines, line_idx):
                continue
            if _is_in_blockquote(line):
                continue

        # Skip regex pattern definitions in Python files (the scanner's own patterns)
        if is_python and _is_in_regex_literal(line):
            continue

        for name, pattern, weight, category, severity, description in ALL_PATTERNS:
            if re.search(pattern, line):
                findings.append(Finding(
                    category=category,
                    severity=severity,
                    weight=weight,
                    file=rel_path,
                    line_num=line_num_1based,
                    line=line.strip()[:200],
                    description=description,
                    pattern_name=name,
                ))

    return findings


def check_urls(file_path: Path, skill_dir: Path) -> list[Finding]:
    """Extract URLs and flag unknown domains."""
    findings = []
    rel_path = str(file_path.relative_to(skill_dir))

    try:
        content = file_path.read_text(errors="replace")
    except Exception:
        return findings

    url_pattern = re.compile(r'https?://([a-zA-Z0-9.-]+)')

    for line_num, line in enumerate(content.split("\n"), 1):
        for match in url_pattern.finditer(line):
            domain = match.group(1).lower()
            # Strip port
            domain = domain.split(":")[0]

            if domain not in KNOWN_SAFE_DOMAINS and not domain.endswith(".gov"):
                findings.append(Finding(
                    category="External URL",
                    severity="INFO",
                    weight=1,
                    file=rel_path,
                    line_num=line_num,
                    line=line.strip()[:200],
                    description=f"External URL to {domain} — verify this domain is legitimate and necessary",
                    pattern_name="unknown-url",
                ))

    return findings


def check_hidden_files(skill_dir: Path) -> list[Finding]:
    """Check for hidden/dotfiles in the skill directory."""
    findings = []
    for item in skill_dir.rglob("*"):
        if item.name.startswith(".") and item.name not in (".gitkeep", ".gitignore"):
            findings.append(Finding(
                category="Hidden Files",
                severity="CAUTION",
                weight=1,
                file=str(item.relative_to(skill_dir)),
                line_num=0,
                line="",
                description=f"Hidden file '{item.name}' — could conceal malicious content",
                pattern_name="hidden-file",
            ))
    return findings


def check_encoding_tricks(file_path: Path, skill_dir: Path) -> list[Finding]:
    """Check for encoding-based obfuscation."""
    findings = []
    rel_path = str(file_path.relative_to(skill_dir))

    try:
        content_bytes = file_path.read_bytes()
    except Exception:
        return findings

    # Zero-width characters
    zero_width = [b'\xe2\x80\x8b', b'\xe2\x80\x8c', b'\xe2\x80\x8d', b'\xef\xbb\xbf']
    for zw in zero_width:
        if zw in content_bytes:
            findings.append(Finding(
                category="Encoding Tricks",
                severity="CAUTION",
                weight=2,
                file=rel_path,
                line_num=0,
                line="(binary content)",
                description="Zero-width Unicode characters detected — may hide instructions from human review",
                pattern_name="zero-width-chars",
            ))
            break

    # Extremely long lines (push content off-screen)
    try:
        content = content_bytes.decode(errors="replace")
        for line_num, line in enumerate(content.split("\n"), 1):
            if len(line) > 1000:
                findings.append(Finding(
                    category="Encoding Tricks",
                    severity="CAUTION",
                    weight=1,
                    file=rel_path,
                    line_num=line_num,
                    line=f"(line is {len(line)} chars — truncated)",
                    description="Extremely long line may hide malicious content off-screen",
                    pattern_name="long-line",
                ))
    except Exception:
        pass

    return findings


def scan_skill(skill_dir: Path) -> list[Finding]:
    """Scan all files in a skill directory."""
    all_findings = []

    # Check hidden files
    all_findings.extend(check_hidden_files(skill_dir))

    # Scan each file
    text_extensions = {
        ".md", ".txt", ".py", ".sh", ".bash", ".js", ".ts",
        ".yaml", ".yml", ".json", ".toml", ".cfg", ".ini",
        ".html", ".css", ".jsx", ".tsx", ".rb", ".go",
        ".rs", ".java", ".c", ".cpp", ".h", ".hpp",
    }

    for file_path in skill_dir.rglob("*"):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() in text_extensions or file_path.name == "SKILL.md":
            all_findings.extend(scan_file(file_path, skill_dir))
            all_findings.extend(check_urls(file_path, skill_dir))
            all_findings.extend(check_encoding_tricks(file_path, skill_dir))

    return all_findings


def calculate_score(findings: list[Finding]) -> int:
    """Calculate total risk score from findings.
    INFO-level findings do NOT contribute to the risk score —
    they're informational only (e.g., unknown URLs in documentation)."""
    seen = set()
    total = 0
    for f in findings:
        if f.severity == "INFO":
            continue
        key = (f.pattern_name, f.file, f.line_num)
        if key not in seen:
            seen.add(key)
            total += f.weight
    return total


def main():
    if len(sys.argv) < 2:
        print("Usage: python security_scan.py <path-to-skill-directory>")
        print("  Scans an Agent Skill for malicious patterns.")
        sys.exit(1)

    skill_dir = Path(sys.argv[1]).resolve()

    if not skill_dir.is_dir():
        print(f"ERROR: {skill_dir} is not a directory")
        sys.exit(1)

    print(f"Security scan: {skill_dir.name}")
    print("=" * 60)
    print("Threat model: ToxicSkills (Snyk, 2026)")
    print("Categories: Prompt Injection, Malicious Code, Credential Theft,")
    print("            Security Disablement, Data Exfiltration")
    print("=" * 60)

    # Count files
    all_files = list(skill_dir.rglob("*"))
    file_count = sum(1 for f in all_files if f.is_file())
    print(f"\nScanning {file_count} files...\n")

    findings = scan_skill(skill_dir)
    score = calculate_score(findings)

    # Group by severity
    danger = [f for f in findings if f.severity == "DANGER"]
    caution = [f for f in findings if f.severity == "CAUTION"]
    info = [f for f in findings if f.severity == "INFO"]

    if danger:
        print("DANGER FINDINGS (block installation):")
        print("-" * 40)
        for f in danger:
            print(f"  [{f.category}] {f.file}:{f.line_num}")
            print(f"    Pattern: {f.pattern_name}")
            print(f"    Line: {f.line}")
            print(f"    Risk: {f.description}")
            print()

    if caution:
        print("CAUTION FINDINGS (require user approval):")
        print("-" * 40)
        for f in caution:
            print(f"  [{f.category}] {f.file}:{f.line_num}")
            print(f"    Pattern: {f.pattern_name}")
            print(f"    Line: {f.line}")
            print(f"    Risk: {f.description}")
            print()

    if info:
        print(f"INFO ({len(info)} items):")
        print("-" * 40)
        for f in info:
            print(f"  [{f.category}] {f.file}:{f.line_num} — {f.description}")
        print()

    # Rating
    print("=" * 60)
    if score >= 6:
        rating = "DANGER"
        symbol = "!!!"
        action = "BLOCK — Do NOT install this skill."
        exit_code = 2
    elif score >= 2:
        rating = "CAUTION"
        symbol = "(!)"
        action = "REVIEW each finding. Get explicit user approval before installing."
        exit_code = 1
    else:
        rating = "SAFE"
        symbol = "[OK]"
        action = "No threats detected. Safe to install."
        exit_code = 0

    print(f"\n  {symbol} Rating: {rating} (score: {score})")
    print(f"  Action: {action}")
    print(f"\n  Findings: {len(danger)} danger, {len(caution)} caution, {len(info)} info")
    print("=" * 60)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
