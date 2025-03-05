CREATE CORTEX SEARCH SERVICE job_search_service
    ON CHUNK
    WAREHOUSE = COMPUTE_WH
    TARGET_LAG = '1 hour'
    AS (
    SELECT * FROM JOBS_DE.PUBLIC.jobs_de_chunks
    );