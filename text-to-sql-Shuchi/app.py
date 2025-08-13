import os
import streamlit as st
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, text, insert, inspect
from smolagents import tool, CodeAgent, LiteLLMModel

# Access the API key from Streamlit secrets
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Create an in-memory SQLite database and define the table structure
engine = create_engine("sqlite:///:memory:")
metadata_obj = MetaData()

table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("state", String(16), nullable=False),
)

metadata_obj.create_all(engine)

# Insert sample data into the table
rows = [
    {"city_name": "New York City", "population": 8336000, "state": "New York"},
    {"city_name": "Los Angeles", "population": 3822000, "state": "California"},
    {"city_name": "Chicago", "population": 2665000, "state": "Illinois"},
    {"city_name": "Houston", "population": 2303000, "state": "Texas"},
    {"city_name": "Miami", "population": 449514, "state": "Florida"},
    {"city_name": "Seattle", "population": 749256, "state": "Washington"},
]

for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        connection.execute(stmt)

# Define the SQL engine tool
@tool
def sql_engine(query: str) -> str:
    """
    Executes the generated SQL query on the 'city_stats' table and returns the results.
    Args:
        query: The query to perform. This should be correct SQL.
    Returns:
        A string representation of the query results.
    """
    try:
        with engine.connect() as con:
            result = con.execute(text(query))
            columns = result.keys()
            rows = result.fetchall()
            
            if not rows:
                return "No results found."
                
            # Format results as a table
            output = "\n| " + " | ".join(columns) + " |"
            output += "\n|" + "---|" * len(columns)
            
            for row in rows:
                output += "\n| " + " | ".join(str(val) for val in row) + " |"
                
            return output
    except Exception as e:
        return f"Error executing SQL query: {str(e)}"

# Initialize the CodeAgent with the SQL engine tool
model_name = 'Gemini Flash 2.0'
if model_name.startswith("Gemini"):
    model = LiteLLMModel(
        model_id="gemini/gemini-2.0-flash-exp",
        api_key=GEMINI_API_KEY
    )
    print("Using Gemini 2.0 Flash")
else:
    model = HfApiModel("Qwen/Qwen2.5-Coder-32B-Instruct")
    print("Using Qwen 2.5 Coder")

agent = CodeAgent(
    tools=[sql_engine],
    model=model,
)

# Streamlit UI
st.title("Welcome to the City Explorer! 🏙️")
st.markdown("""
This app is like a smart assistant that helps you find information about cities. You can ask questions about cities, states, and populations.
""")

# Predefined queries
st.subheader("🔍FAQ Queries")
predefined_queries = {
    "What are the different states?": "What are the different states?",
    "What state is Houston located in?": "What state is Houston located in?",
    "Which city has the largest population?": "Which city has the largest population?",
    "What is the population of Miami?": "What is the population of Miami?",
}

# Dropdown for predefined queries
selected_query = st.selectbox(
    "Choose any query:",
    list(predefined_queries.keys())
)

# Button to execute the predefined query
if st.button("FAQ Result"):
    query_prompt = predefined_queries[selected_query]
#     st.write(f"**Executing Query:** `{query_prompt}`")
    try:
        result = agent.run(query_prompt)
        st.write("**Query Result:**")
        st.write(result)
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Custom query input
st.subheader("💬 Your Query")
custom_query = st.text_input("Enter your query:")

# Button to execute the custom query
if st.button("Run Custom Query"):
    if custom_query.strip() == "":
        st.warning("Please enter a query.")
    else:
     #    st.write(f"**Executing Query:** `{custom_query}`")
        try:
            result = agent.run(custom_query)
            st.write("**Query Result:**")
            st.write(result)
        except Exception as e:
            st.error(f"An error occurred: {e}")

