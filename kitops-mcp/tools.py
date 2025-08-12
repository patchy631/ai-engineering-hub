import os
import json
from typing import List, Dict, Any
from kitops.cli.kit import _run, init
from kitops.cli.utils import _process_command_flags
from kitops.modelkit.kitfile import Kitfile
from kitops.modelkit.manager import ModelKitManager
from util import validate_modelkit_tag


def create(working_dir: str, modelkit_name: str) -> str:
    """Create a new Kitfile at the specified path with referred modelkit name."""
    # Validate the modelkit_name
    if not modelkit_name:
        raise ValueError("Modelkit name must be provided and cannot be empty")
    # Validate the working directory for which the Kitfile is to be created
    working_dir = os.path.abspath(working_dir)
    if not os.path.isdir(working_dir):
        raise ValueError(f"Working directory '{working_dir}' does not exist")

    # Check if Kitfile already exists for the return message
    kitfile_path = os.path.join(working_dir, "Kitfile")
    file_exists = os.path.exists(kitfile_path)
    temp_kitfile_path = None

    try:
        # If Kitfile exists, rename it temporarily to avoid init detecting it
        if file_exists:
            temp_kitfile_path = os.path.join(working_dir, "Kitfile.temp")
            os.rename(kitfile_path, temp_kitfile_path)

        # Create and save Kitfile in the specified working directory
        kitfile = init(directory=working_dir, name=modelkit_name)
        kitfile.save(os.path.join(working_dir, "Kitfile"))

        # Clean up the temporary file if it exists
        if temp_kitfile_path and os.path.exists(temp_kitfile_path):
            os.remove(temp_kitfile_path)

        action = "Overwritten" if file_exists else "Created"
        return f"{action} Kitfile at '{kitfile_path}' with referred ModelKit name '{modelkit_name}' successfully"

    # Handle exceptions that may occur during the creation process
    except Exception as e:
        # Restore the original Kitfile if there was an error
        if temp_kitfile_path and os.path.exists(temp_kitfile_path):
            if os.path.exists(kitfile_path):
                os.remove(kitfile_path)
            os.rename(temp_kitfile_path, kitfile_path)
        raise RuntimeError(f"Failed to create Kitfile: {str(e)}")


def inspect(modelkit_tag: str, **kwargs) -> Dict[str, Any]:
    """Inspect a ModelKit and return its detailed information."""
    # Validate the tag
    validate_modelkit_tag(modelkit_tag)

    try:
        # Prepare the command to inspect the ModelKit
        command = ["kit", "inspect", "--remote", modelkit_tag]
        command.extend(_process_command_flags(kit_cmd_name="inspect", **kwargs))

        # Return the result of the inspection
        result = _run(command=command)
        kit_inspect = json.loads(result.stdout.strip())
        return kit_inspect

    # Handle exceptions that may occur during the inspection process
    except Exception as e:
        raise RuntimeError(f"Failed to inspect ModelKit '{modelkit_tag}': {str(e)}")


def push_and_pack(modelkit_tag: str, working_dir: str) -> str:
    """Pack and push a ModelKit to the repository."""
    # Validate working directory
    if not os.path.isdir(working_dir):
        raise ValueError(f"Working directory '{working_dir}' does not exist")
    
    # Validate the modelkit_tag
    validate_modelkit_tag(modelkit_tag)

    try:
        # Check if Kitfile exists before creating instance
        kitfile_path = os.path.join(working_dir, "Kitfile")
        if not os.path.exists(kitfile_path):
            raise FileNotFoundError(
                f"Kitfile not found in the working directory '{working_dir}'"
            )
        kitfile = Kitfile(path=kitfile_path)

        # Create a ModelKitManager instance and pack and push the ModelKit
        manager = ModelKitManager(
            working_directory=working_dir, modelkit_tag=modelkit_tag
        )
        manager.kitfile = kitfile
        manager.pack_and_push_modelkit()

        return f"Successfully packed project situated at '{working_dir}' and pushed corresponding ModelKit to '{modelkit_tag}' of the remote registry"

    # Handle any exceptions that occur during the pack and push process
    except Exception as e:
        raise RuntimeError(f"Failed to push ModelKit '{modelkit_tag}': {str(e)}")


def pull_and_unpack(
    working_dir: str, modelkit_tag: str, filters: List[str] = None
) -> str:
    """Pull and unpack a ModelKit to the working directory."""
    # Check if working directory and modelkit_tag are valid
    if not os.path.isdir(working_dir):
        os.makedirs(working_dir, exist_ok=True)
    validate_modelkit_tag(modelkit_tag)

    # Validate filters if provided
    valid_filters = {"datasets", "code", "model", "docs"}
    if filters:
        invalid_filters = [f for f in filters if f not in valid_filters]
        if invalid_filters:
            raise ValueError(
                f"Invalid filters: {', '.join(invalid_filters)}. Valid filters are: {', '.join(valid_filters)}"
            )

    try:
        # Create a ModelKitManager instance and pull and unpack the ModelKit
        manager = ModelKitManager(
            working_directory=working_dir, modelkit_tag=modelkit_tag
        )
        manager.pull_and_unpack_modelkit(filters=filters)

        filter_msg = f" with filters {filters}" if filters else ""
        return f"Successfully pulled ModelKit '{modelkit_tag}' to '{working_dir}'{filter_msg}"

    # Handle any exceptions that occur during the pull and unpack process
    except Exception as e:
        raise RuntimeError(f"Failed to pull ModelKit '{modelkit_tag}': {str(e)}")


def remove(modelkit_tag: str) -> str:
    """Remove a ModelKit from the remote registry only."""
    # Validate the modelkit_tag
    validate_modelkit_tag(modelkit_tag)

    try:
        # Create a ModelKitManager instance and remove the ModelKit
        manager = ModelKitManager(modelkit_tag=modelkit_tag)
        manager.remove_modelkit(local=False, remote=True)

        return f"Removed ModelKit '{modelkit_tag}' from the remote registry successfully"

    # Handle exceptions that may occur during the removal process
    except Exception as e:
        raise RuntimeError(f"Failed to remove ModelKit '{modelkit_tag}': {str(e)}")
