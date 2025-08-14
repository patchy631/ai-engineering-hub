import os
import json
from typing import Any
from dotenv import load_dotenv
from pydantic import BaseModel
from openai import OpenAI
from opik.evaluation.metrics import base_metric, score_result


# Take environment variables from .env
load_dotenv()

# Configure Comet's Opik
import opik
opik.configure(use_local=False)


class LLMJudgeResult(BaseModel):
    """Pydantic model representing the result of LLM judge evaluation."""

    score: int
    reason: str


class LLMJudgeMetric(base_metric.BaseMetric):
    """
    A metric that uses an LLM to judge the quality of AI-generated responses.

    Attributes:
        - name (str): The name of the metric.
        - model_name (str): The name of the LLM model to use for evaluation.
        - llm_client (OpenAI): The client for communicating with the LLM.
        - prompt_template (str): The template for constructing prompts to send to the LLM.

    Methods:
        score(input, output, **ignored_kwargs): Evaluates the AI-generated response against the
            provided input using the LLM as a judge.

    Returns:
        ScoreResult: Contains the numerical score (1-5) and reasoning for the evaluation.
    """

    def __init__(self, name: str = "LLM judge metric", model_name: str = "atla-selene"):
        # Initialize the metric with a name and model name
        self.name = name
        self.model_name = model_name

        # Check if API key is available
        api_key = os.environ.get("ATLA_API_KEY")
        if not api_key:
            raise ValueError(
                "ATLA_API_KEY environment variable not found. Please check your .env file."
            )

        # Initialize the OpenAI client with the API key and base URL for Atla
        self.llm_client = OpenAI(
            api_key=api_key,
            base_url="https://api.atla-ai.com/v1",
        )

        # Define the prompt template for the LLM
        self.prompt_template = """
        You are an expert, impartial judge tasked with evaluating an AI-generated response based on a given instruction and scoring rubric.
        Provide comprehensive feedback on the response, strictly adhering to the scoring rubric. Follow this with a score between 1 and 5.

        The format of the your response should be a json with no backticks that returns:
        {{
            "score": <score between 1 and 5>,
            "reason": "<reason for the score>"
        }}

        Scoring Rubric:
        Does the response effectively use humor or wit to enhance the conversation?
        Score 1: The response is devoid of any humor or wit.
        Score 2: The response attempts humor, but it falls flat or is inappropriate.
        Score 3: The response includes humor or wit, but it could be more effectively integrated.
        Score 4: The response uses humor or wit effectively in most instances, enhancing the conversation.
        Score 5: The response perfectly integrates humor or wit, greatly enhancing the enjoyment of the conversation.

        Here is the data to evaluate:
        Instruction: {input}
        Response: {output}
        """
    
    @opik.track
    def score(self, input: str, output: str, **ignored_kwargs: Any):
        """Method to evaluate the AI-generated response using the LLM judge."""
        # Apply prompt template and prepare the messages for the LLM
        prompt = self.prompt_template.format(input=input, output=output)
        messages = [{"role": "user", "content": prompt}]

        # Call the LLM with the prepared messages
        try:
            response = self.llm_client.chat.completions.create(
                model=self.model_name, messages=messages
            )
        except Exception as e:
            raise RuntimeError(f"Error calling LLM API: {str(e)}") from e

        # Parse the response from the LLM
        response_content = (
            response.choices[0].message.content
            if hasattr(response, "choices")
            else response.message.content
        )
        result_json = json.loads(response_content)

        # Return the result as a ScoreResult object with the score and reason
        return score_result.ScoreResult(
            name=self.name, value=result_json["score"], reason=result_json["reason"]
        )


# Example usage
if __name__ == "__main__":
    metric = LLMJudgeMetric()
    metric.score(
        input="Tell me a joke.",
        output="Why did the chicken cross the road? To get to the other side",
    )
