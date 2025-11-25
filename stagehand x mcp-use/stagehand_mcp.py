from mcp.server.fastmcp import FastMCP
from stagehand_tool import browser_automation


# Create FastMCP instance
mcp = FastMCP("stagehand_mcp")


@mcp.tool()
def browser_automation_tool(task_description: str, website_url: str) -> str:
    """Perform browser automation.

    This tool automates interactions with a web browser to perform tasks
    on a specified website.

    Args:
        task_description (str): Description of the automation task to be performed in the browser
        website_url (str): URL of the website to interact with

    Returns:
        str: Result of the browser automation
    """
    try:
        result = browser_automation(task_description, website_url)
        return result
    except RuntimeError as e:
        return {"error": f"Browser automation failed: {str(e)}"}


@mcp.tool()
def add_numbers(a: float, b: float) -> dict:
    """Add two numbers together.

    Args:
        a (float): First number
        b (float): Second number

    Returns:
        dict: Dictionary containing the two numbers and their sum
    """
    sum_result = a + b
    return {
        "first_number": a,
        "second_number": b, 
        "sum": sum_result
    }



# Run the server
if __name__ == "__main__":
    mcp.run()