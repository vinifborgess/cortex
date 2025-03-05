/* Creating Chunk-Table */ 

CREATE TABLE JOBS_DE.PUBLIC.jobs_de_chunks AS
SELECT
    jobs.job_summary,
    jobs.job_title,
    jobs.company,
    jobs.search_city,
    jobs.search_country,
    t.chunk AS chunk
FROM JOBS_DE.PUBLIC.dataengineerstacks AS jobs,
     TABLE(
       jobs_chunk(
         jobs.job_title,                         -- 1)  STRING
         jobs.company,                      -- 2)  STRING
         CAST(NULL AS STRING),                   -- 3)  job_location
         CAST(NULL AS STRING),                   -- 4)  job_link
         CAST(''   AS STRING),                   -- 5)  first_seen
         jobs.search_city,                       -- 6)  STRING
         jobs.search_country,                    -- 7)  STRING
         CAST(''   AS STRING),                   -- 8)  job_level
         CAST(''   AS STRING),                   -- 9)  job_type
         jobs.job_summary                        -- 10) STRING
       )
     ) AS t;