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
