"""Maintainer-only: capture pinned public Skill bytes; never runs package code.

Review changes to both fixtures and bundled fingerprints before committing.
Normal tests and the installer/update commands never access the registry.
"""
import base64
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
from urllib.parse import quote, urlparse
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
RELEASES = [
    ("configure-subagents", "0.1.0-alpha.1"),
    ("@woody_s/configure-subagents", "0.1.0-alpha.2"),
    ("@woody_s/configure-subagents", "0.1.0-alpha.4"),
    ("@woody_s/configure-subagents", "0.1.0-alpha.5"),
]


def capture():
    manifests, fixtures = [], []
    for package, version in RELEASES:
        with urlopen(f"https://registry.npmjs.org/{quote(package, safe='')}/{version}", timeout=30) as response:
            metadata = json.load(response)
        assert (metadata["name"], metadata["version"]) == (package, version)
        dist = metadata["dist"]
        url = urlparse(dist["tarball"])
        assert url.scheme == "https" and url.hostname == "registry.npmjs.org"
        with urlopen(dist["tarball"], timeout=30) as response:
            archive = response.read()
        integrity = "sha512-" + base64.b64encode(hashlib.sha512(archive).digest()).decode()
        assert integrity == dist["integrity"]
        files = {}
        with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
            for member in tar:
                prefix = "package/configure-subagents/"
                if not member.name.startswith(prefix):
                    continue
                relative = member.name[len(prefix):]
                assert member.isfile() and relative and ".." not in PurePosixPath(relative).parts
                assert not PurePosixPath(relative).is_absolute() and "\\" not in relative
                assert relative not in files
                files[relative] = tar.extractfile(member).read()
        assert "SKILL.md" in files
        provenance = {"package": package, "version": version, "integrity": integrity}
        manifests.append({**provenance, "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())}})
        fixtures.append({**provenance, "files": {name: base64.b64encode(data).decode() for name, data in sorted(files.items())}})
    for target, data in [(ROOT / "lib/released-skills.json", manifests), (ROOT / "tests/fixtures/released-skills.json", fixtures)]:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Captured {len(manifests)} integrity-verified release payloads.")


if __name__ == "__main__":
    capture()
