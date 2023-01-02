# Spotify Airflow ETL Job

This is a very basic Airflow job that pulls data from the Spotify API and inserts it into a Postgres database.

## Getting Started
First, create a Spotify developers account and generate a client ID and client secret. This is required in order to make HTTP requests to Spotify's API.

Next, create a new `spotify` Postgres database and user.

Add your credential to a `.env` file in the project directory:

```
SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
PG_DATABASE=spotify
PG_USER=spotify
PG_PASSWORD=spotify
PG_HOST=localhost
PG_PORT=5432
```

## Installing Dependencies
Install the basic project dependencies with `pip install -r requirements.txt`.

Next, we have to install Airflow.

```
export AIRFLOW_HOME=~/airflow
AIRFLOW_VERSION=2.5.0
PYTHON_VERSION="$(python --version | cut -d " " -f 2 | cut -d "." -f 1-2)"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"
pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

Edit your `~/airflow/airflow.cfg` and set the `dags_folder` variable to the absolute file path of the `dags` directory in the project.

## Running the Service
Start Airflow with `airflow standalone` or by running `airflow webserver --port 8080` and `airflow scheduler`.

Running `airflow standalone` will create an admin account for you. You can login with the credentials provided in the terminal.

## Job Summary
Three tables are created, `jobs`, `charts`, and `tracks`.

Each time the Airflow DAG is run, an entry is added to the `jobs` table.
```
    date    |                  id                  
------------+--------------------------------------
 2023-01-02 | 180a8580-a5da-4930-a687-a52c6d975989
(1 row)
```

Each job will query multiple charts, each of which are added to the `charts` table.
```
                job_id                |                  id                  | country 
--------------------------------------+--------------------------------------+---------
 180a8580-a5da-4930-a687-a52c6d975989 | c03967b6-4dbe-42d5-8a95-aa0b2f7668dd | us
 180a8580-a5da-4930-a687-a52c6d975989 | 2fa818a8-6a3c-4ad9-b619-cae47e0d734d | global
 180a8580-a5da-4930-a687-a52c6d975989 | 414528a7-971a-4018-ab08-6312351f2f5a | pl
 180a8580-a5da-4930-a687-a52c6d975989 | 654817f0-8be8-4fe9-92eb-a39542c9b8fd | fi
 180a8580-a5da-4930-a687-a52c6d975989 | dd871bcb-5605-4501-8d76-0dd596999080 | de
 180a8580-a5da-4930-a687-a52c6d975989 | 27596e24-536b-4850-81ec-b4c9a01385c8 | fr
 180a8580-a5da-4930-a687-a52c6d975989 | 96fba318-abaa-46f3-87ec-3dfa220da600 | th
 180a8580-a5da-4930-a687-a52c6d975989 | a3a09f87-6d68-41a4-9c0e-dfff1b1b8ecf | sk
(8 rows)
```

Tracks are added to the `tracks` table for each chart.
```
spotify=> select name from tracks where chart_id = 'c03967b6-4dbe-42d5-8a95-aa0b2f7668dd' limit 10;
                           name                            
-----------------------------------------------------------
 Kill Bill
 Rich Flex
 Unholy (feat. Kim Petras)
 Creepin' (with The Weeknd & 21 Savage)
 Anti-Hero
 Just Wanna Rock
 As It Was
 I'm Good (Blue)
 Bad Habit
 Superhero (Heroes & Villains) [with Future & Chris Brown]
(10 rows)
```

The following columns are saved to the `tracks` table:
```
id
track_id
name
artists
album
popularity
duration_ms
position
chart_id
```