"""Portable package/Skill structure checks; never invokes a model or registry."""
import json
from pathlib import Path
import re
import sys

try:
    import yaml
except ImportError:
    print("PyYAML is required. Use configure-subagents/requirements.txt in a virtual environment.", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "configure-subagents"


def check():
    errors = []
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        errors.append("SKILL.md must begin with YAML frontmatter.")
    else:
        data = yaml.safe_load(match.group(1))
        if not isinstance(data, dict):
            errors.append("Skill frontmatter must be a mapping.")
        else:
            name = data.get("name")
            description = data.get("description")
            if name != SKILL.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(name)):
                errors.append("Skill name must match the kebab-case package folder.")
            if not isinstance(description, str) or not description.strip() or len(description) > 1024:
                errors.append("Skill description must be non-empty and at most 1024 characters.")
        if not text[match.end():].strip():
            errors.append("Skill instructions are empty.")

    docs = sorted(SKILL.rglob("*.md")) + [ROOT / "README.md"]
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    package_name = re.escape(package["name"].split("/")[-1])
    for doc in docs:
        if not doc.is_file():
            errors.append(f"Missing document: {doc.relative_to(ROOT)}")
            continue
        content = doc.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            resolved = (doc.parent / target.split("#", 1)[0]).resolve()
            if not resolved.is_relative_to(ROOT) or not resolved.is_file():
                errors.append(f"Broken or external local reference: {doc.relative_to(ROOT)} -> {target}")
        if re.search(r"\[TODO:[^\]]*\]", content):
            errors.append(f"Unfinished scaffold in {doc.relative_to(ROOT)}")
        # Keep download-and-execute instructions out of the agent-facing Skill.
        # Human-facing release instructions use the verified maintainer's scope.
        if doc.is_relative_to(SKILL) and re.search(rf"\b(?:npx|npm\s+exec)\b[^\r\n]*{package_name}", content):
            errors.append(f"Registry execution instruction in agent-facing document {doc.relative_to(ROOT)}")

    if (ROOT / "LICENSE").read_bytes() != (SKILL / "LICENSE").read_bytes():
        errors.append("Installed Skill license must match the package license.")
    return errors


if __name__ == "__main__":
    try:
        failures = check()
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Structure check unavailable: {exc}", file=sys.stderr)
        sys.exit(2)
    for failure in failures:
        print(failure, file=sys.stderr)
    if failures:
        sys.exit(1)
    print("Skill metadata, local references, licenses, and agent-facing installation boundaries passed.")
