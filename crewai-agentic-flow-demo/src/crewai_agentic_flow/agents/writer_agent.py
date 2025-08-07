"""Writer Agent for generating comprehensive answers based on research data"""

from crewai import Agent
from typing import List


def create_writer_agent(tools: List = None) -> Agent:
    """
    Create a writer agent that specializes in synthesizing research into comprehensive answers
    
    Args:
        tools: Optional list of additional tools for the agent
        
    Returns:
        Agent: Configured writer agent
    """
    
    # Writer typically doesn't need special tools, but can accept them
    agent_tools = tools or []
    
    return Agent(
        role="Content Writer and Synthesizer",
        goal="Create comprehensive, well-structured answers by synthesizing research findings",
        backstory=(
            "You are an experienced content writer and information synthesizer with expertise in "
            "transforming complex research data into clear, comprehensive, and engaging content. "
            "You excel at identifying key themes, organizing information logically, and presenting "
            "findings in a way that is both informative and accessible to your target audience. "
            "Your writing is precise, well-structured, and always backed by credible sources."
        ),
        tools=agent_tools,
        verbose=True,
        allow_delegation=False,
        max_iter=2,
        memory=True
    )