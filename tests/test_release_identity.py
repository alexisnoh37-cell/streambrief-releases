import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.release_identity import prepare_compatible_update


class ReleaseIdentityTests(unittest.TestCase):
    def fixture(self,folder,version='1.0.14',display='1.13'):
        data=b'TEST verified executable';name=f'StreamBrief-{display}-Update.exe'
        (folder/name).write_bytes(data)
        entry={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
        metadata={'version':version,'display_version':display,'distribution_repository':'alexisnoh37-cell/streambrief-releases','files':{name:entry}}
        numeric='1.14' if version=='1.0.14' else display
        manifest={'display_version':display,'update':{'url':f'https://github.com/alexisnoh37-cell/streambrief-releases/releases/download/v{version}/StreamBrief-{numeric}-Update.exe','size':len(data),'sha256':entry['sha256']}}
        return metadata,manifest,data

    def test_refresh_keeps_1_13_download_and_creates_identical_numeric_updater(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);metadata,manifest,data=self.fixture(p)
            self.assertEqual(prepare_compatible_update(p,metadata,manifest),'StreamBrief-1.14-Update.exe')
            self.assertEqual((p/'StreamBrief-1.13-Update.exe').read_bytes(),data)
            self.assertEqual((p/'StreamBrief-1.14-Update.exe').read_bytes(),data)

    def test_ordinary_release_does_not_duplicate_an_asset(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);metadata,manifest,data=self.fixture(p,'1.0.13','1.13');manifest.pop('display_version')
            self.assertEqual(prepare_compatible_update(p,metadata,manifest),'StreamBrief-1.13-Update.exe')
            self.assertEqual(len(list(p.iterdir())),1)

    def test_inconsistent_label_url_or_digest_cannot_publish(self):
        for bad in ['label','url','digest']:
            with self.subTest(bad=bad),tempfile.TemporaryDirectory() as d:
                p=Path(d);metadata,manifest,data=self.fixture(p)
                if bad=='label':manifest['display_version']='1.99'
                elif bad=='url':manifest['update']['url']=manifest['update']['url'].replace('1.14-Update','1.13-Update')
                else:manifest['update']['sha256']='0'*64
                with self.assertRaises(ValueError):prepare_compatible_update(p,metadata,manifest)
