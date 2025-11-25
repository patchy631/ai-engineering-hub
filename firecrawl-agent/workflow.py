import os
from typing import Optional, Any
import re
import requests

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
from llama_index.llms.openai import OpenAI
from llama_index.core.llms import LLM
from llama_index.core.base.base_retriever import BaseRetriever
from typing import List

from llama_index.core.schema import NodeWithScore
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
        firecrawl_api_key: str,
        llm: Optional[LLM] = None,
        **kwargs: Any
    ) -> None:
        """Init params."""
        super().__init__(**kwargs)
        self.index = index
        self.firecrawl_api_key = firecrawl_api_key
        
        if llm is not None:
            self.llm = llm
        else:
            # self.llm = Ollama(
            #     model="gemma3:4b",
            #     base_url="http://localhost:11434",
            #     temperature=0.1,
            # )
            self.llm = OpenAI(
                model="gpt-4o",
                api_key=os.getenv("OPENAI_API_KEY"),
            )
        
        # Set the global LLM settings to avoid conflicts
        from llama_index.core import Settings
        Settings.llm = self.llm

    @step
    async def retrieve(self, ctx: Context, ev: StartEvent) -> Optional[RetrieveEvent]:
        """Retrieve the relevant nodes for the query."""
        query_str = ev.get("query_str")
        retriever_kwargs = ev.get("retriever_kwargs", {})

        print(f"DEBUG: retrieve - query_str: {query_str}")
        print(f"DEBUG: retrieve - retriever_kwargs: {retriever_kwargs}")

        if query_str is None:
            print("DEBUG: retrieve - query_str is None, returning None")
            return None

        retriever: BaseRetriever = self.index.as_retriever(**retriever_kwargs)
        print(f"DEBUG: retrieve - retriever created: {type(retriever)}")
        
        result = retriever.retrieve(query_str)
        print(f"DEBUG: retrieve - retrieved {len(result)} nodes")
        
        if result:
            print(f"DEBUG: retrieve - first node preview: {result[0].text[:100]}...")
        
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

        print(f"DEBUG: Retrieved {len(retrieved_nodes)} nodes")
        print(f"DEBUG: Query: {query_str}")

        relevancy_results = []
        for i, node in enumerate(retrieved_nodes):
            print(f"DEBUG: Node {i} text preview: {node.text[:100]}...")
            prompt = DEFAULT_RELEVANCY_PROMPT_TEMPLATE.format(
                context_str=node.text, query_str=query_str)
            try:
                relevancy = await self.llm.acomplete(prompt)
                relevancy_results.append(relevancy.text.lower().strip())
                print(f"DEBUG: Node {i} relevancy: {relevancy.text}")
            except Exception as e:
                # Fallback to synchronous call if async is not supported
                relevancy = self.llm.complete(prompt)
                relevancy_results.append(relevancy.text.lower().strip())
                print(f"DEBUG: Node {i} relevancy (sync): {relevancy.text}")

        print(f"DEBUG: All relevancy results: {relevancy_results}")

        relevancy_results_striped = [re.sub(r"<think>.*?</think>", "", s, flags=re.DOTALL).strip() for s in relevancy_results]

        # Improved relevancy parsing - look for "yes" anywhere in the response
        relevant_texts = [
            retrieved_nodes[i].text
            for i, result in enumerate(relevancy_results_striped)
            if "yes" in result.lower()
        ]
        relevant_text = "\n".join(relevant_texts)
        
        print(f"DEBUG: Relevant texts count: {len(relevant_texts)}")
        print(f"DEBUG: Relevant text preview: {relevant_text[:200]}...")
        
        if "no" in relevancy_results_striped:
            print("DEBUG: Some documents irrelevant, returning WebSearchEvent")
            return WebSearchEvent(relevant_text=relevant_text)
        else:
            print("DEBUG: All documents relevant, returning QueryEvent")
            return QueryEvent(relevant_text=relevant_text, search_text="")

    def _firecrawl_search(self, query: str, limit: int = 5) -> str:
        """Perform web search using FireCrawl API directly."""
        url = "https://api.firecrawl.dev/v1/search"
        
        payload = {
            "query": query,
            "limit": 5,
            "timeout": 60000,
        }
        
        headers = {
            "Authorization": f"Bearer {self.firecrawl_api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success") and data.get("data"):
                # Extract title and description from each result
                search_results = []
                for result in data["data"]:
                    title = result.get("title", "")
                    description = result.get("description", "")
                    url = result.get("url", "")
                    
                    if title or description:
                        result_text = f"Title: {title}\nDescription: {description}\nURL: {url}\n"
                        search_results.append(result_text)
                
                return "\n---\n".join(search_results)
            else:
                print(f"DEBUG: FireCrawl API returned no results or error: {data}")
                return ""
                
        except requests.exceptions.RequestException as e:
            print(f"DEBUG: FireCrawl API request failed: {e}")
            return ""
        except Exception as e:
            print(f"DEBUG: Unexpected error in FireCrawl search: {e}")
            return ""

    @step
    async def web_search(
        self, ctx: Context, ev: WebSearchEvent
    ) -> QueryEvent:
        """Search the transformed query"""
        # If any document is found irrelevant, transform the query string for better search results.

        query_str = await ctx.get("query_str")

        prompt = DEFAULT_TRANSFORM_QUERY_TEMPLATE.format(query_str=query_str)
        try:
            result = await self.llm.acomplete(prompt)
            transformed_query_str = result.text
        except Exception as e:
            # Fallback to synchronous call if async is not supported
            result = self.llm.complete(prompt)
            transformed_query_str = result.text
            
        print(f"DEBUG: web_search - transformed query: {transformed_query_str}")
        
        # Conduct a search with the transformed query string using direct API call
        search_text = self._firecrawl_search(transformed_query_str)
        
        print(f"DEBUG: web_search - search results length: {len(search_text)}")
        if search_text:
            print(f"DEBUG: web_search - search results preview: {search_text[:200]}...")
        
        return QueryEvent(relevant_text=ev.relevant_text, search_text=search_text)

    @step
    async def query_result(self, ctx: Context, ev: QueryEvent) -> StopEvent:
        """Get result with relevant text."""
        relevant_text = ev.relevant_text
        search_text = ev.search_text
        query_str = await ctx.get("query_str")

        print(f"DEBUG: query_result - query_str: {query_str}")
        print(f"DEBUG: query_result - relevant_text: {relevant_text}")
        print(f"DEBUG: query_result - search_text: {search_text}")

        if not relevant_text.strip() and not search_text.strip():
            print("DEBUG: No relevant text, returning empty response")
            return StopEvent(result="No relevant information found in the documents.")
        

        context_str = relevant_text + "\n" + search_text

        prompt = f"""As a helpful assistant, your task is to answer the user's question based on the given context.

        A few things to keep in mind:
        - The context can either be relevant text or web search results.
        - The context can also be a mix of both.

        Your task is to look at the query and the whole context and generate what you think is the best answer to the question.

        Here is the context:
        Context:
        {context_str}

        --------------------------------

        Question:
        {query_str}

        --------------------------------

        Generate an answer to the question:
        """

        result = await self.llm.acomplete(prompt)
        print(f"DEBUG: query_result - final result: {result.text}")
        return StopEvent(result=result.text)
