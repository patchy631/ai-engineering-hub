# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "huggingface-hub>=1.1.4",
#     "python-dotenv>=1.2.1",
#     "pyyaml>=6.0.3",
#     "requests>=2.32.5",
# ]
# ///

"""
Add Artificial Analysis evaluations to a Hugging Face model card.

NOTE: This is a standalone reference script. For integrated functionality
with additional features (README extraction, validation, etc.), use:
    ../scripts/evaluation_manager.py import-aa [options]

STANDALONE USAGE:
AA_API_KEY="<your-api-key>" HF_TOKEN="<your-huggingface-token>" \
python artificial_analysis_to_hub.py \
--creator-slug <artificial-analysis-creator-slug> \
--model-name <artificial-analysis-model-name> \
--repo-id <huggingface-repo-id>

INTEGRATED USAGE (Recommended):
python ../scripts/evaluation_manager.py import-aa \
--creator-slug <creator-slug> \
--model-name <model-name> \
--repo-id <repo-id> \
[--create-pr]
"""

import argparse
import os

import requests
import dotenv
from huggingface_hub import ModelCard

dotenv.load_dotenv()

API_KEY = os.getenv("AA_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
URL = "https://artificialanalysis.ai/api/v2/data/llms/models"
HEADERS = {"x-api-key": API_KEY}

if not API_KEY:
    raise ValueError("AA_API_KEY is not set")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN is not set")


def get_model_evaluations_data(creator_slug, model_name):
    response = requests.get(URL, headers=HEADERS)
    response_data = response.json()["data"]
    for model in response_data:
        if (
            model["model_creator"]["slug"] == creator_slug
            and model["slug"] == model_name
        ):
            return model
    raise ValueError(f"Model {model_name} not found")


def aa_evaluations_to_model_index(
    model,
    dataset_name="Artificial Analysis Benchmarks",
    dataset_type="artificial_analysis",
    task_type="evaluation",
):
    if not model:
        raise ValueError("Model data is required")

    model_name = model.get("name", model.get("slug", "unknown-model"))
    evaluations = model.get("evaluations", {})

    metrics = []
    for key, value in evaluations.items():
        metrics.append(
            {
                "name": key.replace("_", " ").title(),
                "type": key,
                "value": value,
            }
        )

    model_index = [
        {
            "name": model_name,
            "results": [
                {
                    "task": {"type": task_type},
                    "dataset": {"name": dataset_name, "type": dataset_type},
                    "metrics": metrics,
                    "source": {
                        "name": "Artificial Analysis API",
                        "url": "https://artificialanalysis.ai",
                    },
                }
            ],
        }
    ]

    return model_index


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--creator-slug", type=str, required=True)
    parser.add_argument("--model-name", type=str, required=True)
    parser.add_argument("--repo-id", type=str, required=True)
    args = parser.parse_args()

    aa_evaluations_data = get_model_evaluations_data(
        creator_slug=args.creator_slug, model_name=args.model_name
    )

    model_index = aa_evaluations_to_model_index(model=aa_evaluations_data)

    card = ModelCard.load(args.repo_id)
    card.data["model-index"] = model_index

    commit_message = (
        f"Add Artificial Analysis evaluations for {args.model_name}"
    )
    commit_description = (
        f"This commit adds the Artificial Analysis evaluations for the {args.model_name} model to this repository. "
        "To see the scores, visit the [Artificial Analysis](https://artificialanalysis.ai) website."
    )

    card.push_to_hub(
        args.repo_id,
        token=HF_TOKEN,
        commit_message=commit_message,
        commit_description=commit_description,
        create_pr=True,
    )


if __name__ == "__main__":
    main()
