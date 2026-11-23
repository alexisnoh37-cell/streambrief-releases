import unittest
from scripts.distribution_source import validate_source


class SourceTests(unittest.TestCase):
    def test_only_verified_artifact_and_private_build_cdn_are_allowed(self):
        for value in ['https://productionresults123.blob.core.windows.net/actions-results/TEST/file.zip?sig=TEST',
                      'https://release-assets.githubusercontent.com/github-production-release-asset/1454701863/TEST?sig=TEST']:
            self.assertEqual(validate_source(value).scheme,'https')
        for value in ['http://release-assets.githubusercontent.com/github-production-release-asset/1454701863/TEST?sig=TEST',
                      'https://release-assets.githubusercontent.com/github-production-release-asset/999/TEST?sig=TEST',
                      'https://release-assets.githubusercontent.com/github-production-release-asset/1454701863/TEST',
                      'https://release-assets.githubusercontent.com:444/github-production-release-asset/1454701863/TEST?sig=TEST',
                      'https://user:pass@release-assets.githubusercontent.com/github-production-release-asset/1454701863/TEST?sig=TEST',
                      'https://github.com/other-owner/file.zip','https://example.invalid/file.zip',
                      'https://productionresults123.blob.core.windows.net/other/file.zip',
                      'https://release-assets.githubusercontent.com/github-production-release-asset/1454701863/TEST?sig=TEST#fragment']:
            with self.subTest(value=value),self.assertRaises(ValueError):validate_source(value)
