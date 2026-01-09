import requests
from urllib import parse

GOOGLE_CLIENT_ID = (
    "CLIENT-ID"
)
GOOGLE_SECRET = "SECRET"
REDIRECT_URI = "https://vertexaisearch.cloud.google.com/oauth-redirect"

def get_authorization_url() -> str:
    """Get authorization url."""
    base_url = "https://accounts.google.com/o/oauth2/auth?"
    scopes = ['https://www.googleapis.com/auth/userinfo.email','https://www.googleapis.com/auth/userinfo.profile','openid']
    params = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(scopes),
        "access_type": "offline",
        "include_granted_scopes": "true",
        "prompt": "consent",
    }
    return base_url + parse.urlencode(params)
auth_url = get_authorization_url()
print(auth_url)