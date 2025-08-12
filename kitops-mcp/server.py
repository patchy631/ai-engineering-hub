from typing import List, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
import tools


# Create FastMCP instance
mcp = FastMCP("kitops_mcp")


@mcp.tool()
def create_kitfile(working_dir: str, modelkit_name: str) -> str:
    """Create a new Kitfile at the specified directory with the given ModelKit name.

    Use this tool when you need to initialize a Kitfile for a new project or update an existing one with
    updated project code, model, dataset, or documentation. The tool will create or overwrite the Kitfile in the specified
    working directory.

    Args:
        working_dir: The absolute or relative path to the directory where the Kitfile should be created.
                    Must be an existing directory.
        modelkit_name: The name to use for the ModelKit reference in the Kitfile.
                      Cannot be empty.

    Returns:
        A message confirming the Kitfile is created or updated successfully.

    Raises:
        ValueError: If the working directory doesn't exist or modelkit_name is empty.
        RuntimeError: If the Kitfile creation fails for any reason.
    """
    return tools.create(working_dir, modelkit_name)


@mcp.tool()
def inspect_modelkit(modelkit_tag: str, **kwargs) -> Dict[str, Any]:
    """Inspect a ModelKit and return its detailed information from the remote registry.

    Use this tool when you need to retrieve detailed information about a specific ModelKit,
    such as its manifest, cliVersion, Kitfile, and other properties.

    Args:
        modelkit_tag: The tag of the ModelKit to inspect in the format 'registry/namespace/repository:tag'.
        **kwargs: Additional optional parameters to pass to the kit inspect command.

    Returns:
        A dictionary containing detailed information about the ModelKit.

    Raises:
        RuntimeError: If the inspection fails or the ModelKit doesn't exist.
        ValueError: If the modelkit_tag format is invalid.
    """
    return tools.inspect(modelkit_tag, **kwargs)


@mcp.tool()
def push_and_pack_modelkit(modelkit_tag: str, working_dir: str) -> str:
    """Pack the project situated at the working directory and push it as a ModelKit to the remote registry.

    Use this tool when you need to save and publish a local project as a ModelKit.
    This requires a valid Kitfile in the working directory.

    Args:
        modelkit_tag: The tag for the ModelKit in the format 'registry/namespace/repository:tag'.
        working_dir: The absolute or relative path to the directory containing the project to pack.
                    Must contain a valid Kitfile.

    Returns:
        A message confirming the ModelKit is packed and pushed successfully.

    Raises:
        ValueError: If the working directory doesn't exist or the modelkit_tag format is invalid.
        RuntimeError: If packing or pushing fails, including if the Kitfile is missing.
    """
    return tools.push_and_pack(modelkit_tag, working_dir)


@mcp.tool()
def pull_and_unpack_modelkit(
    working_dir: str, modelkit_tag: str, filters: Optional[List[str]] = None
) -> str:
    """Pull a ModelKit from the remote registry and unpack it to the specified directory.

    Use this tool when you need to download and extract a ModelKit to a local directory.
    The directory will be created if it doesn't exist. You can optionally specify filters
    to download only specific components of the ModelKit.

    Args:
        working_dir: The absolute or relative path to the directory where the ModelKit should be unpacked.
        modelkit_tag: The tag of the ModelKit to pull in the format 'registry/namespace/repository:tag'.
        filters: Optional list of components to download. Valid values are 'datasets', 'code', 'model', and 'docs'.
                If not provided, all components will be downloaded.

    Returns:
        A message confirming the ModelKit was pulled and unpacked successfully.

    Raises:
        ValueError: If the modelkit_tag format is invalid or filters contain invalid values.
        RuntimeError: If pulling or unpacking the ModelKit fails.
    """
    return tools.pull_and_unpack(working_dir, modelkit_tag, filters)


@mcp.tool()
def remove_modelkit(modelkit_tag: str) -> str:
    """Remove a ModelKit from the remote registry.

    Use this tool when you need to delete a ModelKit from the remote registry.
    This operation cannot be undone, so use it with caution.

    Args:
        modelkit_tag: The tag of the ModelKit to remove in the format 'registry/namespace/repository:tag'.

    Returns:
        A message confirming the ModelKit was removed successfully.

    Raises:
        ValueError: If the modelkit_tag format is invalid.
        RuntimeError: If the removal operation fails.
    """
    return tools.remove(modelkit_tag)


# Run the server
if __name__ == "__main__":
    mcp.run(transport="stdio")
