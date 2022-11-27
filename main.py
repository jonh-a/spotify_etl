from dags.util.authorize_spotify import authorize_spotify
from dags.scripts.get_top_songs import get_top_songs


def main():
    auth_token = authorize_spotify()
    top_songs = get_top_songs(auth_token)


if __name__ == "__main__":
    main()
