"""Research Flow using CrewAI Flows for orchestrating Researcher and Writer agents"""

from typing import Dict, Any
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start
from crewai import Crew, Task

from ..agents import create_researcher_agent, create_writer_agent


class FlowState(BaseModel):
    """Structured state model for the research flow"""
    query: str = ""
    research_findings: str = ""
    final_answer: str = ""


class ResearchFlow(Flow[FlowState]):
    """
    Agentic workflow that orchestrates research and writing tasks
    
    This flow demonstrates:
    1. Starting with a user query
    2. Using a Researcher agent to gather information
    3. Using a Writer agent to synthesize the findings into a comprehensive answer
    """

    def __init__(self):
        super().__init__()
        
        # Initialize agents
        self.researcher = create_researcher_agent()
        self.writer = create_writer_agent()

    @start()
    def initialize_research(self) -> str:
        """
        Initialize the research flow with a user query
        
        Returns:
            str: The initial query to be processed
        """
        query = self.state.query
        print(f"🔍 Starting research flow for query: '{query}'")
        
        # Store the query in state for downstream tasks
        self.state.query = query
        
        return query

    @listen(initialize_research)
    def conduct_research(self, query: str) -> str:
        """
        Conduct research using the Researcher agent
        
        Args:
            query: The research query from the previous step
            
        Returns:
            str: Research findings
        """
        print(f"📚 Conducting research on: '{query}'")
        
        # Create a research task
        research_task = Task(
            description=(
                f"Conduct comprehensive research on the following query: '{query}'. "
                "Use the Firecrawl search tool to gather relevant information from multiple sources. "
                "Focus on finding accurate, up-to-date, and credible information. "
                "Organize your findings clearly and include source URLs where applicable."
            ),
            agent=self.researcher,
            expected_output=(
                "A comprehensive research report containing:\n"
                "1. Key findings and insights\n"
                "2. Multiple perspectives on the topic\n"
                "3. Relevant data, statistics, or examples\n"
                "4. Source URLs and credibility assessment\n"
                "5. Summary of main themes discovered"
            )
        )
        
        # Create a crew with just the researcher for this task
        research_crew = Crew(
            agents=[self.researcher],
            tasks=[research_task],
            verbose=True
        )
        
        # Execute the research
        research_findings = research_crew.kickoff()
        
        # Store findings in state
        self.state.research_findings = str(research_findings)
        
        print("✅ Research completed")
        return str(research_findings)

    @listen(conduct_research)
    def generate_answer(self, research_findings: str) -> str:
        """
        Generate a comprehensive answer using the Writer agent
        
        Args:
            research_findings: Research results from the previous step
            
        Returns:
            str: Final comprehensive answer
        """
        print("✍️ Generating comprehensive answer...")
        
        original_query = self.state.query
        
        # Create a writing task
        writing_task = Task(
            description=(
                f"Based on the research findings provided, create a comprehensive answer "
                f"to the original query: '{original_query}'. "
                "Synthesize the research data into a well-structured, informative response. "
                "Ensure the answer is accurate, complete, and addresses all aspects of the query. "
                f"Research findings to synthesize:\n\n{research_findings}"
            ),
            agent=self.writer,
            expected_output=(
                "A comprehensive, well-structured answer that includes:\n"
                "1. Clear introduction addressing the query\n"
                "2. Main body with key information organized logically\n"
                "3. Supporting evidence and examples from research\n"
                "4. Conclusion that summarizes key takeaways\n"
                "5. References to sources when applicable\n"
                "The answer should be informative, accurate, and easy to understand."
            )
        )
        
        # Create a crew with just the writer for this task
        writing_crew = Crew(
            agents=[self.writer],
            tasks=[writing_task],
            verbose=True
        )
        
        # Execute the writing task
        final_answer = writing_crew.kickoff()
        
        # Store final answer in state
        self.state.final_answer = str(final_answer)
        
        print("✅ Answer generation completed")
        print(f"📄 Final answer ready!")
        
        return str(final_answer)

    def run_flow(self, query: str) -> Dict[str, Any]:
        """
        Convenience method to run the complete flow
        
        Args:
            query: The research query
            
        Returns:
            Dict containing the complete flow results
        """
        # Initialize state
        self.state = FlowState(query=query)
        
        # Start the flow
        result = self.kickoff()
        
        # Return comprehensive results
        return {
            "query": self.state.query,
            "research_findings": self.state.research_findings,
            "final_answer": self.state.final_answer,
            "flow_result": result
        }