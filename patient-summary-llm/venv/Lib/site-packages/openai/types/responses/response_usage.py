# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.


from ..._models import BaseModel

__all__ = ["ResponseUsage", "OutputTokensDetails"]


class OutputTokensDetails(BaseModel):
    reasoning_tokens: int
    """The number of reasoning tokens."""


class ResponseUsage(BaseModel):
    input_tokens: int
    """The number of input tokens."""

    output_tokens: int
    """The number of output tokens."""

    output_tokens_details: OutputTokensDetails
    """A detailed breakdown of the output tokens."""

    total_tokens: int
    """The total number of tokens used."""
