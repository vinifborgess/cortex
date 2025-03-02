# Cortex RAG 

Chatbot capable of analyzing job listing descriptions exclusively customized for the data engineering field. Provides personalized keyword and job description feedback according to skills, geolocation and other contexts. The chatbot is powered by a dataset provided by the Kaggle community with real job listing data collected.

# Steps of the RAG (Retrieval-Augmented Generation)

## 1. Importing Data
- **Data Collection**: Data is collected from **Kaggle**.
- **Storage**: Data is imported into **Snowflake**, a data storage and analysis platform.

## 2. Splitting Data into Chunks
- **Processing**: Job descriptions are split into smaller parts (**chunks**) to facilitate processing by the AI ​​model.
- **Focus**: Extract **skills** and **requirements** from job listings, ignoring some irrelevant information.

## 3. Connecting to Snowflake Cortex
- **Data Processing**: **Snowflake Cortex** is used to process the data and apply language models (LLMs) to generate answers.
- **Generative Applications**: Cortex allows you to create generative applications based on stored data.

## 4. Building the Chatbot with Streamlit
- **Development**: The chatbot is developed using **Streamlit**, a Python library that makes it easy to create web applications.
- **Functionality**: The chatbot allows users to ask questions like: *"I know AWS and I'm based on Canada. What I need to know more to be a good fit to a Canadian job post?"*.
- **Analysis and Suggestions**: The chatbot analyzes the data and suggests complementary skills, such as learning **Python** and **SQL**, or deepening knowledge in other tools.

## RAG Project Summary
The RAG project combines **data collection**, **chunk processing**, **language models**, and **web interface** to create a chatbot that provides personalized recommendations based on real job data. The goal is to help users identify the skills they need to advance their careers and increase their salaries.

## Tags
(coming soon)
