from opik.evaluation.metrics import GEval


def evaluate_code(generated_code: str, reference_code: str = None):
    """
    Evaluate generated Python code using Comet Opik's GEval metrics.

    1. Code Correctness - Assesses functional correctness, edge case handling,
       and completeness of implementation
    2. Code Readability - Evaluates naming conventions, formatting, documentation,
       and overall code structure
    3. Code Best Practices - Checks error handling, security practices, efficiency,
       and modularity

    Args:
        generated_code (str): The Python code to evaluate
        reference_code (str, optional): Reference code for comparison. If provided,
            the correctness evaluation will compare against this reference.

    Returns:
        dict: A dictionary containing evaluation results with the following structure:
            {
                "overall_score": float,  # Average score across all metrics (0-10 scale)
                "detailed_metrics": {
                    "correctness": {"score": float, "reason": str},
                    "readability": {"score": float, "reason": str},
                    "best_practices": {"score": float, "reason": str}
                },
                "passed": bool,  # Whether overall_score >= 7.0 (70% threshold)
                "error": str, optional  # Error message if evaluation fails
            }
    """
    try:
        # Validate input
        if not generated_code or not generated_code.strip():
            raise ValueError("Generated code cannot be empty")
     
        # Build the context string that includes both actual and expected code
        context = f"ACTUAL_CODE:\n```\n{generated_code}\n```"
        if reference_code:
            context += f"\nEXPECTED_CODE:\n```\n{reference_code}\n```"

        # Define rubric scoring criteria
        correctness_rubric_text = (
            "Score 0-2: Code is non-functional or has critical errors\n"
            "Score 3-5: Code works but misses key functionality\n"
            "Score 6-8: Code is mostly correct with minor issues\n"
            "Score 9-10: Code is completely correct"
        )

        readability_rubric_text = (
            "Score 0-2: Code is poorly formatted and hard to read\n"
            "Score 3-5: Code has basic formatting but lacks clarity\n"
            "Score 6-8: Code is well formatted with minor issues\n"
            "Score 9-10: Code is exceptionally readable and well documented"
        )

        best_practices_rubric_text = (
            "Score 0-2: Code ignores best practices\n"
            "Score 3-5: Code follows basic practices with gaps\n"
            "Score 6-8: Code mostly follows best practices\n"
            "Score 9-10: Code perfectly follows all best practices"
        )

        # 1. Code Correctness Metric
        correctness_metric = GEval(
            task_introduction=(
                "You are an expert judge evaluating Python code correctness. "
                "The expected implementation is under EXPECTED_CODE and the submitted code is under ACTUAL_CODE. "
                "Assess if the code is functionally correct, handles edge cases, and fully implements the required functionality. "
                "Use the following rubric to assign scores:"
            ),
            evaluation_criteria=(
                "EVALUATION STEPS:\n"
                "1. Check if all required functionality is implemented.\n"
                "2. Verify proper handling of edge cases.\n"
                "3. Identify potential runtime errors.\n"
                "4. Confirm the code produces the expected outputs.\n\n"
                "SCORING RUBRIC:\n"
                f"{correctness_rubric_text}\n\n"
                "Return only a score between 0 and 10, and a concise reason that references the rubric."
            ),
            name="Code Correctness",
        )

        # 2. Code Readability Metric
        readability_metric = GEval(
            task_introduction=(
                "You are an expert judge evaluating Python code readability. "
                "The code to review is under ACTUAL_CODE. Focus on naming, formatting, and documentation. "
                "Use the following rubric to assign scores:"
            ),
            evaluation_criteria=(
                "EVALUATION STEPS:\n"
                "1. Are naming conventions clear and consistent?\n"
                "2. Is formatting and indentation correct?\n"
                "3. Are comments and docstrings complete and helpful?\n"
                "4. Is the code organized logically?\n\n"
                "SCORING RUBRIC:\n"
                f"{readability_rubric_text}\n\n"
                "Return only a score between 0 and 10, and a concise reason that references the rubric."
            ),
            name="Code Readability",
        )

        # 3. Code Best Practices Metric
        best_practices_metric = GEval(
            task_introduction=(
                "You are an expert judge evaluating adherence to Python best practices. "
                "The code to review is under ACTUAL_CODE. Focus on error handling, security, efficiency, and modularity. "
                "Use the following rubric to assign scores:"
            ),
            evaluation_criteria=(
                "EVALUATION STEPS:\n"
                "1. Does it handle exceptions and errors properly?\n"
                "2. Are security best practices followed?\n"
                "3. Is the code efficient in performance?\n"
                "4. Is functionality split into reusable, modular components?\n\n"
                "SCORING RUBRIC:\n"
                f"{best_practices_rubric_text}\n\n"
                "Return only a score between 0 and 10, and a concise reason that references the rubric."
            ),
            name="Code Best Practices",
        )

        # Run evaluation for each metric using Opik's GEval
        correctness_result = correctness_metric.score(output=context)
        readability_result = readability_metric.score(output=context)
        best_practices_result = best_practices_metric.score(output=context)

        # Convert scores from Opik's 0-1 scale to 0-10 scale
        # Opik returns scores as 0-1, we multiply by 10 for consistency
        correctness_score = correctness_result.value * 10
        readability_score = readability_result.value * 10
        best_practices_score = best_practices_result.value * 10

        # Calculate overall score as average of all three metrics
        overall_score = (
            correctness_score + readability_score + best_practices_score
        ) / 3

        # Prepare detailed metrics structure
        detailed_metrics = {
            "correctness": {
                "score": correctness_score,
                "reason": correctness_result.reason,
            },
            "readability": {
                "score": readability_score,
                "reason": readability_result.reason,
            },
            "best_practices": {
                "score": best_practices_score,
                "reason": best_practices_result.reason,
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
            "error": f"Error evaluating code: {str(e)}",
            "overall_score": 0.0,
            "detailed_metrics": {},
            "passed": False,
        }
