from typing import Optional, Any
from loguru import logger
from crewai import LLM
from crewai.flow.flow import Flow, start, listen, router, or_
from pydantic import BaseModel

from .events import RetrieveEvent, EvaluateEvent, WebSearchEvent, SynthesizeEvent
from src.tools.firecrawl_search_tool import FirecrawlSearchTool
from src.retrieval.retriever_rerank import Retriever
from src.generation.rag import RAG
from config.settings import settings

# Prompt templates for workflow steps
ROUTER_EVALUATION_TEMPLATE = (
    """You are a quality evaluator for RAG responses. Your task is to determine if the given response adequately answers the user's question.

USER QUESTION:
{query}

RAG RESPONSE:
{rag_response}

EVALUATION CRITERIA:
- Does the response directly address the user's question?
- Is the response factually coherent and well-structured?
- Does the response contain sufficient detail to be helpful?
- If the response says "I don't know" or similar, is it because the context truly lacks the information?

Please evaluate the response quality and respond with either:
- "GOOD" - if the response adequately answers the question
- "BAD" - if the response is incomplete, unclear, or doesn't answer the question

IMPORTANT: Respond with ONLY ONE WORD in UPPERCASE: GOOD or BAD. No punctuation or extra text.

Your evaluation (GOOD or BAD):"""
)

QUERY_OPTIMIZATION_TEMPLATE = (
    """Optimize the following query for web search to get the most relevant and accurate results.

Original Query: {query}

Guidelines:
- Make the query more specific and searchable
- Add relevant keywords that would help find authoritative sources
- Keep it concise but comprehensive
- Focus on the core information need

Optimized Query:"""
)

SYNTHESIS_TEMPLATE = (
    """You are a response synthesizer. Create a comprehensive and accurate answer based on the available information.

USER QUESTION:
{query}

RAG RESPONSE (from document knowledge):
{rag_response}

WEB SEARCH RESULTS (additional context):
{web_results}

INSTRUCTIONS:
- Synthesize information from both sources to provide the most complete answer
- Prioritize information from reliable sources
- If there are contradictions, acknowledge them
- Clearly indicate when information comes from web search vs document knowledge
- If web results are empty, refine and improve the RAG response

SYNTHESIZED RESPONSE:"""
)

# Define flow state
class ParalegalAgentState(BaseModel):
    query: str = ""
    top_k: Optional[int] = 3

class ParalegalAgentWorkflow(Flow[ParalegalAgentState]):
    """Paralegal Agent Workflow with router and web search fallback using CrewAI Flows."""

    def __init__(
        self,
        retriever: Retriever,
        rag_system: RAG,
        firecrawl_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(**kwargs)
        self.retriever = retriever
        self.rag = rag_system

        self.openai_api_key = openai_api_key or settings.openai_api_key
        self.llm = LLM(model=settings.llm_model, api_key=self.openai_api_key, temperature=0.1)

    @start()
    def retrieve(self) -> RetrieveEvent:
        """Retrieve relevant documents from vector database"""
        query = self.state.query
        top_k = self.state.top_k

        if not query:
            raise ValueError("Query is required")

        logger.info(f"Retrieving documents for query: {query}")

        retrieved_nodes = self.retriever.search(query, top_k=top_k)
        logger.info(f"Retrieved {len(retrieved_nodes)} documents")
        return RetrieveEvent(retrieved_nodes=retrieved_nodes, query=query)

    @listen(retrieve)
    def generate_rag_response(self, ev: RetrieveEvent) -> EvaluateEvent:
        """Generate initial RAG response"""
        query = ev.query
        retrieved_nodes = ev.retrieved_nodes

        logger.info("Generating RAG response")

        rag_response = self.rag.query(query)

        logger.info("RAG response generated")
        return EvaluateEvent(
            rag_response=rag_response,
            retrieved_nodes=retrieved_nodes,
            query=query
        )

    @router(generate_rag_response)
    def evaluate_response(self, ev: EvaluateEvent) -> str:
        """Evaluate RAG response quality and route accordingly"""
        rag_response = ev.rag_response
        query = ev.query
        
        logger.info("Evaluating RAG response quality")

        evaluation_prompt = ROUTER_EVALUATION_TEMPLATE.format(query=query, rag_response=rag_response)
        resp_text = self.llm.call(evaluation_prompt)
        evaluation = (resp_text or "").strip().upper().split()[0]

        logger.info(f"Evaluation result: {evaluation}")
        return "synthesize" if "GOOD" in evaluation else "web_search"

    @listen("web_search")
    def perform_web_search(self, ev: EvaluateEvent | WebSearchEvent) -> SynthesizeEvent:
        """Perform web search if insufficient information from RAG response"""
        query = ev.query
        rag_response = ev.rag_response
        retrieved_nodes = getattr(ev, "retrieved_nodes", [])
        
        logger.info("Performing web search")
        
        search_results = ""
        try:
            optimization_prompt = QUERY_OPTIMIZATION_TEMPLATE.format(query=query)
            optimized_query = (self.llm.call(optimization_prompt) or query).strip()
            search_results = FirecrawlSearchTool().run(query=optimized_query, limit=3)
            logger.info("Web search completed via custom tool")
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            search_results = "Web search unavailable due to technical issues."
        
        return SynthesizeEvent(
            rag_response=rag_response,
            web_search_results=search_results,
            retrieved_nodes=retrieved_nodes,
            query=query,
            use_web_results=True
        )

    @listen(or_("synthesize", "perform_web_search"))
    def synthesize_response(self, ev: EvaluateEvent | SynthesizeEvent) -> dict:
        """Synthesize final response from RAG and web search results"""
        rag_response = ev.rag_response
        web_results = getattr(ev, "web_search_results", "") or ""
        query = ev.query
        use_web_results = getattr(ev, "use_web_results", False)
        
        logger.info("Synthesizing final response")
        
        if use_web_results and web_results:
            synthesis_prompt = SYNTHESIS_TEMPLATE.format(
                query=query, rag_response=rag_response, web_results=web_results
            )
            synthesized_answer = self.llm.call(synthesis_prompt)
            result = {
                "answer": synthesized_answer,
                "rag_response": rag_response,
                "web_search_used": True,
                "web_results": web_results,
                "query": query,
            }
        else:
            refinement_prompt = (
                f"Improve and refine the following response to make it more helpful and comprehensive:\n\n"
                f"Original Response: {rag_response}\n\nRefined Response:"
            )
            refined = self.llm.call(refinement_prompt)
            result = {
                "answer": refined,
                "rag_response": rag_response,
                "web_search_used": False,
                "web_results": None,
                "query": query,
            }
        
        logger.info("Final response synthesized")
        return result

    async def run_workflow(self, query: str, top_k: Optional[int] = None) -> dict:
        """
        Run the complete flow for a given query.
        
        Args:
            query: User question
            top_k: Number of documents to retrieve
            
        Returns:
            Dictionary with final answer and metadata
        """
        try:
            # Kick off the CrewAI flow asynchronously with runtime inputs
            result = await self.kickoff_async(inputs={"query": query, "top_k": top_k})
            return result if isinstance(result, dict) else {"answer": str(result), "query": query}
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "answer": f"I apologize, but I encountered an error while processing your question: {str(e)}",
                "rag_response": None,
                "web_search_used": False,
                "web_results": None,
                "query": query,
                "error": str(e)
            }