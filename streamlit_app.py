import streamlit as st
from langchain import OpenAI, SQLDatabase
from langchain.chains import create_sql_query_chain
from snowflake.snowpark import Session
import os

# Streamlit app structure
def main():
    # Load secrets for Snowflake and OpenAI
    snowflake_url = st.secrets["snowflake_url"]
    OpenAI_API_KEY = st.secrets["OpenAI_API_KEY"]

    # Streamlit UI components
    st.title("Natural Language SQL Query Generator")
    natural_language_query = st.text_area("Enter your query in natural language:")
    submit_button = st.button("Generate SQL Query")

    # Connection to the database
    db = SQLDatabase.from_uri(snowflake_url, sample_rows_in_table_info=1, include_tables=['orders', 'locations'])

    if submit_button and natural_language_query:
        llm = OpenAI(temperature=0, openai_api_key=OpenAI_API_KEY)
        # Process the natural language query and generate SQL
        database_chain = create_sql_query_chain(llm, db)
        generated_sql_query = database_chain(natural_language_query)

        # Display the generated SQL query
        st.text("Generated SQL Query:")
        st.code(generated_sql_query)

        # Execute and display query results
        session = Session.builder.configs(db.session_configs).create()
        query_result = session.sql(generated_sql_query).collect()
        formatted_results = format_query_results(query_result)

        # Display results in a scrollable box
        st.text("Query Results:")
        st.text_area("", value=formatted_results, height=300)

def format_query_results(query_result):
    # Format the Snowflake query results for display
    # Implement the formatting logic as per your requirements
    # This is a placeholder - update it to match your actual formatting needs
    formatted_result = "\n".join([str(row) for row in query_result])
    return formatted_result

# Run the app
if __name__ == "__main__":
    main()
