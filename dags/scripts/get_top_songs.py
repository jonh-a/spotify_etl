import requests
import datetime
from uuid import uuid4
import psycopg2
import sql.create_tables
import sql.insert_top_tracks


def _fetch_tracks(playlist, playlist_id, auth_token, date, job_id, chart_id):
    resp = requests.get(
        f"https://api.spotify.com/v1/playlists/{playlist_id}",
        headers={"Authorization": f"Bearer {auth_token}"},
    )

    try:
        tracks = []

        for i, t in enumerate(resp.json()["tracks"]["items"]):
            tracks.append(
                {
                    "id": str(uuid4()),
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
                    "chart_id": chart_id,
                }
            )

        return tracks

    except KeyError:
        print("Failed to parse top tracks.")
        return


def _insert_job(date, job_id, cur, conn):
    cur.execute(sql.insert_top_tracks.insert_job, (date, job_id))
    conn.commit()


def _insert_chart(job_id, chart_id, playlist, cur, conn):
    cur.execute(sql.insert_top_tracks.insert_chart, (chart_id, job_id, playlist))
    conn.commit()


def _insert_tracks(chart_id, tracks, cur, conn):
    for t in tracks:
        cur.execute(
            sql.insert_top_tracks.insert_track,
            (
                t["id"],
                t["track_id"],
                t["name"],
                t["artists"],
                t["album"],
                t["popularity"],
                t["duration_ms"],
                t["position"],
                chart_id,
            ),
        )
        conn.commit()


def get_top_songs(auth_token, conn):
    cur = conn.cursor()

    playlists = {"us": "37i9dQZEVXbLRQDuF5jeBp", "global": "37i9dQZEVXbMDoHDwVN2tF"}
    today = str(datetime.datetime.utcnow()).split(" ")[0]
    job_id = str(uuid4())

    _insert_job(today, job_id, cur, conn)

    charts = []

    for playlist in playlists.keys():
        chart_id = str(uuid4())

        _insert_chart(job_id, chart_id, playlist, cur, conn)
        tracks = _fetch_tracks(
            playlist=playlist,
            playlist_id=playlists[playlist],
            auth_token=auth_token,
            date=today,
            job_id=job_id,
            chart_id=chart_id,
        )

        _insert_tracks(chart_id, tracks, cur, conn)

    return charts
