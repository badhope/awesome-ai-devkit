"""Release pre-check: validation repo completeness before creating a GitHub Release."""
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    root = ROOT

    # 1. LICENSE present
    license_files = list(root.glob('LICENSE*'))
    if not license_files:
        errors.append('LICENSE 文件缺失')
    else:
        print(f'✓ LICENSE 文件存在: {license_files[0].name}')

    # 2. README (EN + ZH) complete and non-trivial
    for name in ('README.md', 'README_zh.md'):
        f = root / name
        if not f.exists():
            errors.append(f'{name} 缺失')
        elif f.stat().st_size < 1000:
            warnings.append(f'{name} 内容偏少 ({f.stat().st_size} bytes)')
        else:
            print(f'✓ {name} ({f.stat().st_size} bytes)')

    # 3. CHANGELOG format
    changelog = root / 'CHANGELOG.md'
    if not changelog.exists():
        warnings.append('CHANGELOG.md 缺失')
    else:
        content = changelog.read_text(encoding='utf-8')
        if '[Unreleased]' not in content and not re.search(r'## \[\d+\.\d+\.\d+\]', content):
            warnings.append('CHANGELOG.md 格式不规范 (缺少版本标题)')
        else:
            print('✓ CHANGELOG.md 格式正确')

    # 4. Required directories
    required_dirs = [
        'framework/agents',
        'framework/skills',
        'scenarios/programming/fullstack/scaffolds',
        'scenarios/programming/fullstack/hooks',
    ]
    for d in required_dirs:
        if not (root / d).exists():
            errors.append(f'必要目录缺失: {d}')
        else:
            print(f'✓ {d}')

    # 5. Core config files
    for f in ['.env.example', '.gitignore', 'hooks/config.yaml']:
        if not (root / f).exists():
            warnings.append(f'配置缺失: {f}')
        else:
            print(f'✓ {f}')

    print()
    print('=' * 50)
    print('发布前验收结果')
    print(f'  错误:   {len(errors)}')
    print(f'  警告:   {len(warnings)}')
    print('=' * 50)

    if warnings:
        print()
        print('警告项:')
        for w in warnings:
            print(f'  ⚠ {w}')

    if errors:
        print()
        print('验收失败，阻止发布:')
        for e in errors:
            print(f'  ✗ {e}')
        return 1

    print()
    print('✓ 发布前验收通过')
    return 0


if __name__ == '__main__':
    sys.exit(main())