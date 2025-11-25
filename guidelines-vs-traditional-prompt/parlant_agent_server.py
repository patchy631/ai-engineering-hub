import asyncio
import os
import parlant.sdk as p
from dotenv import load_dotenv

load_dotenv()

# Life Insurance Agent - Parlant's structured approach vs traditional prompts

@p.tool
async def get_policy_types(context: p.ToolContext) -> p.ToolResult:
    """Retrieves comprehensive information about available life insurance policy types.
    
    This tool provides detailed descriptions of different life insurance policies,
    including their key features, benefits, drawbacks, and ideal use cases.
    Use this tool when customers ask about policy types, want to understand
    their options, or need guidance on which type might suit their needs.
    """
    return p.ToolResult(data={
        "all_policy_types": {
            "Term Life": "Coverage for specific period (10-30 years), affordable, no cash value",
            "Whole Life": "Lifetime coverage, builds cash value, higher premiums",
            "Universal Life": "Flexible premiums and death benefit, cash value with interest", 
            "Variable Life": "Investment component, cash value in market sub-accounts",
        },
        "explanation": "There are 4 main types of life insurance policies. Each serves different needs and financial goals. It's important to understand all options before making a decision."
    })


@p.tool
async def calculate_coverage_recommendation(
    context: p.ToolContext,
    annual_income: float,
    num_dependents: int,
    existing_coverage: float = 0.0,
) -> p.ToolResult:
    """Calculates personalized life insurance coverage recommendation.
    
    This tool analyzes the customer's financial situation and family structure
    to provide a tailored coverage recommendation. It considers income replacement
    needs, dependent support, and existing coverage to determine optimal coverage amount.
    
    Args:
        annual_income: Customer's annual income in dollars
        num_dependents: Number of dependents (spouse, children, etc.)
        existing_coverage: Current life insurance coverage amount (optional)
    """
    base_coverage = annual_income * 10
    dependent_coverage = num_dependents * 100000
    recommended = base_coverage + dependent_coverage - existing_coverage
    
    return p.ToolResult(data={
        "recommended_coverage": max(250000, recommended),
        "explanation": f"Based on {num_dependents} dependents and ${annual_income:,.0f} annual income",
    })


@p.tool
async def check_health_impact(context: p.ToolContext, condition: str, controlled: bool = True) -> p.ToolResult:
    """Analyzes how specific health conditions affect life insurance rates and underwriting.
    
    This tool provides detailed information about how various health conditions
    impact life insurance premiums, underwriting requirements, and approval chances.
    It helps customers understand what to expect during the application process.
    
    Args:
        condition: The specific health condition to analyze
        controlled: Whether the condition is well-managed/controlled (default: True)
    """
    conditions_impact = {
        "diabetes": "Controlled diabetes may qualify for standard rates. Uncontrolled may result in higher premiums.",
        "high blood pressure": "Controlled blood pressure typically qualifies for standard rates.",
        "heart disease": "Stable condition with good management may be approved with higher premiums.",
        "cancer": "Typically need 5-10 years cancer-free, varies by type and stage.",
        "obesity": "High BMI may increase rates or require additional underwriting.",
        "asthma": "Well-controlled asthma usually has minimal impact on rates.",
        "depression": "Controlled depression/anxiety typically approved at standard rates.",
        "sleep apnea": "Treated sleep apnea usually has minimal impact.",
    }
    
    impact = conditions_impact.get(condition.lower(), "Evaluated during underwriting; case-by-case.")
    
    return p.ToolResult(data={
        "condition": condition,
        "impact": impact,
        "controlled": controlled,
        "needs_underwriting": True,
    })


@p.tool
async def get_premium_factors(context: p.ToolContext) -> p.ToolResult:
    """Returns factors that affect life insurance premium pricing."""
    return p.ToolResult(data={
        "age": "Younger applicants get lower rates",
        "health": "Better health = lower premiums (medical exam required)",
        "smoking": "Tobacco use increases premiums 2-3x",
        "occupation": "High-risk jobs increase rates",
        "hobbies": "Dangerous activities increase rates",
        "coverage_amount": "Higher death benefit = higher premium",
        "term_length": "Longer terms cost more per month but better value",
        "family_history": "Genetic conditions may affect rates",
    })


@p.tool
async def explain_policy_riders(context: p.ToolContext, rider_name: str = None) -> p.ToolResult:
    """Explains available policy riders and add-ons."""
    riders = {
        "accidental death": "Extra payout if death is from accident",
        "waiver of premium": "Waives premiums if you become disabled",
        "accelerated death benefit": "Access death benefit if terminally ill",
        "long-term care": "Covers nursing home or in-home care costs",
        "child term": "Covers children until adulthood",
        "guaranteed insurability": "Buy more coverage later without medical exam",
    }
    return p.ToolResult(data={rider_name: riders.get(rider_name.lower(), "Rider not found")} if rider_name else riders)


@p.tool
async def get_application_steps(context: p.ToolContext) -> p.ToolResult:
    """Provides the step-by-step application process."""
    return p.ToolResult(data={
        "steps": [
            "Complete application form",
            "Schedule and complete medical exam",
            "Underwriting review (2-6 weeks)",
            "Receive offer with rating",
            "Accept offer and make first premium payment",
            "Policy issued and coverage begins",
        ],
        "typical_timeline": "4-8 weeks from application to approval",
    })


@p.tool
async def get_agent_contact(context: p.ToolContext) -> p.ToolResult:
    """Provides comprehensive contact information for licensed insurance agents.
    
    This tool connects customers with qualified human agents who can provide
    personalized advice, handle complex cases, and assist with policy applications.
    Use this tool when customers need human support or specialized guidance.
    """
    return p.ToolResult(data={
        "phone": "1-800-LIFE-INS (1-800-543-3467)",
        "email": "agents@lifeinsurance.com",
        "hours": "Monday-Friday 8am-8pm EST, Saturday 9am-5pm EST",
        "website": "www.example-lifeinsurance.com",
    })


async def main() -> None:
    """Initialize the Parlant life insurance agent with tools and guidelines."""
    async with p.Server(session_store="local") as server:
        agent = await server.create_agent(
            name="Life Insurance Advisor",
            description="You are a helpful life insurance advisor who provides detailed, thorough answers to customer questions.",
        )

        # Set up greeting and guidelines
        await agent.create_canned_response(
            template="Hello! I'm your Life Insurance Advisor. How can I assist you today?"
        )
        await agent.create_guideline(
            condition="The customer wants to replace, switch, or cancel their existing life insurance policy to get a different type of policy.",
            action="CRITICAL: Warn them DO NOT cancel their current policy until the new one is approved and active. Explain the risks and use get_agent_contact tool to provide agent contact information.",
            tools=[get_agent_contact],
        )

        await agent.create_guideline(
            condition="The customer asks about types of life insurance, policy options, or what kinds of policies are available (but NOT about replacing existing policies).",
            action="Use get_policy_types tool to retrieve policy information, then explain ALL policy types clearly with key features, benefits, and who each type is best suited for. Make sure to cover all available options.",
            tools=[get_policy_types],
        )

        await agent.create_guideline(
            condition="The customer asks about coverage amount, how much life insurance they need, or what coverage amount is recommended (and provides their age, income, and family situation).",
            action="Use calculate_coverage_recommendation tool with their income and number of dependents. Explain the calculation and provide the specific recommendation.",
            tools=[calculate_coverage_recommendation],
        )

        await agent.create_guideline(
            condition="The customer asks about premium factors, what affects life insurance rates, or what determines pricing.",
            action="Use get_premium_factors tool to retrieve factor information, then explain each factor clearly with specific examples of how they impact premium costs.",
            tools=[get_premium_factors],
        )

        await agent.create_guideline(
            condition="The customer mentions any health condition, medical issue, or asks about how a specific health condition affects life insurance.",
            action="Use check_health_impact tool with the specific condition mentioned. Explain how this condition typically affects life insurance rates and underwriting.",
            tools=[check_health_impact],
        )

        await agent.create_guideline(
            condition="The customer asks about policy riders, add-ons, or additional coverage options.",
            action="Use explain_policy_riders tool to retrieve rider information, then explain each available rider with its benefits, costs, and who should consider it.",
            tools=[explain_policy_riders],
        )

        await agent.create_guideline(
            condition="The customer asks about the application process, how to apply, or what steps are involved in getting life insurance.",
            action="Use get_application_steps tool to retrieve the process information, then walk them through each step clearly with timelines and what to expect at each stage.",
            tools=[get_application_steps],
        )

        await agent.create_guideline(
            condition="The customer asks for legal advice, financial advice, tax advice, or investment advice.",
            action="Clearly state that you cannot provide legal, financial, tax, or investment advice. Recommend they consult with a licensed attorney, financial advisor, or tax professional for such matters.",
        )

        await agent.create_guideline(
            condition="The customer asks about topics unrelated to life insurance (auto insurance, health insurance, home insurance, etc.) or mentions multiple types of insurance.",
            action="Explain that you specialize only in life insurance. For other insurance types, use get_agent_contact tool to provide agent contact information.",
            tools=[get_agent_contact],
        )

        await agent.create_guideline(
            condition="The customer is confused about conflicting advice from different sources regarding which type of life insurance to choose.",
            action="Use get_policy_types tool to provide objective information about ALL policy types. Explain each type clearly and explain that different types serve different needs. Make sure to cover all available options to help them understand the full range of choices.",
            tools=[get_policy_types],
        )

        # Save agent ID for demo client
        os.makedirs("parlant-data", exist_ok=True)
        with open(os.path.join("parlant-data", "agent_id.txt"), "w", encoding="utf-8") as f:
            f.write(getattr(agent, "id", ""))


if __name__ == "__main__":
    asyncio.run(main())
