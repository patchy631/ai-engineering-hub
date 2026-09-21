from llama_index.core.tools import QueryEngineTool
from sql_setup import SQLSetup
from llama_cloud_setup import LlamaCloudSetup

class QueryEngineTools:
    def __init__(self):
        self.sql_setup = SQLSetup()
        self.llama_cloud_setup = LlamaCloudSetup()

        self.sql_query_engine = self.sql_setup.get_sql_query_engine()
        self.llama_cloud_query_engine = self.llama_cloud_setup.get_query_engine()

        self.sql_tool = None
        self.llama_cloud_tool = None

        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize query engine tools."""
        self.sql_tool = QueryEngineTool.from_defaults(
            query_engine=self.sql_query_engine,
            description=(
                "Useful for translating a natural language query into a SQL query over"
                " a table containing: city_stats, containing the population/state of"
                " each city located in the USA."
            ),
            name="sql_tool"
        )

        self.llama_cloud_tool = QueryEngineTool.from_defaults(
            query_engine=self.llama_cloud_query_engine,
            description="Useful for answering semantic questions about certain cities in the US.",
            name="llama_cloud_tool"
        )

    def get_sql_tool(self):
        """Returns the SQL query tool."""
        return self.sql_tool

    def get_llama_cloud_tool(self):
        """Returns the LlamaCloud query tool."""
        return self.llama_cloud_tool


# Usage Example:
if __name__ == "__main__":
    tool_setup = QueryEngineTools()
    sql_tool = tool_setup.get_sql_tool()
    llama_cloud_tool = tool_setup.get_llama_cloud_tool()
