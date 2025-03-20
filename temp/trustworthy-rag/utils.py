from typing import Dict, List, ClassVar
from llama_index.core.instrumentation.events import BaseEvent
from llama_index.core.instrumentation.event_handlers import BaseEventHandler
from llama_index.core.instrumentation import get_dispatcher
from llama_index.core.instrumentation.events.llm import LLMCompletionEndEvent


class GetTrustworthinessScoreAndReasoning(BaseEventHandler):
    events: ClassVar[List[BaseEvent]] = []
    trustworthiness_score: float = 0.0
    reasoning: str = ""

    @classmethod
    def class_name(cls) -> str:
        """Class name."""
        return "GetTrustworthinessScoreAndReasoning"

    def handle(self, event: BaseEvent) -> Dict:
        if isinstance(event, LLMCompletionEndEvent):
            self.trustworthiness_score = event.response.additional_kwargs[
                "trustworthiness_score"
            ]
            self.reasoning = event.response.additional_kwargs[
                "explanation"
            ]
            self.events.append(event)


def setup_trustworthiness_handler():
    """Initialize and register the trustworthiness event handler."""
    root_dispatcher = get_dispatcher()
    event_handler = GetTrustworthinessScoreAndReasoning()
    root_dispatcher.add_event_handler(event_handler)
    return event_handler


def display_response(response, event_handler):
    """Display the response along with trustworthiness information."""
    response_str = response.response
    trustworthiness_score = event_handler.trustworthiness_score
    reasoning = event_handler.reasoning
    print(f"Response: {response_str}")
    print(f"Trustworthiness score: {round(trustworthiness_score, 2)}")
    print(f"Reasoning: {reasoning}")

def outputs_with_trustworthiness(response, event_handler):
    """Display the response along with trustworthiness information."""
    response_str = response.response
    trustworthiness_score = event_handler.trustworthiness_score
    reasoning = event_handler.reasoning
    return response_str, trustworthiness_score, reasoning