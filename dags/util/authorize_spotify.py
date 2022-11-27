import requests
from dotenv import load_dotenv
import os
import base64


def _encode_auth_header(client_id, client_secret):
    string = f"{client_id}:{client_secret}"
    string_bytes = string.encode("ascii")
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


def authorize_spotify():
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    auth_header = _encode_auth_header(client_id, client_secret)

    authorize_response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={"grant_type": "client_credentials"},
    )

    try:
        return authorize_response.json()["access_token"]
    except KeyError:
        print("Failed to authenticate with Spotify.")
        return ""
