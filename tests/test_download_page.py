import copy
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from scripts.build_download_page import REPOSITORY, ROOT, release_values, render, main


def release(version='1.0.11', display='1.11'):
    base = f'https://github.com/{REPOSITORY}/releases'
    names = [f'StreamBrief-{display}-Setup.exe', f'StreamBrief-{display}-Update.exe',
             'StreamBrief-User-Guide.html', 'StreamBrief-Quick-Guide-60s.mp4']
    return {'tag_name': 'v' + version, 'draft': False, 'prerelease': False,
            'html_url': f'{base}/tag/v{version}',
            'assets': [{'name': n, 'size': 828974113 if n.endswith('Setup.exe') else 64847255,
                        'browser_download_url': f'{base}/download/v{version}/{n}'} for n in names]}


class DownloadPageTests(unittest.TestCase):
    def test_current_release_keeps_approved_copy_and_distinct_actions(self):
        page = render(release())
        self.assertIn('최신 버전 1.11', page)
        self.assertIn('<script src="./metrics.js" defer></script>', page)
        self.assertIn('방문자 식별자 없이', page)
        self.assertIn('Windows 설치용 파일 받기', page)
        self.assertIn('Windows 업데이트용 파일 받기', page)
        self.assertIn('이미 설치하셨나요?', page)
        self.assertIn('전체 사용자의 날짜별 기록 실행·오류 횟수 합계만', page)
        self.assertIn('약 791 MB', page)
        self.assertIn('약 62 MB', page)
        self.assertNotIn('<span class="preview">', page)
        self.assertLess(page.index('<div class="quick-links"'), page.index('<aside class="privacy-strip"'))
        self.assertLess(page.index('<aside class="privacy-strip"'), page.index('<aside class="live-notice"'))

    def test_site_output_contains_the_statistics_script_referenced_by_the_page(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'release.json'
            source.write_text(json.dumps(release()), encoding='utf-8')
            output = root / 'site'
            with patch('sys.argv', ['build_download_page', '--release-json', str(source), '--output', str(output)]):
                main()
            self.assertEqual((output / 'metrics.js').read_bytes(), (ROOT / 'site' / 'metrics.js').read_bytes())
            self.assertIn('./metrics.js', (output / 'index.html').read_text(encoding='utf-8'))

    def test_next_release_updates_every_versioned_link_and_label(self):
        page = render(release('1.0.12', '1.12'))
        self.assertNotIn('1.0.11', page)
        self.assertNotIn('1.11', page)
        self.assertIn('최신 버전 1.12', page)
        for name in ['StreamBrief-1.12-Setup.exe', 'StreamBrief-1.12-Update.exe',
                     'StreamBrief-User-Guide.html', 'StreamBrief-Quick-Guide-60s.mp4']:
            self.assertIn(f'/download/v1.0.12/{name}', page)

    def test_refreshed_1_13_uses_new_tag_but_keeps_label_and_manual_download_names(self):
        data=release('1.0.15','1.13')
        data['assets'].append({'name':'StreamBrief-1.15-Update.exe','size':64847255,'browser_download_url':f'https://github.com/{REPOSITORY}/releases/download/v1.0.15/StreamBrief-1.15-Update.exe'})
        page=render(data)
        self.assertIn('최신 버전 1.13',page)
        self.assertNotIn('최신 버전 1.14',page)
        self.assertIn('/download/v1.0.15/StreamBrief-1.13-Setup.exe',page)
        self.assertIn('/download/v1.0.15/StreamBrief-1.13-Update.exe',page)
        self.assertNotIn('StreamBrief-1.15-Update.exe',page)
        self.assertIn('고정 높이의 스크롤 영역',page)
        self.assertIn('업데이트 버튼은 창 하단에 항상 표시',page)
        self.assertIn('Windows 알림',page)

    def test_incomplete_or_unpublished_release_cannot_replace_the_page(self):
        for change in ['draft', 'prerelease', 'missing_update', 'missing_video', 'duplicate_asset', 'bad_size']:
            with self.subTest(change=change):
                data = copy.deepcopy(release())
                if change in ['draft', 'prerelease']:
                    data[change] = True
                elif change == 'missing_update':
                    data['assets'].pop(1)
                elif change == 'missing_video':
                    data['assets'].pop()
                elif change == 'duplicate_asset':
                    data['assets'].append(data['assets'][0])
                elif change == 'bad_size':
                    data['assets'][0]['size'] = True
                with self.assertRaises(ValueError):
                    release_values(data)

    def test_unexpected_repositories_and_download_hosts_are_rejected(self):
        for host in ['http://github.com', 'https://example.invalid', 'https://github.com/other-owner']:
            data = release()
            data['assets'][1]['browser_download_url'] = data['assets'][1]['browser_download_url'].replace('https://github.com', host)
            with self.subTest(host=host), self.assertRaises(ValueError):
                render(data)
        data = release(); data['html_url'] = 'https://github.com/other-owner/repo/releases/tag/v1.0.11'
        with self.assertRaises(ValueError):
            render(data)


if __name__ == '__main__':
    unittest.main()
