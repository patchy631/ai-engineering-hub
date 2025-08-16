from typing import Optional
from loguru import logger
from crewai import LLM
from pydantic import BaseModel
from src.retrieval.retriever_rerank import Retriever
from config.settings import settings

class ChatMessage(BaseModel):
    role: str
    content: str

class RAG: 
    def __init__(
        self, 
        retriever: Retriever, 
        llm_model: str = None,
        openai_api_key: str = None,
        temperature: float = None,
        max_tokens: int = None
    ):
        self.retriever = retriever
        self.llm_model = llm_model or settings.llm_model
        self.openai_api_key = openai_api_key or settings.openai_api_key
        self.temperature = temperature or settings.temperature
        self.max_tokens = max_tokens or settings.max_tokens
        
        # Initialize LLM
        self.llm = self._setup_llm()
        
        # System message
        self.system_message = ChatMessage(
            role="system",
            content="You are a helpful assistant that answers questions based on the provided context. "
                   "Always base your answers on the given information and clearly indicate when you don't know something."
        )
        
        # RAG prompt template
        self.prompt_template = (
            "CONTEXT:\n"
            "{context}\n"
            "---------------------\n"
            "Based on the context information above, please answer the following question. "
            "If the context doesn't contain enough information to answer the question, or "
            "even if you know the answer, but it is not relevant to the provided context, "
            "clearly state that you don't know and explain what information is missing.\n\n"
            "QUESTION: {query}\n"
            "ANSWER: "
        )

    def _setup_llm(self):
        if not self.openai_api_key:
            raise ValueError(
                "OpenAI API key is required. Set OPENAI_API_KEY environment variable "
                "or pass openai_api_key parameter."
            )
        llm = LLM(model=self.llm_model, api_key=self.openai_api_key, temperature=self.temperature)
        logger.info(f"Initialized CrewAI LLM with model: {self.llm_model}")
        return llm

    def generate_context(self, query: str, top_k: Optional[int] = None):
        # Generate context from retrieval results
        return self.retriever.get_combined_context(query, top_k)

    def query(self, query: str, top_k: Optional[int] = None):
        # Generate context from retrieval
        context = self.generate_context(query, top_k)
        
        # Create prompt from template
        prompt = self.prompt_template.format(context=context, query=query)
        return self.llm.call(f"{self.system_message.content}\n\n{prompt}")

    def get_detailed_response(self, query: str, top_k: Optional[int] = None):
        # Get retrieval results with scores
        retrieval_results = self.retriever.search_with_scores(query, top_k)
        
        # Generate context
        context = self.retriever.get_combined_context(query, top_k)
        
        # Generate response
        response = self.query(query, top_k=top_k)
        
        return {
            "response": response,
            "context": context,
            "sources": retrieval_results,
            "query": query,
            "model": self.llm_model
        }

    def set_prompt_template(self, template: str):
        # Set custom prompt template
        self.prompt_template = template
        logger.info("Updated prompt template")

    def set_system_message(self, content: str):
        # Set custom system message
        self.system_message = ChatMessage(role="system", content=content)
        logger.info("Updated system message")