import os
from typing import Optional, Any

from llama_index.core.workflow import (
    StartEvent,
    StopEvent,
    step,
    Workflow,
    Context,
)
from llama_index.core import SummaryIndex
from llama_index.core.schema import Document
from llama_index.core.prompts import PromptTemplate
from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.core.base.base_retriever import BaseRetriever
from llama_index.tools.linkup_research.base import LinkupToolSpec
from typing import List

from llama_index.core.schema import  NodeWithScore
from llama_index.core.workflow import (
    Event,
)

from dotenv import load_dotenv

load_dotenv()

class RetrieveEvent(Event):
    """Retrieve event (gets retrieved nodes)."""

    retrieved_nodes: List[NodeWithScore]



class WebSearchEvent(Event):
    """Web search event."""

    relevant_text: str  # not used, just used for pass through


class QueryEvent(Event):
    """Query event. Queries given relevant text and search text."""

    relevant_text: str
    search_text: str


DEFAULT_RELEVANCY_PROMPT_TEMPLATE = PromptTemplate(
    template="""As a grader, your task is to evaluate the relevance of a document retrieved in response to a user's question.

    Retrieved Document:
    -------------------
    {context_str}

    User Question:
    --------------
    {query_str}

    Evaluation Criteria:
    - Consider whether the document contains keywords or topics related to the user's question.
    - The evaluation should not be overly stringent; the primary objective is to identify and filter out clearly irrelevant retrievals.

    Decision:
    - Assign a binary score to indicate the document's relevance.
    - Use 'yes' if the document is relevant to the question, or 'no' if it is not.

    Please provide your binary score ('yes' or 'no') below to indicate the document's relevance to the user question."""
)

DEFAULT_TRANSFORM_QUERY_TEMPLATE = PromptTemplate(
    template="""Your task is to refine a query to ensure it is highly effective for retrieving relevant search results. \n
    Analyze the given input to grasp the core semantic intent or meaning. \n
    Original Query:
    \n ------- \n
    {query_str}
    \n ------- \n
    Your goal is to rephrase or enhance this query to improve its search performance. Ensure the revised query is concise and directly aligned with the intended search objective. \n
    Respond with the optimized query only:"""
)

class CorrectiveRAGWorkflow(Workflow):
    """Corrective RAG Workflow."""
    def __init__(
        self,
        index,
        linkup_api_key: str,
        llm: Optional[LLM] = None,
        **kwargs: Any
    ) -> None:
        """Init params."""
        super().__init__(**kwargs)
        self.index = index
        self.linkup_tool = LinkupToolSpec(
                                api_key=linkup_api_key,
                                depth="deep", # or "deep"
                                output_type="searchResults", # or "sourcedAnswer" or "structured"
                            )
        self.llm = llm

    @step
    async def retrieve(self, ctx: Context, ev: StartEvent) -> Optional[RetrieveEvent]:
        """Retrieve the relevant nodes for the query."""
        query_str = ev.get("query_str")
        retriever_kwargs = ev.get("retriever_kwargs", {})

        if query_str is None:
            return None

        retriever: BaseRetriever = self.index.as_retriever(**retriever_kwargs)
        result = retriever.retrieve(query_str)
        await ctx.set("retrieved_nodes", result)
        await ctx.set("query_str", query_str)
        return RetrieveEvent(retrieved_nodes=result)

    @step
    async def eval_relevance(
        self, ctx: Context, ev: RetrieveEvent
    ) -> WebSearchEvent | QueryEvent:
        """Evaluate relevancy of retrieved documents with the query."""
        retrieved_nodes = ev.retrieved_nodes
        query_str = await ctx.get("query_str")

        relevancy_results = []
        for node in retrieved_nodes:
            prompt = DEFAULT_RELEVANCY_PROMPT_TEMPLATE.format(context_str=node.text, query_str=query_str)
            relevancy = self.llm.complete(prompt)
            relevancy_results.append(relevancy.text.lower().strip())

        relevant_texts = [
            retrieved_nodes[i].text
            for i, result in enumerate(relevancy_results)
            if result == "yes"
        ]
        relevant_text = "\n".join(relevant_texts)
        if "no" in relevancy_results:
            return WebSearchEvent(relevant_text=relevant_text)
        else:
            return QueryEvent(relevant_text=relevant_text, search_text="")

    @step
    async def web_search(
        self, ctx: Context, ev: WebSearchEvent
    ) -> QueryEvent:
        """Search the transformed query with Tavily API."""
        # If any document is found irrelevant, transform the query string for better search results.

        query_str = await ctx.get("query_str")

        prompt = DEFAULT_TRANSFORM_QUERY_TEMPLATE.format(query_str=query_str)
        result = self.llm.complete(prompt)
        transformed_query_str = result.text
        # Conduct a search with the transformed query string and collect the results.
        search_results = self.linkup_tool.search(transformed_query_str).results
        search_text = "\n".join([result.content for result in search_results])
        return QueryEvent(relevant_text=ev.relevant_text, search_text=search_text)

    @step
    async def query_result(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        """Get result with relevant text."""
        relevant_text = ev.relevant_text
        search_text = ev.search_text
        query_str = await ctx.get("query_str")

        documents = [Document(text=relevant_text + "\n" + search_text)]
        index = SummaryIndex.from_documents(documents)
        query_engine = index.as_query_engine()
        result = query_engine.query(query_str)
        return StopEvent(result=result)
