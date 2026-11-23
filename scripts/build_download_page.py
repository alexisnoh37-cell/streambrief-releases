"""Render the approved public download page from the latest verified release."""
import argparse
import html
import json
import re
from pathlib import Path

REPOSITORY = 'alexisnoh37-cell/streambrief-releases'
ROOT = Path(__file__).resolve().parent.parent


def release_values(release):
    if release.get('draft') or release.get('prerelease'):
        raise ValueError('A published stable release is required')
    tag = release.get('tag_name', '')
    if not re.fullmatch(r'v(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)', tag):
        raise ValueError('Invalid release version')
    base = f'https://github.com/{REPOSITORY}/releases'
    if release.get('html_url') != f'{base}/tag/{tag}':
        raise ValueError('Unexpected release repository')
    assets = release.get('assets', [])
    if not isinstance(assets, list) or not all(isinstance(a, dict) for a in assets):
        raise ValueError('Invalid release assets')
    names = [a.get('name') for a in assets]
    if not all(isinstance(n, str) for n in names) or len(set(names)) != len(names):
        raise ValueError('Duplicate or invalid assets')
    setups = [(a, re.fullmatch(r'StreamBrief-(\d+\.\d+(?:\.\d+)?)-Setup\.exe', a['name'])) for a in assets]
    setups = [(a, match) for a, match in setups if match]
    if len(setups) != 1:
        raise ValueError('Exactly one full installer is required')
    setup, match = setups[0]
    display = match.group(1)
    required = [setup['name'], f'StreamBrief-{display}-Update.exe', 'StreamBrief-User-Guide.html', 'StreamBrief-Quick-Guide-60s.mp4']
    by_name = {a['name']: a for a in assets}
    for name in required:
        asset = by_name.get(name)
        if not asset or asset.get('browser_download_url') != f'{base}/download/{tag}/{name}':
            raise ValueError(f'Missing or unexpected public download: {name}')
        size = asset.get('size')
        if type(size) is not int or size <= 0:
            raise ValueError(f'Invalid asset size: {name}')
    return {'PACKAGE_VERSION': tag[1:], 'DISPLAY_VERSION': display,
            'SETUP_MB': f"{setup['size'] / 1024**2:.0f}",
            'UPDATE_MB': f"{by_name[required[1]]['size'] / 1024**2:.0f}"}


def render(release):
    values = release_values(release)
    page = (ROOT / 'site' / 'index.template.html').read_text(encoding='utf-8')
    for name, value in values.items():
        page = page.replace(f'__{name}__', html.escape(value, quote=True))
    if re.search(r'__[A-Z_]+__', page):
        raise ValueError('Unresolved page placeholders')
    return page


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--release-json', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT / '_site')
    args = parser.parse_args()
    release = json.loads(args.release_json.read_text(encoding='utf-8-sig'))
    page = render(release)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'index.html').write_text(page, encoding='utf-8')
    (args.output / 'metrics.js').write_bytes((ROOT / 'site' / 'metrics.js').read_bytes())
    (args.output / '.nojekyll').write_text('', encoding='utf-8')
    print('Download page rendered for ' + release['tag_name'])


if __name__ == '__main__':
    main()
