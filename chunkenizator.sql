/* Chunkenization */ 

CREATE OR REPLACE FUNCTION jobs_chunk(
    JOB_TITLE STRING,
    COMPANY STRING,
    JOB_LOCATION STRING,
    JOB_LINK STRING,
    FIRST_SEEN STRING,
    SEARCH_CITY STRING,
    SEARCH_COUNTRY STRING,
    JOB_LEVEL STRING,
    JOB_TYPE STRING,
    JOB_SUMMARY STRING
)
RETURNS TABLE (
    chunk STRING,
    job_summary STRING,
    job_title STRING,
    company_name STRING,
    search_city STRING,
    search_country STRING
)
LANGUAGE PYTHON
RUNTIME_VERSION = '3.9'
HANDLER = 'JobsChunkUDTF'    -- AQUI VAI O NOME DA CLASSE
PACKAGES = ('snowflake-snowpark-python', 'langchain')
AS
$$
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import Optional

# Lista de palavras-chave para Data Engineering
SKILL_KEYWORDS = [
    'SQL', 'Python', 'Apache Spark', 'Hadoop', 'Kafka', 'ETL', 
    'Data Pipeline', 'Data Warehouse', 'Snowflake', 'BigQuery', 'Redshift', 
    'Airflow', 'Databricks', 'AWS Glue', 'Azure Data Factory', 'Google Cloud Dataflow',
    'NoSQL', 'PostgreSQL', 'MongoDB', 'Delta Lake', 'Dremio', 'Presto',
    'Data Lake', 'OLAP', 'Batch Processing', 'Streaming', 'Parquet', 'Avro',
    'Athena', 'Terraform', 'Data Modeling', 'Data Governance', 'Data Quality'
]

class JobsChunkUDTF:
    def process(
        self,
        job_title: str,         
        company: str,           
        job_location: str,      
        job_link: str,          
        first_seen: str,        
        search_city: str,       
        search_country: str,    
        job_level: str,         
        job_type: str,          
        job_summary: Optional[str]
    ):
        # Caso o resumo esteja nulo
        if job_summary is None:
            job_summary = ""

        # Inicializa o text splitter do LangChain
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=300
        )

        # Divide o texto em chunks
        chunks = text_splitter.split_text(job_summary)
        
        # Para cada chunk, vamos gerar uma linha
        for chunk in chunks:
            skill_mentions = [skill for skill in SKILL_KEYWORDS if skill.lower() in chunk.lower()]
            if skill_mentions:
                chunk_with_skills = f"Skills: {', '.join(skill_mentions)}\n{chunk}"
            else:
                chunk_with_skills = chunk

            # Use yield para retornar várias linhas
            yield (
                chunk_with_skills,  # chunk
                job_summary,        # job_summary
                job_title,          # job_title
                company,            # company_name
                search_city,        # search_city
                search_country      # search_country
            )
$$;