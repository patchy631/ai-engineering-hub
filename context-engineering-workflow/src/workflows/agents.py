import os
from crewai import Agent
from typing import Optional

from src.config import ConfigLoader
from src.tools import (
    RAGTool, 
    MemoryTool, 
    ArxivTool, 
    FirecrawlSearchTool
)
from src.rag import RAGPipeline
from src.memory import ZepMemoryLayer


class AgentFactory:
    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        self.config_loader = config_loader or ConfigLoader()
    
    def create_rag_agent(self, rag_pipeline: RAGPipeline) -> Agent:
        config = self.config_loader.get_agent_config("rag_agent")
        rag_tool = RAGTool(rag_pipeline=rag_pipeline)
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[rag_tool],
            verbose=config.get("verbose", True)
        )
    
    def create_memory_agent(self, memory_layer: ZepMemoryLayer) -> Agent:
        config = self.config_loader.get_agent_config("memory_agent")
        memory_tool = MemoryTool(memory_layer=memory_layer)
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[memory_tool],
            verbose=config.get("verbose", True)
        )
    
    def create_web_search_agent(self, firecrawl_api_key: str) -> Agent:
        config = self.config_loader.get_agent_config("web_search_agent")
        web_search_tool = FirecrawlSearchTool(api_key=firecrawl_api_key)
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[web_search_tool],
            verbose=config.get("verbose", True)
        )
    
    def create_arxiv_agent(self) -> Agent:
        config = self.config_loader.get_agent_config("arxiv_agent")
        arxiv_tool = ArxivTool()
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            tools=[arxiv_tool],
            verbose=config.get("verbose", True)
        )
    
    def create_evaluator_agent(self) -> Agent:
        config = self.config_loader.get_agent_config("evaluator_agent")
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config.get("verbose", True)
        )
    
    def create_synthesizer_agent(self) -> Agent:
        config = self.config_loader.get_agent_config("synthesizer_agent")
        return Agent(
            role=config["role"],
            goal=config["goal"],
            backstory=config["backstory"],
            verbose=config.get("verbose", True)
        )

def create_rag_agent(rag_pipeline: RAGPipeline) -> Agent:
    """Create RAG agent for document-based retrieval and processing"""
    factory = AgentFactory()
    return factory.create_rag_agent(rag_pipeline)


def create_memory_agent(memory_layer: ZepMemoryLayer) -> Agent:
    """Create memory agent for conversation history retrieval"""
    factory = AgentFactory()
    return factory.create_memory_agent(memory_layer)


def create_web_search_agent(firecrawl_api_key: str) -> Agent:
    """Create web search agent using Firecrawl"""
    factory = AgentFactory()
    return factory.create_web_search_agent(firecrawl_api_key)


def create_tool_calling_agent() -> Agent:
    """Create ArXiv research agent for academic paper search"""
    factory = AgentFactory()
    return factory.create_arxiv_agent()


def create_evaluator_agent() -> Agent:
    """Create evaluator agent to filter and rank context relevance"""
    factory = AgentFactory()
    return factory.create_evaluator_agent()


def create_synthesizer_agent() -> Agent:
    """Create synthesizer agent to generate coherent final responses"""
    factory = AgentFactory()
    return factory.create_synthesizer_agent()

from src.tools import RAGTool, MemoryTool, ArxivTool as ExternalAPITool

__all__ = [
    "AgentFactory",
    "create_rag_agent",
    "create_memory_agent",
    "create_web_search_agent", 
    "create_tool_calling_agent",
    "create_evaluator_agent",
    "create_synthesizer_agent",
    "RAGTool",
    "MemoryTool", 
    "ExternalAPITool"
]
