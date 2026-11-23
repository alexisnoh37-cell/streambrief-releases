"""Allow only signed build-file delivery hosts; the ZIP digest is verified separately."""
import re
from urllib.parse import urlsplit


def validate_source(value):
    parsed=urlsplit(value)
    if parsed.scheme!='https' or parsed.username or parsed.password or parsed.port not in (None,443) or parsed.fragment:
        raise ValueError('Invalid verified build source')
    azure=bool(re.fullmatch(r'productionresults[a-z0-9]+\.blob\.core\.windows\.net',parsed.hostname or '')) and parsed.path.startswith('/actions-results/')
    github=parsed.hostname=='release-assets.githubusercontent.com' and parsed.path.startswith('/github-production-release-asset/1454701863/') and bool(parsed.query)
    if not (azure or github):raise ValueError('Unapproved verified build source')
    return parsed
