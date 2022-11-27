import requests
import datetime
from uuid import uuid4


def _fetch_tracks(playlist, playlist_id, auth_token, date, job_id, playlist_job_id):
    resp = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    try:
        tracks = []

        for i, t in enumerate(resp.json()["tracks"]["items"]):
            tracks.append(
                {
                    "id": uuid4(),
                    "track_id": t["track"]["id"],
                    "name": t["track"]["name"],
                    "artists": list(
                        map(lambda artist: artist["name"], t["track"]["artists"])
                    ),
                    "album": t["track"]["name"],
                    "popularity": t["track"]["popularity"],
                    "duration_ms": t["track"]["duration_ms"],
                    "position": i + 1,
                    "playlist": playlist,
                    "date": date,
                    "job_id": job_id,
                    "playlist_job_id": playlist_job_id,
                }
            )

        return tracks

    except KeyError:
        print("Failed to parse top tracks.")
        return


def get_top_songs(auth_token):
    playlists = {"us": "37i9dQZEVXbLRQDuF5jeBp", "global": "37i9dQZEVXbMDoHDwVN2tF"}
    today = str(datetime.datetime.utcnow()).split(" ")[0]
    job_id = uuid4()

    charts = []

    for playlist in playlists.keys():
        charts.append(
            _fetch_tracks(
                playlist=playlist,
                playlist_id=playlists[playlist],
                auth_token=auth_token,
                date=today,
                job_id=job_id,
                playlist_job_id=uuid4(),
            )
        )

    return charts
