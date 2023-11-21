import streamlit as st
from langchain import OpenAI, SQLDatabase
from langchain.chains import create_sql_query_chain
from snowflake.snowpark import Session

# Function to check login credentials
def check_login(username, password):
    correct_username = st.secrets["loginId"]
    correct_password = st.secrets["loginPassword"]
    return username == correct_username and password == correct_password

# Streamlit app structure
def main():
    # Login Page
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.title("Login to Access the SQL Query Generator")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if check_login(username, password):
                st.session_state['logged_in'] = True
            else:
                st.error("Incorrect username or password. Please try again.")

    # Main App
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        # Load secrets for Snowflake and OpenAI
        OpenAI_API_KEY = st.secrets["OPENAI_API_KEY"]
        snowflake_account = st.secrets["ACCOUNT"]
        username = st.secrets["USER"]
        password = st.secrets["SNOWSQL_PWD"]
        warehouse = st.secrets["WAREHOUSE"]
        database = st.secrets['LANGCHAIN_DEMO_DB']
        schema = st.secrets['PUBLIC']
        role = st.secrets["ROLE"]

        snowflake_url = f'snowflake://{username}:{password}@{snowflake_account}/{database}/{schema}?warehouse={warehouse}&role={role}'

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
    formatted_result = "\n".join([str(row) for row in query_result])
    return formatted_result

# Run the app
if __name__ == "__main__":
    main()
