import requests
from dotenv import load_dotenv
import os
import base64
import datetime
from uuid import uuid4
import sql.create_tables
import sql.insert_top_tracks
import psycopg2
from airflow import DAG
from airflow.operators.python_operator import PythonOperator


def _connect_to_db():
    load_dotenv()
    try:
        conn = psycopg2.connect(
            database=os.getenv("PG_DATABASE"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            host=os.getenv("PG_HOST"),
            port=os.getenv("PG_PORT"),
        )
        print("connected")
        return conn
    except:
        print("failed to connect")


def _create_tables(conn):
    cur = conn.cursor()
    cur.execute(sql.create_tables.create_tracks_table)
    cur.execute(sql.create_tables.create_jobs_table)
    cur.execute(sql.create_tables.create_charts_table)
    conn.commit()


def _encode_auth_header(client_id, client_secret):
    string = f"{client_id}:{client_secret}"
    string_bytes = string.encode("ascii")
    base64_bytes = base64.b64encode(string_bytes)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


def _authenticate_spotify():
    load_dotenv()
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    auth_header = _encode_auth_header(client_id, client_secret)

    try:
        authorize_response = requests.post(
            "https://accounts.spotify.com/api/token",
            headers={
                "Authorization": f"Basic {auth_header}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "client_credentials"},
        )

        print("Authorize response:", authorize_response.status_code)
        return authorize_response.json()["access_token"]
    except Exception as e:
        print("Failed to authenticate with Spotify.", e)
        return ""


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


def get_top_songs():
    conn = _connect_to_db()
    print("Connected to database.")

    _create_tables(conn)
    print("Created tables.")

    auth_token = _authenticate_spotify()
    print("Authenticated with Spotify.")

    cur = conn.cursor()

    playlists = {
        "us": "37i9dQZEVXbLRQDuF5jeBp",
        "global": "37i9dQZEVXbMDoHDwVN2tF",
        "pl": "37i9dQZEVXbN6itCcaL3Tt",
        "fi": "37i9dQZEVXbMxcczTSoGwZ",
        "de": "37i9dQZEVXbJiZcmkrIHGU",
        "fr": "37i9dQZEVXbIPWwFssbupI",
        "th": "37i9dQZEVXbMnz8KIWsvf9",
        "sk": "37i9dQZEVXbNxXF4SkHj9F",
    }
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


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.datetime(2022, 12, 8),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=1),
}

dag = DAG(
    "spotify_dag",
    default_args=default_args,
    description="Spotify ETL job",
    schedule_interval=datetime.timedelta(days=1),
)

run_etl = PythonOperator(
    task_id="spotify_etl_task", python_callable=get_top_songs, dag=dag
)

run_etl
