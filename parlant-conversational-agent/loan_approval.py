import asyncio
import parlant.sdk as p
from dotenv import load_dotenv

load_dotenv()


@p.tool
async def check_eligibility(context: p.ToolContext, credit_score: int, income: float, loan_amount: float) -> p.ToolResult:
    """
    Checks if the customer meets the basic qualification criteria for a loan.
    """
    # Simulate a business logic check for eligibility
    if credit_score >= 680 and income >= 50000 and loan_amount <= 500000:
        return p.ToolResult(data={"is_eligible": True})
    else:
        # Provide reason for ineligibility
        reason = "insufficient credit score" if credit_score < 680 else "income criteria does not meet the requirements"
        return p.ToolResult(data={"is_eligible": False, "reason": reason})

@p.tool
async def process_documents(context: p.ToolContext, document_list: list) -> p.ToolResult:
    """
    Simulates a service that processes and validates uploaded documents.
    """
    # Simulate document processing and validation logic
    # We add a condition to simulate a document failing the validation
    if "tax_returns.pdf" in document_list and "pay_stubs.pdf" in document_list:
        # Assume one document is found to be inaccurate, a common real-world scenario
        if "inaccurate_info" in document_list:
            return p.ToolResult(data={"documents_processed": False, "reason": "inaccurate information"})
        else:
            return p.ToolResult(data={"documents_processed": True})
    else:
        # Case for when the expected documents are not provided
        return p.ToolResult(data={"documents_processed": False, "reason": "missing documents"})

@p.tool
async def get_current_rates(context: p.ToolContext, zip_code: str) -> p.ToolResult:
    """
    Fetches the current loan interest rates based on the customer's location.
    """
    # Simulate an API call to get dynamic rates
    return p.ToolResult(data={"rates": {"30-year-fixed": "6.2%", "15-year-fixed": "5.8%"}})

@p.tool
async def get_loan_types(context: p.ToolContext) -> p.ToolResult:
    """
    Provides a list of available loan types.
    """
    return p.ToolResult(data=["Home Loan", "Personal Loan", "Auto Loan", "Mortgage", "Refinancing"])


async def add_domain_glossary(agent: p.Agent) -> None:
    """
    Adds domain-specific terminology to align the agent's understanding with
    financial services concepts and brand voice.
    """
    await agent.create_term(
        name="Customer Care Phone Number",
        description="The direct line for human assistance, at +1-234-567-8900",
    )
    await agent.create_term(
        name="Loan Specialist",
        description="A specific term to use when referring to human experts who handle loan applications.",
    )
    await agent.create_term(
        name="Loan Operations",
        description="The official department name to refer to in legal disclaimers.",
    )
    await agent.create_term(
        name="Online Portal",
        description="The online platform where customers can manage their application and upload documents manually."
    )
    # Define financial concepts to prevent misinformation
    await agent.create_term(name="APR", description="Annual Percentage Rate")
    await agent.create_term(name="LTV", description="Loan-to-Value ratio")
    await agent.create_term(name="Loan Qualification", description="A preliminary estimate, not a guaranteed loan")


async def create_loan_journey(agent: p.Agent) -> p.Journey:
    """
    Defines the structured, multi-step journey for loan approval.
    """
    journey = await agent.create_journey(
        title="Loan Approval",
        description="Guides a potential borrower through a two-stage loan approval process.",
        conditions=["The customer asks about loans or related financial services"],
    )

    # Ask the customer what type of loan they are interested in
    t0 = await journey.initial_state.transition_to(
        chat_state="Determine the type of loan user is interested in"
    )

    # Collect initial details from the user
    t1 = await t0.target.transition_to(
        chat_state="Ask them to provide their credit score, annual income, and the desired loan amount",
        condition="The customer specified the type of loan",
    )

    # Use a tool to check basic credit eligibility
    t2 = await t1.target.transition_to(tool_state=check_eligibility)

    # Handle the path for initial credit ineligibility
    t3_credit_ineligible = await t2.target.transition_to(
        chat_state="Inform them that they are not qualified for the loan and ask them if they are interested in other types of loans",
        condition="The customer is not eligible for the loan",
    )
    await t3_credit_ineligible.target.transition_to(state=p.END_JOURNEY)

    # Else continue this path: request and process documents
    t3_request_docs = await t2.target.transition_to(
        chat_state="Inform them that they meet the initial criteria and ask them to provide their tax returns and recent pay stubs",
        condition="The customer is eligible for the loan",
    )

    # Process the documents using a tool
    t4_process_docs = await t3_request_docs.target.transition_to(tool_state=process_documents)

    # Handle the path for document ineligibility
    t5_docs_ineligible = await t4_process_docs.target.transition_to(
        chat_state="Ask them to use our Online Portal to submit their documents, or contact a Loan Specialist at our Customer Care Phone Number for assistance",
        condition="The documents are either invalid, missing or not uploaded correctly",
    )
    await t5_docs_ineligible.target.transition_to(state=p.END_JOURNEY)

    # Else continue this path: success and hand-off to human
    t5_final_eligible = await t4_process_docs.target.transition_to(
        chat_state="Inform them that their application has been approved and a Loan Specialist will review their information and contact them shortly",
        condition="Documents are successfully uploaded",
    )

    # End the journey
    await t5_final_eligible.target.transition_to(state=p.END_JOURNEY)

    # Create additional guidelines for the journey
    await journey.create_guideline(
        condition="The customer asks about the types of loans we offer.",
        action="Call the get_loan_types tool and provide the list of loan types we offer.",
        tools=[get_loan_types]
    )

    return journey


async def main() -> None:
    """
    The main function to initialize and configure the Parlant agent.
    """
    async with p.Server(session_store="local") as server:
        agent = await server.create_agent(
            name="Financial Services Agent",
            description="A compliance-driven agent that helps customers with loan approval.",
        )

        # Add foundational components
        await add_domain_glossary(agent)
        await agent.create_canned_response(
            template="Hello! My name is {{generative.agent_name}}. I am here to assist you with the loan approval process."
        )

        loan_approval_journey = await create_loan_journey(agent)

        # Implement guidelines for behavioral control
        await agent.create_guideline(
            condition="The customer asks about current loan interest rates.",
            action="Call the get_current_rates tool and provide the current rates for the customer's zip code.",
            tools=[get_current_rates],
        )

        await agent.create_guideline(
            condition="The customer asks for legal or financial advice",
            action="State that you cannot provide financial or legal advice and recommend a licensed professional.",
        )

        await agent.create_guideline(
            condition="The customer asks about something that has nothing to do with financial services.",
            action="Kindly tell them you cannot assist with off-topic inquiries - do not engage with their request.",
        )

        await agent.create_guideline(
            condition="The customer asks for contact information for human support.",
            action="Provide the Customer Care Phone Number and tell them a Loan Specialist can assist them.",
        )


if __name__ == "__main__":
    asyncio.run(main())