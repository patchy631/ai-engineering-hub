import os
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from crewai import Crew, Task
from crewai.flow.flow import Flow, listen, start

from src.rag import RAGPipeline
from src.memory import ZepMemoryLayer
from .agents import Agents
from .tasks import Tasks

class ResearchAssistantState(BaseModel):
    query: str = ""
    user_id: str = "default_user"
    thread_id: str = "default_thread"


class ContextEvaluationResult(BaseModel):
    """Pydantic schema for context evaluation agent output validation"""
    relevant_sources: List[str] = Field(
        ..., 
        description="List of source names that are relevant to the query (e.g., 'RAG', 'Memory', 'Web', 'ArXiv')"
    )
    filtered_context: Dict[str, Any] = Field(
        ..., 
        description="Dictionary containing only relevant information from each source, keyed by source name"
    )
    relevance_scores: Dict[str, float] = Field(
        ..., 
        description="Confidence scores (0-1) for each source's relevance to the query"
    )
    reasoning: str = Field(
        ..., 
        description="Brief explanation of filtering decisions and why certain sources were included/excluded"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "relevant_sources": ["RAG", "Web"],
                "filtered_context": {
                    "RAG": {
                        "status": "OK",
                        "answer": "Relevant document context...",
                        "citations": [{"label": "Paper Title", "locator": "chunk_1"}]
                    },
                    "Web": {
                        "status": "OK", 
                        "answer": "Recent web information...",
                        "citations": [{"label": "Article Title", "locator": "https://example.com"}]
                    }
                },
                "relevance_scores": {
                    "RAG": 0.95,
                    "Memory": 0.3,
                    "Web": 0.85,
                    "ArXiv": 0.1
                },
                "reasoning": "RAG and Web sources contain highly relevant information for the query. Memory has some context but low relevance. ArXiv results don't match the specific query focus."
            }
        }


class ResearchAssistantFlow(Flow[ResearchAssistantState]):
    def __init__(
        self,
        tensorlake_api_key: Optional[str] = None,
        voyage_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        zep_api_key: Optional[str] = None,
        firecrawl_api_key: Optional[str] = None,
        milvus_db_path: str = "milvus_lite.db",
    ):
        super().__init__()
        
        self.rag_pipeline = RAGPipeline(
            tensorlake_api_key=tensorlake_api_key,
            voyage_api_key=voyage_api_key,
            openai_api_key=openai_api_key,
            milvus_db_path=milvus_db_path
        )
        
        self.memory_layer = ZepMemoryLayer(
            user_id=self.state.user_id,
            thread_id=self.state.thread_id,
            zep_api_key=zep_api_key
        )
        
        # Initialize tasks and agents
        self.tasks = Tasks()
        self.agents = Agents()
        
        # Create agents
        self.rag_agent = self.agents.create_rag_agent(self.rag_pipeline)
        self.memory_agent = self.agents.create_memory_agent(self.memory_layer)
        self.web_search_agent = self.agents.create_web_search_agent(firecrawl_api_key or os.getenv("FIRECRAWL_API_KEY"))
        self.tool_calling_agent = self.agents.create_arxiv_agent()
        self.evaluator_agent = self.agents.create_evaluator_agent()
        self.synthesizer_agent = self.agents.create_synthesizer_agent()
    
    @start()
    def process_query(self) -> Dict[str, Any]:
        query = self.state.query
        
        # Save user query to memory
        summarized_query = self._summarize_for_memory(query, max_length=1500)
        self.memory_layer.save_user_message(summarized_query)
        
        return {
            "query": query,
            "status": "processing"
        }
    
    @listen(process_query)
    def gather_context_from_all_sources(self, flow_state: Dict[str, Any]) -> Dict[str, Any]:
        query = flow_state["query"]
        
        # Create tasks for each agent
        rag_task = self.tasks.create_rag_search_task(query, self.rag_agent)
        
        memory_task = self.tasks.create_memory_retrieval_task(query, self.memory_agent)
        web_search_task = self.tasks.create_web_search_task(query, self.web_search_agent)
        tool_calling_task = self.tasks.create_arxiv_search_task(query, self.tool_calling_agent)
        
        context_crew = Crew(
            agents=[self.rag_agent, self.memory_agent, self.web_search_agent, self.tool_calling_agent],
            tasks=[rag_task, memory_task, web_search_task, tool_calling_task],
            verbose=True
        )
        
        results = context_crew.kickoff()
        
        # Parse results from each agent
        context_sources = {
            "rag_result": self._parse_agent_result(results.tasks_output[0].raw),
            "memory_result": self._parse_agent_result(results.tasks_output[1].raw),
            "web_result": self._parse_agent_result(results.tasks_output[2].raw),
            "tool_result": self._parse_agent_result(results.tasks_output[3].raw)
        }
        
        return {
            **flow_state,
            "context_sources": context_sources,
            "raw_results": [task.raw for task in results.tasks_output]
        }
    
    @listen(gather_context_from_all_sources)
    def evaluate_context_relevance(self, flow_state: Dict[str, Any]) -> Dict[str, Any]:
        query = flow_state["query"]
        context_sources = flow_state["context_sources"]
        
        evaluation_task = self.tasks.create_context_evaluation_task(
            query, context_sources, self.evaluator_agent, ContextEvaluationResult
        )
        
        evaluation_crew = Crew(
            agents=[self.evaluator_agent],
            tasks=[evaluation_task],
            verbose=True
        )
        
        evaluation_result = evaluation_crew.kickoff()
        evaluation_output = evaluation_result.tasks_output[0].pydantic
        
        if isinstance(evaluation_output, ContextEvaluationResult):
            filtered_context = evaluation_output.filtered_context
            evaluation_data = evaluation_output.model_dump()
        else:
            print("Pydantic output not available, falling back to raw parsing")
            filtered_context = self._parse_agent_result(evaluation_result.tasks_output[0].raw)
            evaluation_data = {"raw_fallback": evaluation_result.tasks_output[0].raw}
        
        return {
            **flow_state,
            "filtered_context": filtered_context,
            "evaluation_result": evaluation_data,
            "evaluation_raw": evaluation_result.tasks_output[0].raw
        }
    
    @listen(evaluate_context_relevance)
    def synthesize_final_response(self, flow_state: Dict[str, Any]) -> Dict[str, Any]:
        query = flow_state["query"]
        filtered_context = flow_state["filtered_context"]
        
        synthesis_task = self.tasks.create_synthesis_task(
            query, filtered_context, self.synthesizer_agent
        )
        
        synthesis_crew = Crew(
            agents=[self.synthesizer_agent],
            tasks=[synthesis_task],
            verbose=True
        )
        
        synthesis_result = synthesis_crew.kickoff()
        final_response = synthesis_result.tasks_output[0].raw
        
        # Save summarized assistant response to memory
        summarized_response = self._summarize_for_memory(final_response)
        self.memory_layer.save_assistant_message(summarized_response)
        
        return {
            **flow_state,
            "final_response": final_response,
            "synthesis_raw": final_response,
            "status": "completed"
        }
    
    def _parse_agent_result(self, raw_result: str) -> Dict[str, Any]:
        try:
            return json.loads(raw_result)
        except json.JSONDecodeError:
            return {
                "status": "OK",
                "source_used": "UNKNOWN",
                "answer": raw_result,
                "citations": [],
                "confidence": 0.5
            }
    
    def _summarize_for_memory(self, response: str, max_length: int = 2000) -> str:
        if len(response) <= max_length:
            return response
        
        truncated = response[:max_length]
        last_period = truncated.rfind('.')
        last_exclamation = truncated.rfind('!')
        last_question = truncated.rfind('?')
        last_sentence_end = max(last_period, last_exclamation, last_question)
        
        if last_sentence_end > max_length * 0.7: 
            return truncated[:last_sentence_end + 1] + " [Response truncated for memory storage]"
        else:
            last_space = truncated.rfind(' ')
            if last_space > max_length * 0.8:
                return truncated[:last_space] + "... [Response truncated for memory storage]"
            else:
                return truncated + "... [Response truncated for memory storage]"
    
    def process_documents(self, document_paths: List[str]) -> Dict[str, Any]:
        return self.rag_pipeline.process_documents(document_paths)


def create_research_assistant_flow(**kwargs) -> ResearchAssistantFlow:
    return ResearchAssistantFlow(**kwargs)
