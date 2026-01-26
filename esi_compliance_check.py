#!/usr/bin/env python3
"""
EVE ESI Compliance Checker

Scans a project directory for ESI integration patterns and checks compliance
with CCP's Terms of Service and best practices.

Usage:
    python esi_compliance_check.py /path/to/project
    python esi_compliance_check.py /path/to/project --verbose
    python esi_compliance_check.py /path/to/project --fix
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional


class Severity(Enum):
    CRITICAL = "CRITICAL"  # Bannable offense
    WARNING = "WARNING"    # Best practice violation
    INFO = "INFO"          # Suggestion


@dataclass
class Finding:
    severity: Severity
    message: str
    file: Optional[Path] = None
    line: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ComplianceReport:
    findings: List[Finding] = field(default_factory=list)
    files_scanned: int = 0
    esi_usage_detected: bool = False
    image_server_usage: bool = False
    sso_usage: bool = False

    @property
    def score(self) -> int:
        """Calculate compliance score 0-100."""
        if not self.esi_usage_detected and not self.image_server_usage:
            return 100  # No ESI usage, no violations possible

        critical = sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
        warnings = sum(1 for f in self.findings if f.severity == Severity.WARNING)

        score = 100 - (critical * 25) - (warnings * 5)
        return max(0, score)

    @property
    def grade(self) -> str:
        score = self.score
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"


# Patterns to check
PATTERNS = {
    # ESI Base URLs
    "esi_url": re.compile(r'esi\.evetech\.net|esi\.tech\.ccp\.is'),

    # Image server
    "image_server": re.compile(r'images\.evetech\.net|image\.eveonline\.com'),

    # SSO
    "sso_url": re.compile(r'login\.eveonline\.com'),

    # User-Agent header
    "user_agent_set": re.compile(r'["\']User-Agent["\']|user.?agent|UserAgent', re.IGNORECASE),

    # Cache header handling
    "cache_handling": re.compile(r'Expires|Cache-Control|ETag|If-None-Match', re.IGNORECASE),

    # Error limit handling
    "error_limit": re.compile(r'X-ESI-Error-Limit|error.?limit|420', re.IGNORECASE),

    # Discovery patterns (BAD)
    "discovery_loop": re.compile(r'for.*in.*range.*get.*character|for.*in.*range.*get.*corporation', re.IGNORECASE),
    "search_abuse": re.compile(r'/search/.*strict=false.*categories=character', re.IGNORECASE),

    # Rate limiting
    "rate_limit": re.compile(r'rate.?limit|throttle|sleep|asyncio\.sleep|time\.sleep', re.IGNORECASE),

    # Versioned endpoints
    "versioned_endpoint": re.compile(r'/v\d+/|/latest/|/dev/|/legacy/'),
    "unversioned_endpoint": re.compile(r'esi\.evetech\.net/[a-z]+/[a-z]+'),

    # Token storage (potential issue)
    "plaintext_token": re.compile(r'access_token\s*=\s*["\'][^"\']+["\']'),
    "hardcoded_secret": re.compile(r'client_secret\s*=\s*["\'][^"\']+["\']'),
}


def scan_file(filepath: Path) -> List[Finding]:
    """Scan a single file for compliance issues."""
    findings = []

    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        lines = content.split('\n')
    except Exception as e:
        return [Finding(Severity.INFO, f"Could not read file: {e}", filepath)]

    # Check for ESI usage
    if not PATTERNS["esi_url"].search(content):
        return []  # No ESI usage in this file

    # Check for User-Agent header
    if not PATTERNS["user_agent_set"].search(content):
        findings.append(Finding(
            Severity.WARNING,
            "ESI usage detected but no User-Agent header found",
            filepath,
            suggestion="Add User-Agent header: 'User-Agent': 'YourApp/1.0 (contact@email.com)'"
        ))

    # Check for cache header handling
    if not PATTERNS["cache_handling"].search(content):
        findings.append(Finding(
            Severity.WARNING,
            "No cache header handling detected",
            filepath,
            suggestion="Respect ESI's Expires header to avoid unnecessary requests"
        ))

    # Check for error limit handling
    if not PATTERNS["error_limit"].search(content):
        findings.append(Finding(
            Severity.WARNING,
            "No error limit handling detected",
            filepath,
            suggestion="Monitor X-ESI-Error-Limit-Remain header to avoid bans"
        ))

    # Check for discovery abuse patterns
    for i, line in enumerate(lines, 1):
        if PATTERNS["discovery_loop"].search(line):
            findings.append(Finding(
                Severity.CRITICAL,
                "Potential discovery abuse pattern detected",
                filepath,
                i,
                "Iterating over IDs to discover entities is against TOS"
            ))

        if PATTERNS["search_abuse"].search(line):
            findings.append(Finding(
                Severity.CRITICAL,
                "Potential search endpoint abuse",
                filepath,
                i,
                "Using search to discover entities is bannable"
            ))

        if PATTERNS["hardcoded_secret"].search(line):
            findings.append(Finding(
                Severity.CRITICAL,
                "Hardcoded client secret detected",
                filepath,
                i,
                "Move secrets to environment variables"
            ))

        if PATTERNS["plaintext_token"].search(line):
            findings.append(Finding(
                Severity.WARNING,
                "Potential plaintext token storage",
                filepath,
                i,
                "Consider encrypting stored tokens"
            ))

    # Check for rate limiting
    if not PATTERNS["rate_limit"].search(content):
        findings.append(Finding(
            Severity.INFO,
            "No rate limiting implementation detected",
            filepath,
            suggestion="Consider adding rate limiting for bulk operations"
        ))

    # Check for versioned endpoints
    if PATTERNS["unversioned_endpoint"].search(content) and not PATTERNS["versioned_endpoint"].search(content):
        findings.append(Finding(
            Severity.WARNING,
            "Unversioned ESI endpoints detected",
            filepath,
            suggestion="Use /latest/ or /v{n}/ prefixed endpoints for stability"
        ))

    return findings


def scan_project(project_path: Path, verbose: bool = False) -> ComplianceReport:
    """Scan entire project for ESI compliance."""
    report = ComplianceReport()

    # File extensions to scan
    extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cs', '.go', '.rs', '.rb', '.php'}

    # Also check config files
    config_files = {'package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pom.xml'}

    for filepath in project_path.rglob('*'):
        if filepath.is_file():
            if filepath.suffix in extensions or filepath.name in config_files:
                if verbose:
                    print(f"Scanning: {filepath}")

                report.files_scanned += 1

                try:
                    content = filepath.read_text(encoding='utf-8', errors='ignore')
                except Exception:
                    continue

                # Detect usage types
                if PATTERNS["esi_url"].search(content):
                    report.esi_usage_detected = True
                if PATTERNS["image_server"].search(content):
                    report.image_server_usage = True
                if PATTERNS["sso_url"].search(content):
                    report.sso_usage = True

                # Get findings
                findings = scan_file(filepath)
                report.findings.extend(findings)

    return report


def print_report(report: ComplianceReport, project_name: str):
    """Print formatted compliance report."""
    print("\n" + "=" * 60)
    print(f"  EVE ESI COMPLIANCE REPORT: {project_name}")
    print("=" * 60)

    print(f"\n📊 Score: {report.score}/100 (Grade: {report.grade})")
    print(f"📁 Files scanned: {report.files_scanned}")

    print("\n📋 Usage Detection:")
    print(f"   ESI API: {'✅ Yes' if report.esi_usage_detected else '❌ No'}")
    print(f"   Image Server: {'✅ Yes' if report.image_server_usage else '❌ No'}")
    print(f"   SSO Auth: {'✅ Yes' if report.sso_usage else '❌ No'}")

    if report.findings:
        print("\n🔍 Findings:")

        # Group by severity
        critical = [f for f in report.findings if f.severity == Severity.CRITICAL]
        warnings = [f for f in report.findings if f.severity == Severity.WARNING]
        info = [f for f in report.findings if f.severity == Severity.INFO]

        if critical:
            print(f"\n  🚨 CRITICAL ({len(critical)}):")
            for f in critical:
                loc = f"{f.file.name}:{f.line}" if f.line else str(f.file.name) if f.file else ""
                print(f"     [{loc}] {f.message}")
                if f.suggestion:
                    print(f"        → {f.suggestion}")

        if warnings:
            print(f"\n  ⚠️  WARNINGS ({len(warnings)}):")
            for f in warnings:
                loc = f"{f.file.name}:{f.line}" if f.line else str(f.file.name) if f.file else ""
                print(f"     [{loc}] {f.message}")
                if f.suggestion:
                    print(f"        → {f.suggestion}")

        if info:
            print(f"\n  ℹ️  INFO ({len(info)}):")
            for f in info:
                loc = f"{f.file.name}:{f.line}" if f.line else str(f.file.name) if f.file else ""
                print(f"     [{loc}] {f.message}")
                if f.suggestion:
                    print(f"        → {f.suggestion}")
    else:
        if report.esi_usage_detected:
            print("\n✅ No issues found!")
        else:
            print("\n📝 No ESI usage detected in this project")

    print("\n" + "-" * 60)
    print("  TOS Reminder: https://developers.eveonline.com/")
    print("  Never use ESI to discover structures/characters")
    print("-" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Check EVE ESI compliance")
    parser.add_argument("path", type=Path, help="Project directory to scan")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show files being scanned")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}")
        sys.exit(1)

    report = scan_project(args.path, args.verbose)

    if args.json:
        import json
        print(json.dumps({
            "score": report.score,
            "grade": report.grade,
            "files_scanned": report.files_scanned,
            "esi_usage": report.esi_usage_detected,
            "findings": [
                {
                    "severity": f.severity.value,
                    "message": f.message,
                    "file": str(f.file) if f.file else None,
                    "line": f.line,
                    "suggestion": f.suggestion
                }
                for f in report.findings
            ]
        }, indent=2))
    else:
        print_report(report, args.path.name)

    # Exit code based on findings
    critical_count = sum(1 for f in report.findings if f.severity == Severity.CRITICAL)
    sys.exit(1 if critical_count > 0 else 0)


if __name__ == "__main__":
    main()
