"""Researcher Agent for gathering information using web search"""

from crewai import Agent
from typing import List
from ..tools import FirecrawlSearchTool


def create_researcher_agent(tools: List = None) -> Agent:
    """
    Create a researcher agent that specializes in gathering information from the web
    
    Args:
        tools: Optional list of additional tools for the agent
        
    Returns:
        Agent: Configured researcher agent
    """
    
    # Default tools for the researcher
    default_tools = [FirecrawlSearchTool()]
    
    # Combine with any additional tools provided
    agent_tools = default_tools + (tools or [])
    
    return Agent(
        role="Research Specialist",
        goal="Gather comprehensive and accurate information from web sources to answer user queries",
        backstory=(
            "You are an expert research specialist with years of experience in information gathering "
            "and analysis. You excel at finding relevant, credible sources and extracting key insights "
            "from web content. Your research is thorough, well-organized, and focuses on providing "
            "factual, up-to-date information that directly addresses the user's needs."
        ),
        tools=agent_tools,
        verbose=True,
        allow_delegation=False,
        max_iter=3,
        memory=True
    )