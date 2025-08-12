from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics.g_eval import Rubric
from typing import Dict, Any

def evaluate_code(generated_code: str, reference_code: str = None):
    try:
        # Initialize test case
        test_case = LLMTestCase(
            input="Code Generation Task",
            actual_output=generated_code,
            expected_output=reference_code if reference_code else ""
        )

        # Code Correctness Metric
        correctness_metric = GEval(
            name="Code Correctness",
            criteria="Evaluate if the code is functionally correct, properly handles edge cases, and implements the required functionality completely.",
            evaluation_steps=[
                "Check if the code implements all required functionality",
                "Verify proper handling of edge cases",
                "Check for potential runtime errors",
                "Assess if the code produces expected outputs"
            ],
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.EXPECTED_OUTPUT],
            rubric=[
                Rubric(score_range=(0,2), expected_outcome="Code is non-functional or has critical errors"),
                Rubric(score_range=(3,5), expected_outcome="Code works but misses key functionality"),
                Rubric(score_range=(6,8), expected_outcome="Code is mostly correct with minor issues"),
                Rubric(score_range=(9,10), expected_outcome="Code is completely correct")
            ],
            threshold=0.7
        )

        # Code Readability Metric
        readability_metric = GEval(
            name="Code Readability",
            criteria="Evaluate code readability including proper naming, formatting, and documentation.",
            evaluation_steps=[
                "Check for clear and consistent naming conventions",
                "Verify proper code formatting and indentation",
                "Assess quality and completeness of comments and docstrings",
                "Check for code organization and logical structure"
            ],
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
            rubric=[
                Rubric(score_range=(0,2), expected_outcome="Code is poorly formatted and hard to read"),
                Rubric(score_range=(3,5), expected_outcome="Code has basic formatting but lacks clarity"),
                Rubric(score_range=(6,8), expected_outcome="Code is well formatted with minor issues"),
                Rubric(score_range=(9,10), expected_outcome="Code is exceptionally readable and well documented")
            ],
            threshold=0.7
        )

        # Code Best Practices Metric
        best_practices_metric = GEval(
            name="Code Best Practices",
            criteria="Evaluate adherence to coding best practices, including error handling, security, and efficiency.",
            evaluation_steps=[
                "Check for proper error handling and exceptions",
                "Verify security best practices",
                "Assess code efficiency and performance considerations",
                "Check for code reusability and modularity"
            ],
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
            rubric=[
                Rubric(score_range=(0,2), expected_outcome="Code ignores best practices"),
                Rubric(score_range=(3,5), expected_outcome="Code follows basic practices with gaps"),
                Rubric(score_range=(6,8), expected_outcome="Code mostly follows best practices"),
                Rubric(score_range=(9,10), expected_outcome="Code perfectly follows all best practices")
            ],
            threshold=0.7
        )

        # Run evaluation
        metrics = [correctness_metric, readability_metric, best_practices_metric]
        for metric in metrics:
            metric.measure(test_case)

        # Calculate overall score
        overall_score = (correctness_metric.score + readability_metric.score + best_practices_metric.score) / 3

        # Prepare detailed metrics
        detailed_metrics = {
            "correctness": {
                "score": correctness_metric.score,
                "reason": correctness_metric.reason
            },
            "readability": {
                "score": readability_metric.score,
                "reason": readability_metric.reason
            },
            "best_practices": {
                "score": best_practices_metric.score,
                "reason": best_practices_metric.reason
            }
        }

        return {
            "overall_score": overall_score,
            "detailed_metrics": detailed_metrics,
            "passed": overall_score >= 0.7 
        }

    except Exception as e:
        return {
            "error": f"Error evaluating code: {str(e)}",
            "overall_score": 0.0,
            "detailed_metrics": {},
            "passed": False
        } 