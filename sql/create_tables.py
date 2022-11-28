create_jobs_table = """CREATE TABLE IF NOT EXISTS jobs (
    date DATE,
    id VARCHAR(100)
);
"""

create_charts_table = """CREATE TABLE IF NOT EXISTS charts (
    job_id VARCHAR(100),
    id VARCHAR(100),
    country VARCHAR(100)
)"""

create_tracks_table = """CREATE TABLE IF NOT EXISTS tracks (
    id VARCHAR(100),
    track_id VARCHAR(100),
    name VARCHAR(1000),
    artists VARCHAR[],
    album VARCHAR(1000),
    popularity INTEGER,
    duration_ms INTEGER,
    position INTEGER,
    chart_id VARCHAR(100)
)"""
