from mcp.server.fastmcp import FastMCP
from tools import generate, evaluate, visualize


# Create FastMCP instance
mcp = FastMCP("sdv_mcp")


@mcp.tool()
def sdv_generate(folder_name: str) -> str:
    """Generate synthetic data based on real data using SDV Synthesizer.

    This tool reads CSV files from the specified folder, creates a synthetic
    version of that data, and saves it to a 'synthetic_data' folder.

    Args:
        folder_name (str): Path to folder containing CSV data files and metadata.json

    Returns:
        str: Success message with information about generated tables
    """
    try:
        return generate(folder_name)
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except RuntimeError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def sdv_evaluate(folder_name: str) -> dict:
    """Evaluate the quality of synthetic data compared to real data.

    This tool compares the synthetic data in the 'synthetic_data' folder
    with the real data in the specified folder and generates quality metrics.

    Args:
        folder_name (str): Path to folder containing the original CSV data files and metadata.json

    Returns:
        dict: Evaluation results including overall score and detailed properties
    """
    try:
        result = evaluate(folder_name)
        return result
    except FileNotFoundError as e:
        return {"error": f"File not found: {str(e)}"}
    except RuntimeError as e:
        return {"error": f"Evaluation failed: {str(e)}"}


@mcp.tool()
def sdv_visualize(
    folder_name: str,
    table_name: str,
    column_name: str,
) -> str:
    """Generate visualization comparing real and synthetic data for a specific column.

    This tool creates a visual comparison between the real data in the specified folder
    and the synthetic data in the 'synthetic_data' folder for a particular table column.
    The visualization is saved as a PNG file in the 'evaluation_plots' folder.

    Args:
        folder_name (str): Path to folder containing the original CSV data files and metadata.json
        table_name (str): Name of the table to visualize (must exist in the metadata)
        column_name (str): Name of the column to visualize within the specified table

    Returns:
        str: Success message with the path to the saved visualization or error message
    """
    try:
        return visualize(folder_name, table_name, column_name)
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except RuntimeError as e:
        return f"Error: {str(e)}"


# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
