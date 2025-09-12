import json
from crewai import Task
from typing import Dict, Any, Optional

from src.config import ConfigLoader


class Tasks:
    def __init__(self, config_loader: Optional[ConfigLoader] = None):
        self.config_loader = config_loader or ConfigLoader()
    
    def create_rag_search_task(self, query: str, agent) -> Task:
        config = self.config_loader.get_task_config("rag_search_task")
        return Task(
            description=config["description"].format(query=query),
            expected_output=config["expected_output"],
            agent=agent
        )
    
    def create_memory_retrieval_task(self, query: str, agent) -> Task:
        config = self.config_loader.get_task_config("memory_retrieval_task")
        return Task(
            description=config["description"].format(query=query),
            expected_output=config["expected_output"],
            agent=agent
        )
    
    def create_web_search_task(self, query: str, agent) -> Task:
        config = self.config_loader.get_task_config("web_search_task")
        return Task(
            description=config["description"].format(query=query),
            expected_output=config["expected_output"],
            agent=agent
        )
    
    def create_arxiv_search_task(self, query: str, agent) -> Task:
        config = self.config_loader.get_task_config("arxiv_search_task")
        return Task(
            description=config["description"].format(query=query),
            expected_output=config["expected_output"],
            agent=agent
        )
    
    def create_context_evaluation_task(self, query: str, context_sources: Dict[str, Any], agent, output_pydantic=None) -> Task:
        config = self.config_loader.get_task_config("context_evaluation_task")
        formatted_description = config["description"].format(
            query=query,
            rag_result=json.dumps(context_sources.get('rag_result', {}), indent=2),
            memory_result=json.dumps(context_sources.get('memory_result', {}), indent=2),
            web_result=json.dumps(context_sources.get('web_result', {}), indent=2),
            tool_result=json.dumps(context_sources.get('tool_result', {}), indent=2)
        )
        
        task_kwargs = {
            "description": formatted_description,
            "expected_output": config["expected_output"],
            "agent": agent
        }
        
        if output_pydantic:
            task_kwargs["output_pydantic"] = output_pydantic
            
        return Task(**task_kwargs)
    
    def create_synthesis_task(self, query: str, filtered_context: Dict[str, Any], agent) -> Task:
        config = self.config_loader.get_task_config("synthesis_task")
        return Task(
            description=config["description"].format(
                query=query,
                filtered_context=json.dumps(filtered_context, indent=2)
            ),
            expected_output=config["expected_output"],
            agent=agent
        )
