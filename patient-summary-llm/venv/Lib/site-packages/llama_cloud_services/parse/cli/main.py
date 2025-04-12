import click
import json
from enum import Enum
from pathlib import Path
from pydantic.fields import FieldInfo
from typing import Any, Callable, List

from llama_cloud_services.parse.base import LlamaParse


def pydantic_field_to_click_option(name: str, field: FieldInfo) -> click.Option:
    """Convert a Pydantic field to a Click option."""
    kwargs = {
        "default": field.default if field.default else None,
        "help": field.description,
    }

    if isinstance(kwargs["default"], Enum):
        kwargs["default"] = kwargs["default"].value

    if field.annotation is bool:
        kwargs["is_flag"] = True
        if field.default and field.default is True:
            name = f"no-{name}"
    return click.option(f'--{name.replace("_", "-")}', **kwargs)


def add_options(options: List[click.Option]) -> Callable:
    def _add_options(func: Callable) -> Callable:
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


@click.command()
@click.argument("file_paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output-file", type=click.Path(path_type=Path), help="Path to save the output"
)
@click.option("--output-raw-json", is_flag=True, help="Output the raw JSON result")
@add_options(
    [
        pydantic_field_to_click_option(name, field)
        for name, field in LlamaParse.model_fields.items()
        if name not in ["custom_client"]
    ]
)
def parse(**kwargs: Any) -> None:
    """Parse files using LlamaParse and output the results."""
    file_paths = kwargs.pop("file_paths")
    output_file = kwargs.pop("output_file")
    output_raw_json = kwargs.pop("output_raw_json")

    # Remove None values to use LlamaParse defaults
    kwargs = {k: v for k, v in kwargs.items() if v is not None}

    # Remove no- prefix for boolean flags
    kwargs = {k.replace("no_", ""): v for k, v in kwargs.items()}

    parser = LlamaParse(**kwargs)
    if output_raw_json:
        results = parser.get_json_result(list(file_paths))

        if output_file:
            with output_file.open("w") as f:
                json.dump(results, f)
            click.echo(f"Results saved to {output_file}")
        else:
            click.echo(results)
    else:
        results = parser.load_data(list(file_paths))

        if output_file:
            with output_file.open("w") as f:
                for i, doc in enumerate(results):
                    f.write(f"File: {doc.metadata.get('file_path', 'Unknown')}\n")  # type: ignore
                    f.write(doc.text)  # type: ignore
                    if i < len(results) - 1:
                        f.write("\n\n---\n\n")
            click.echo(f"Results saved to {output_file}")
        else:
            for i, doc in enumerate(results):
                click.echo(f"File: {doc.metadata.get('file_path', 'Unknown')}")  # type: ignore
                click.echo(doc.text)  # type: ignore
                if i < len(results) - 1:
                    click.echo("\n---\n")


if __name__ == "__main__":
    parse()
