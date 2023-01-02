insert_job = """INSERT INTO jobs (
    date,
    id
) VALUES (
    %s,
    %s
)
"""

insert_chart = """INSERT INTO charts (
    id,
    job_id,
    country
) VALUES (
    %s,
    %s,
    %s
)
"""

insert_track = """INSERT INTO tracks (
    id,
    track_id,
    name,
    artists,
    album,
    popularity,
    duration_ms,
    position,
    chart_id
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s
)"""
