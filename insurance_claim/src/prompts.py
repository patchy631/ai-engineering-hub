GENERATE_POLICY_QUERIES_PROMPT = """\
You are an assistant tasked with determining what insurance policy sections to consult for a given auto claim.

**Instructions:**
1. Review the claim data, including the type of loss (rear-end collision), estimated repair cost, and policy number.
2. Identify what aspects of the policy we need:
   - Collision coverage conditions
   - Deductible application
   - Any special endorsements related to rear-end collisions or no-fault scenarios
3. Produce 3-5 queries that can be used against a vector index of insurance policies to find relevant clauses.

Claim Data:
{claim_info}

Return a JSON object matching the PolicyQueries schema.
"""

POLICY_RECOMMENDATION_PROMPT = """\
Given the retrieved policy sections for this claim, determine:
- If the collision is covered
- The applicable deductible
- Recommended settlement amount (e.g., cost minus deductible)
- Which policy section applies

Claim Info:
{claim_info}

Policy Text:
{policy_text}

Return a JSON object matching PolicyRecommendation schema.
"""