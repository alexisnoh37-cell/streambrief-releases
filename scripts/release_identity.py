"""Keep the public label while preserving older clients' numeric asset contract."""
import re
import shutil
from pathlib import Path


def prepare_compatible_update(folder,metadata,manifest):
    version=metadata['version'];display=metadata['display_version']
    if not isinstance(display,str) or len(display)>32 or not re.fullmatch(r'\d+\.\d+(?:\.\d+)?',display):raise ValueError('Invalid display label')
    if not re.fullmatch(r'(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)',version):raise ValueError('Invalid package version')
    major,minor,patch=map(int,version.split('.'))
    numeric=f'{major}.{patch:02d}' if minor==0 else version
    name=f'StreamBrief-{numeric}-Update.exe'
    if manifest.get('display_version',numeric)!=display:raise ValueError('Display label does not match verified metadata')
    canonical=f'StreamBrief-{display}-Update.exe';entry=metadata['files'][canonical]
    expected={'url':f"https://github.com/{metadata['distribution_repository']}/releases/download/v{version}/{name}",'size':entry['bytes'],'sha256':entry['sha256']}
    if manifest['update']!=expected:raise ValueError('Numeric update identity does not match the verified executable')
    if name!=canonical:shutil.copyfile(Path(folder)/canonical,Path(folder)/name)
    return name
