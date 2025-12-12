import streamlit as st
from datetime import datetime
import json
from ..workflow.events import LogEvent, PolicyQueryEvent

def format_workflow_step(step_number, step_name, description, status="pending"):
    """Format a workflow step for display."""
    colors = {
        "pending": "gray",
        "in_progress": "blue",
        "completed": "green",
        "error": "red"
    }
    icons = {
        "pending": "⭕",
        "in_progress": "🔄",
        "completed": "✅",
        "error": "❌"
    }
    return f"""
    <div style="padding: 10px; margin: 5px 0; border-left: 3px solid {colors[status]};">
        <p style="margin: 0; color: {colors[status]};">
            {icons[status]} Step {step_number}: <strong>{step_name}</strong>
        </p>
        <p style="margin: 5px 0 0 25px; font-size: 0.9em; color: #666;">
            {description}
        </p>
    </div>
    """

def display_policy_content(policy_text):
    """Display policy content in expandable sections."""
    sections = policy_text.split("\n\n")
    for i, section in enumerate(sections):
        if section.strip():
            with st.expander(f"Section {i+1}"):
                st.markdown(section)

class StreamlitEventHandler:
    def __init__(self, progress_container, details_container):
        self.progress_container = progress_container
        self.details_container = details_container
        self.current_step = 0
        self.policy_queries = []  # Store policy queries
        self.retrieval_queries = []  # Store retrieval queries
        self.steps = [
            ("Loading Claim Info", "Parsing and validating claim information"),
            ("Generating Policy Queries", "Creating targeted queries to search policy documents"),
            ("Retrieving Policy Sections", "Searching for relevant policy sections"),
            ("Generating Recommendation", "Analyzing claim against policy terms"),
            ("Finalizing Decision", "Determining coverage and calculating payout")
        ]
        self.display_initial_steps()

    def display_initial_steps(self):
        """Display the initial workflow steps."""
        steps_html = ""
        for i, (step_name, description) in enumerate(self.steps, 1):
            steps_html += format_workflow_step(i, step_name, description)
        self.progress_container.markdown(steps_html, unsafe_allow_html=True)

    def update_progress(self, step_index, status="in_progress"):
        """Update the progress display."""
        steps_html = ""
        for i, (step_name, description) in enumerate(self.steps, 1):
            if i < step_index:
                current_status = "completed"
            elif i == step_index:
                current_status = status
            else:
                current_status = "pending"
            steps_html += format_workflow_step(i, step_name, description, current_status)
        self.progress_container.markdown(steps_html, unsafe_allow_html=True)

    def display_queries(self):
        """Display policy and retrieval queries."""
        with self.details_container.expander("📝 Policy Analysis Queries", expanded=True):
            # Display policy queries
            if self.policy_queries:
                st.markdown("### Initial Policy Queries")
                st.markdown("""
                <div style="margin-bottom: 10px; padding: 10px; background-color: #e3f2fd; border-radius: 5px;">
                    <p style="margin: 0;"><strong>💡 About these queries:</strong></p>
                    <p style="margin: 5px 0;">These are the initial queries generated to identify relevant policy sections based on the claim details.</p>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, query in enumerate(self.policy_queries, 1):
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: #f0f2f6; border-radius: 5px; margin: 5px 0;">
                        <p style="color: #1a237e; margin: 0;"><strong>Policy Query {idx}:</strong></p>
                        <p style="margin: 5px 0 0 20px;">{query}</p>
                    </div>
                    """, unsafe_allow_html=True)

            # Display retrieval queries
            if self.retrieval_queries:
                st.markdown("### Document Retrieval Queries")
                st.markdown("""
                <div style="margin-bottom: 10px; padding: 10px; background-color: #e3f2fd; border-radius: 5px;">
                    <p style="margin: 0;"><strong>💡 About these queries:</strong></p>
                    <p style="margin: 5px 0;">These queries are used to search and retrieve specific sections from the policy document.</p>
                </div>
                """, unsafe_allow_html=True)
                
                for idx, query in enumerate(self.retrieval_queries, 1):
                    st.markdown(f"""
                    <div style="padding: 10px; background-color: #f3e5f5; border-radius: 5px; margin: 5px 0;">
                        <p style="color: #4a148c; margin: 0;"><strong>Retrieval Query {idx}:</strong></p>
                        <p style="margin: 5px 0 0 20px;">{query}</p>
                    </div>
                    """, unsafe_allow_html=True)

    async def handle_event(self, event):
        """Handle workflow events and update the UI accordingly."""
        if isinstance(event, LogEvent):
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if "Loading Claim Info" in event.msg:
                self.current_step = 1
                self.update_progress(1)
            elif "Generating Policy Queries" in event.msg:
                self.current_step = 2
                self.update_progress(2)
            elif "Retrieving policy sections" in event.msg:
                self.current_step = 3
                self.update_progress(3)
            elif "Generating Policy Recommendation" in event.msg:
                self.current_step = 4
                self.update_progress(4)
            elif "Finalizing Decision" in event.msg:
                self.current_step = 5
                self.update_progress(5)
            
            # Format and display detailed information
            if "Query:" in event.msg:
                query = event.msg.split("Query:")[1].strip()
                self.retrieval_queries.append(query)
                self.display_queries()
            
            elif "Recommendation:" in event.msg:
                try:
                    rec_data = json.loads(event.msg.split("Recommendation:")[1].strip())
                    with self.details_container.expander("📋 Initial Recommendation", expanded=True):
                        st.markdown(f"""
                        <div style="padding: 10px; background-color: #e8f4ea; border-radius: 5px; margin: 5px 0;">
                            <p style="color: #2e7d32; margin: 0;">📋 <strong>Initial Recommendation:</strong></p>
                            <ul style="margin: 5px 0 0 20px;">
                                <li>Section: {rec_data['policy_section']}</li>
                                <li>Summary: {rec_data['recommendation_summary']}</li>
                                <li>Deductible: ${rec_data.get('deductible', 0):.2f}</li>
                                <li>Settlement: ${rec_data.get('settlement_amount', 0):.2f}</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                except json.JSONDecodeError as e:
                    self.details_container.markdown(f"Error parsing recommendation JSON: {e}")
                    self.details_container.markdown(event.msg)
                except KeyError as e:
                    self.details_container.markdown(f"Missing required field in recommendation data: {e}")
                    self.details_container.markdown(f"Available fields: {list(rec_data.keys()) if 'rec_data' in locals() else 'None'}")
                except Exception as e:
                    self.details_container.markdown(f"Unexpected error processing recommendation: {str(e)}")
                    self.details_container.markdown(event.msg)
            else:
                with self.details_container.expander("🔄 Processing Log", expanded=True):
                    st.markdown(f"⏱️ `{timestamp}` {event.msg}")
        
        elif isinstance(event, PolicyQueryEvent):
            # Store the policy queries when they're generated
            self.policy_queries = event.queries.queries
            self.display_queries() 
