from opik.evaluation.metrics import GEval


def evaluate_reasoning(generated_response: str, reference_answer: str = None):
    """
    Evaluate reasoning capabilities of generated responses using Comet Opik's GEval metrics.

    This function evaluates responses across four key reasoning dimensions:
    1. Logical Reasoning - Assesses the coherence and validity of logical steps and conclusions
    2. Factual Accuracy - Evaluates the correctness of factual claims and information
    3. Coherence - Measures how well-structured and clear the response is
    4. Depth of Analysis - Assesses the thoroughness and insight of the reasoning

    Args:
        generated_response (str): The response to evaluate
        reference_answer (str, optional): Reference answer for comparison. If provided,
            the evaluation will compare against this reference.

    Returns:
        dict: A dictionary containing evaluation results with the following structure:
            {
                "overall_score": float,  # Average score across all metrics (0-10 scale)
                "detailed_metrics": {
                    "logical_reasoning": {"score": float, "reason": str},
                    "factual_accuracy": {"score": float, "reason": str},
                    "coherence": {"score": float, "reason": str},
                    "depth_of_analysis": {"score": float, "reason": str}
                },
                "passed": bool,  # Whether overall_score >= 7.0 (70% threshold)
                "error": str, optional  # Error message if evaluation fails
            }
    """
    try:
        # Validate input
        if not generated_response or not generated_response.strip():
            raise ValueError("Generated response cannot be empty")
     
        # Build the context string that includes both actual and expected responses
        context = f"ACTUAL_RESPONSE:\n```\n{generated_response}\n```"
        if reference_answer:
            context += f"\nEXPECTED_RESPONSE:\n```\n{reference_answer}\n```"

        # Define rubric scoring criteria for reasoning evaluation
        logical_reasoning_rubric = (
            "Score 0-2: Response contains major logical fallacies or contradictions\n"
            "Score 3-5: Response has basic logical structure but with some flaws\n"
            "Score 6-8: Response demonstrates sound logical reasoning with minor gaps\n"
            "Score 9-10: Response shows exceptional logical consistency and validity"
        )

        factual_accuracy_rubric = (
            "Score 0-2: Response contains significant factual errors or unsupported claims\n"
            "Score 3-5: Response has mostly accurate information with some questionable claims\n"
            "Score 6-8: Response is largely accurate with minor factual issues\n"
            "Score 9-10: Response is completely accurate and well-supported with facts"
        )

        coherence_rubric = (
            "Score 0-2: Response is poorly structured and difficult to follow\n"
            "Score 3-5: Response has basic organization but lacks clear flow\n"
            "Score 6-8: Response is well-organized with good structure and clarity\n"
            "Score 9-10: Response is exceptionally clear, well-structured, and easy to follow"
        )

        depth_of_analysis_rubric = (
            "Score 0-2: Response provides superficial analysis with little insight\n"
            "Score 3-5: Response shows basic analysis but lacks depth or nuance\n"
            "Score 6-8: Response demonstrates thorough analysis with good insights\n"
            "Score 9-10: Response shows exceptional depth, nuance, and profound insights"
        )

        # 1. Logical Reasoning Metric
        logical_reasoning_metric = GEval(
            task_introduction=(
                "You are an expert judge evaluating the logical reasoning quality of a response. "
                "The response to evaluate is under ACTUAL_RESPONSE. "
                f"{'The expected response is under EXPECTED_RESPONSE for comparison. ' if reference_answer else ''}"
                "Assess the logical consistency, validity of arguments, and reasoning flow. "
                "Use the following rubric to assign scores:"
            ),
            evaluation_criteria=(
                "EVALUATION STEPS:\n"
                "1. Check for logical consistency throughout the response.\n"
                "2. Identify any logical fallacies or contradictions.\n"
                "3. Evaluate the validity of conclusions drawn from premises.\n"
                "4. Assess the overall reasoning structure and flow.\n\n"
                "SCORING RUBRIC:\n"
                f"{logical_reasoning_rubric}\n\n"
                "Return only a score between 0 and 10, and a concise reason that references the rubric."
            ),
            name="Logical Reasoning",
        )

        # 2. Factual Accuracy Metric
        factual_accuracy_metric = GEval(
            task_introduction=(
                "You are an expert judge evaluating the factual accuracy of a response. "
                "The response to evaluate is under ACTUAL_RESPONSE. "
                f"{'The expected response is under EXPECTED_RESPONSE for comparison. ' if reference_answer else ''}"
                "Assess the correctness of factual claims and information provided. "
                "Use the following rubric to assign scores:"
            ),
            evaluation_criteria=(
                "EVALUATION STEPS:\n"
                "1. Verify the accuracy of factual claims made in the response.\n"
                "2. Check for any misleading or incorrect information.\n"
                "3. Assess whether claims are properly supported or justified.\n"
                "4. Evaluate the reliability of information sources if mentioned.\n\n"
                "SCORING RUBRIC:\n"
                f"{factual_accuracy_rubric}\n\n"
                "Return only a score between 0 and 10, and a concise reason that references the rubric."
            ),
            name="Factual Accuracy",
        )

        # 3. Coherence Metric
        coherence_metric = GEval(
            task_introduction=(
                "You are an expert judge evaluating the coherence and clarity of a response. "
                "The response to evaluate is under ACTUAL_RESPONSE. "
                "Focus on organization, structure, and overall readability. "
                "Use the following rubric to assign scores:"
            ),
            evaluation_criteria=(
                "EVALUATION STEPS:\n"
                "1. Assess the overall organization and structure of the response.\n"
                "2. Check for clear transitions between ideas and concepts.\n"
                "3. Evaluate the clarity and readability of the writing.\n"
                "4. Determine if the response follows a logical sequence.\n\n"
                "SCORING RUBRIC:\n"
                f"{coherence_rubric}\n\n"
                "Return only a score between 0 and 10, and a concise reason that references the rubric."
            ),
            name="Coherence",
        )

        # 4. Depth of Analysis Metric
        depth_of_analysis_metric = GEval(
            task_introduction=(
                "You are an expert judge evaluating the depth and quality of analysis in a response. "
                "The response to evaluate is under ACTUAL_RESPONSE. "
                f"{'The expected response is under EXPECTED_RESPONSE for comparison. ' if reference_answer else ''}"
                "Assess the thoroughness, insight, and analytical depth. "
                "Use the following rubric to assign scores:"
            ),
            evaluation_criteria=(
                "EVALUATION STEPS:\n"
                "1. Evaluate the depth and thoroughness of the analysis provided.\n"
                "2. Check for evidence of critical thinking and insight.\n"
                "3. Assess whether multiple perspectives are considered where appropriate.\n"
                "4. Determine if the response goes beyond surface-level observations.\n\n"
                "SCORING RUBRIC:\n"
                f"{depth_of_analysis_rubric}\n\n"
                "Return only a score between 0 and 10, and a concise reason that references the rubric."
            ),
            name="Depth of Analysis",
        )

        # Run evaluation for each metric using Opik's GEval
        logical_reasoning_result = logical_reasoning_metric.score(output=context)
        factual_accuracy_result = factual_accuracy_metric.score(output=context)
        coherence_result = coherence_metric.score(output=context)
        depth_of_analysis_result = depth_of_analysis_metric.score(output=context)

        # Convert scores from Opik's 0-1 scale to 0-10 scale
        # Opik returns scores as 0-1, we multiply by 10 for consistency
        logical_reasoning_score = logical_reasoning_result.value * 10
        factual_accuracy_score = factual_accuracy_result.value * 10
        coherence_score = coherence_result.value * 10
        depth_of_analysis_score = depth_of_analysis_result.value * 10

        # Calculate overall score as average of all four metrics
        overall_score = (
            logical_reasoning_score + factual_accuracy_score + 
            coherence_score + depth_of_analysis_score
        ) / 4

        # Prepare detailed metrics structure
        detailed_metrics = {
            "logical_reasoning": {
                "score": logical_reasoning_score,
                "reason": logical_reasoning_result.reason,
            },
            "factual_accuracy": {
                "score": factual_accuracy_score,
                "reason": factual_accuracy_result.reason,
            },
            "coherence": {
                "score": coherence_score,
                "reason": coherence_result.reason,
            },
            "depth_of_analysis": {
                "score": depth_of_analysis_score,
                "reason": depth_of_analysis_result.reason,
            },
        }

        # Return results
        return {
            "overall_score": overall_score,
            "detailed_metrics": detailed_metrics,
            "passed": overall_score >= 7.0,  # 70% threshold
        }

    except Exception as e:
        # Error handling
        return {
            "error": f"Error evaluating reasoning: {str(e)}",
            "overall_score": 0.0,
            "detailed_metrics": {},
            "passed": False,
        }


# Keep backward compatibility with the old function name
def evaluate_code(generated_response: str, reference_answer: str = None):
    """
    Backward compatibility wrapper for evaluate_reasoning.
    This allows the existing app code to work without modifications.
    """
    return evaluate_reasoning(generated_response, reference_answer)