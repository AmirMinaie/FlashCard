from pathlib import Path
import re

VERSION_FILE = Path("app/version.py")

text = VERSION_FILE.read_text(encoding="utf-8")

match = re.search(
    r'VERSION\s*=\s*"(\d+)\.(\d+)\.(\d+)"',
    text
)

if not match:
    raise RuntimeError("VERSION not found")

major, minor, patch = map(int, match.groups())

patch += 1

new_version = f"{major}.{minor}.{patch}"

text = re.sub(
    r'VERSION\s*=\s*"\d+\.\d+\.\d+"',
    f'VERSION = "{new_version}"',
    text
)

VERSION_FILE.write_text(text, encoding="utf-8")

print(f"Version bumped to {new_version}")