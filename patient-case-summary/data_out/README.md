# Output Data Directory

This directory stores intermediate and final outputs from the patient case summary workflow.

## Contents

When the workflow runs, it creates the following files:

- `workflow_output/patient_info.json`: Extracted patient information
- `workflow_output/condition_bundles.json`: Conditions mapped to encounters and medications
- `workflow_output/guideline_recommendations.jsonl`: Guideline recommendations for each condition

These files are cached to improve performance on subsequent runs with the same patient data. 