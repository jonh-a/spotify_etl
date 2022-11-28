import psycopg2
from dags.util.authenticate_spotify import authenticate_spotify
from dags.scripts.get_top_songs import get_top_songs
import sql.create_tables
from dotenv import load_dotenv
import os


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


def main():
    conn = _connect_to_db()
    _create_tables(conn)

    auth_token = authenticate_spotify()
    top_songs = get_top_songs(auth_token, conn)
    conn.close()


if __name__ == "__main__":
    main()
