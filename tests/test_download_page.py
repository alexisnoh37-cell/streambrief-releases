import copy
import unittest

from scripts.build_download_page import REPOSITORY, release_values, render


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
        self.assertIn('Windows 설치용 파일 받기', page)
        self.assertIn('Windows 업데이트용 파일 받기', page)
        self.assertIn('이미 설치하셨나요?', page)
        self.assertIn('전체 사용자의 날짜별 기록 실행·오류 횟수 합계만', page)
        self.assertIn('약 791 MB', page)
        self.assertIn('약 62 MB', page)
        self.assertNotIn('<span class="preview">', page)
        self.assertLess(page.index('<aside class="privacy-strip"'), page.index('<div class="quick-links"'))

    def test_next_release_updates_every_versioned_link_and_label(self):
        page = render(release('1.0.12', '1.12'))
        self.assertNotIn('1.0.11', page)
        self.assertNotIn('1.11', page)
        self.assertIn('최신 버전 1.12', page)
        for name in ['StreamBrief-1.12-Setup.exe', 'StreamBrief-1.12-Update.exe',
                     'StreamBrief-User-Guide.html', 'StreamBrief-Quick-Guide-60s.mp4']:
            self.assertIn(f'/download/v1.0.12/{name}', page)

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
