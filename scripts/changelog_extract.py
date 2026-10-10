"""Extract a version section from CHANGELOG.md for release notes.

Usage: python3 scripts/changelog_extract.py <version>
Example: python3 scripts/changelog_extract.py 2.0.0
Prints the `## [v2.0.0]` / `## [2.0.0]` section up to the next `## ` heading.
"""
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) < 2:
        print('(missing version argument)')
        return 0
    version = sys.argv[1]
    changelog_path = ROOT / 'CHANGELOG.md'
    if not changelog_path.exists():
        print('(CHANGELOG.md 不存在)')
        return 0

    content = changelog_path.read_text(encoding='utf-8')
    pattern = re.compile(r'^## \[v?%s\].*$' % re.escape(version))
    lines = content.split('\n')

    start = -1
    for i, line in enumerate(lines):
        if pattern.match(line.strip()):
            start = i
            break

    if start == -1:
        print('(CHANGELOG 中未找到 v%s 的变更记录)' % version)
        return 0

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].strip().startswith('## '):
            end = i
            break

    section = '\n'.join(lines[start:end]).strip()
    print(section if section else '(v%s 的变更记录为空)' % version)
    return 0


if __name__ == '__main__':
    sys.exit(main())