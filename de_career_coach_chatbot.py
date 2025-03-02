import streamlit as st
import re
from snowflake.snowpark.context import get_active_session

# ------------------------------------------------------------------------------
# 1) INITIAL CONFIGURATION
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Cortex AI - Data Engineering Assistant", page_icon=":brain:")

# Active Snowpark session (on Snowflake)
session = get_active_session()

# ------------------------------------------------------------------------------
# 2) HEADER & LAYOUT ELEMENTS
# ------------------------------------------------------------------------------
st.markdown(
    """
    <div style="text-align: center;">
        <img src="https://i.pinimg.com/originals/0b/1d/fc/0b1dfc8ebe6f365f4208cb0cff5c46c9.gif" width="100" alt="Chibi AI Mascot">
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Cortex AI - Your Data Engineering Career Assistant :mag_right:")
st.markdown(
    """
    Welcome to **Cortex AI**, your dedicated assistant for exploring career opportunities in Data Engineering!  

    🔹 **Relevance Score:** Indicates how well the job listing matches your search term. A **higher score** means a **closer match**.  
    🔹 **Locations Available:** *United States, Canada, United Kingdom, Australia*  
    """
)

# ------------------------------------------------------------------------------
# 3) JOB SEARCH FUNCTION
# ------------------------------------------------------------------------------

def get_available_locations():
    """Busca todas as localizações disponíveis, removendo espaços extras e excluindo valores inválidos."""
    query = "SELECT DISTINCT TRIM(SEARCH_COUNTRY) AS SEARCH_COUNTRY FROM JOBS_DE.PUBLIC.jobs_de_chunks"
    locations = session.sql(query).collect()
    return {row['SEARCH_COUNTRY'].strip() for row in locations if row['SEARCH_COUNTRY'] and row['SEARCH_COUNTRY'] != 'search_country'}

def clean_text(text):
    """Remove informações irrelevantes dos anúncios de vaga."""
    patterns_to_remove = [
        r"Get The Future You Want.*?www.capgemini.com",
        r"Click the following link for more information.*?$",
        r"Capgemini is committed to providing reasonable accommodations.*?$",
        r"Please be aware that Capgemini may capture your image.*?$",
        r"This is a general description.*?$",
        r"Life at Capgemini.*?$",
        r"About Capgemini.*?$",
        r"Applicants for employment in.*?$"
    ]

    for pattern in patterns_to_remove:
        text = re.sub(pattern, "", text, flags=re.MULTILINE | re.DOTALL)

    return text.strip()

def search_jobs(query: str, location: str = None):
    """Realiza a busca por vagas com base no termo e localização."""
    terms = query.split()
    or_conditions = " OR ".join([f"CHUNK ILIKE '%{term}%'" for term in terms if term])

    if not or_conditions:
        return []

    available_locations = get_available_locations()
    normalized_location = location.strip() if location else None

    # 🚨 Se a localização não for válida, alerta o usuário
    if normalized_location and normalized_location not in available_locations:
        st.warning(f"⚠ '{normalized_location}' is not a valid location. Available locations: {', '.join(available_locations)}")
        return []

    location_filter = f"TRIM(SEARCH_COUNTRY) ILIKE '{normalized_location}'" if normalized_location else ""

    sql_query = f"""
    WITH FilteredJobs AS (
        SELECT DISTINCT JOB_TITLE, COMPANY, SEARCH_CITY, TRIM(SEARCH_COUNTRY) AS SEARCH_COUNTRY, CHUNK
        FROM JOBS_DE.PUBLIC.jobs_de_chunks
        WHERE ({or_conditions}) {f'AND ({location_filter})' if location_filter else ''}
    ),
    AggregatedJobs AS (
        SELECT 
            JOB_TITLE, 
            COMPANY, 
            SEARCH_CITY, 
            SEARCH_COUNTRY, 
            COALESCE(LISTAGG(CHUNK, ' ') WITHIN GROUP (ORDER BY CHUNK), 'No description available') AS FULL_DESCRIPTION,
            COUNT(*) AS MATCH_COUNT
        FROM FilteredJobs
        GROUP BY JOB_TITLE, COMPANY, SEARCH_CITY, SEARCH_COUNTRY
    )
    SELECT JOB_TITLE, COMPANY, SEARCH_CITY, SEARCH_COUNTRY, FULL_DESCRIPTION, MATCH_COUNT
    FROM AggregatedJobs
    ORDER BY MATCH_COUNT DESC
    LIMIT 50;
    """

    results = session.sql(sql_query).collect()

    formatted_results = []
    for i, row in enumerate(results, start=1):
        description = row.FULL_DESCRIPTION if "FULL_DESCRIPTION" in row.asDict() else "No description available"
        cleaned_description = clean_text(description)
        short_description = cleaned_description[:300] + "..." if len(cleaned_description) > 300 else cleaned_description
        
        formatted_results.append({
            "index": i,
            "job_title": row.JOB_TITLE,
            "company": row.COMPANY,
            "location": f"{row.SEARCH_CITY}, {row.SEARCH_COUNTRY}",
            "match_score": row.MATCH_COUNT,
            "short_description": short_description,
            "full_description": cleaned_description
        })
    
    return formatted_results

# ------------------------------------------------------------------------------
# 4) CHAT INTERFACE
# ------------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def display_chat():
    """Exibe o histórico de chat."""
    for msg in st.session_state["messages"]:
        if msg["from"] == "user":
            st.markdown(f"**You:** {msg['text']}")
        else:
            st.markdown(f"**Cortex AI:** {msg['text']}")

# 🔹 Campo para palavra-chave e país
user_input = st.text_input("Enter a keyword to search for jobs...", "")
location_input = st.text_input("Enter a country to filter jobs (e.g., 'United States', 'Canada', 'United Kingdom', 'Australia')...", "")

# 🔹 Botão de busca
if st.button("Search", help="Click to find relevant job openings"):
    if user_input.strip():
        st.session_state["messages"].append({"from": "user", "text": f"{user_input} (Location: {location_input})"})
        results = search_jobs(user_input, location_input)

        if not results:
            response = f"❌ No results found for '{user_input}' in {location_input if location_input else 'any location'}. Try different keywords or a broader location."
        else:
            response = f"### 🔍 Found **{len(results)}** job listings in {location_input if location_input else 'all locations'}:\n"

            for i, row in enumerate(results, start=1):
                with st.container():
                    st.markdown(f"### **[{i}] {row['job_title']}**")
                    st.markdown(f"🏢 **Company:** {row['company']}  \n"
                                f"📍 **Location:** {row['location']}  \n"
                                f"📊 **Relevance Score:** {row['match_score']} (higher is better)")

                    with st.expander("📄 View Full Job Description"):
                        st.markdown(f"```\n{row['full_description']}\n```")

            response += "\nExpand the listings to view detailed descriptions!"

        st.session_state["messages"].append({"from": "bot", "text": response})

display_chat()

# ------------------------------------------------------------------------------
# 5) FOOTER
# ------------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 0.9em;'>
        Built with 💝 and a lot of 🍕🍕🍕🍕.<br>
        (C) 2025 - Cortex AI for Data Engineers
    </div>
    """,
    unsafe_allow_html=True
)
