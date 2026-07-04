# Train YOLO26 Object Detection Model on a Custom Dataset

This project demonstrates how to fine-tune a **YOLO26m** checkpoint on a custom object detection dataset using Ultralytics, download datasets directly from Roboflow Universe, and track experiments with Comet ML. The full workflow — from pre-trained inference to validation and test-set visualization — is covered in a single Jupyter notebook.

---

## Setup and installations

**Get API Keys**:

- [Roboflow](https://roboflow.com/) — needed to download the dataset. Store it as `ROBOFLOW_API_KEY` in a `.env` file.
- [Comet ML](https://www.comet.com/) — needed for experiment tracking. Store it as `api_key` in a `.comet.config` file.

Refer to `.env.example` and `.comet.config.example` files for the structure of the files.

**Install Dependencies**:

Ensure you have Python 3.12 or later installed.

```bash
uv sync
```

Select the above python virtual environment as kernel in the notebook.

**Run the notebook**:

Open and run `train_yolo26_object_detection.ipynb` end-to-end. The notebook covers:

1. Pre-trained YOLO26 inference on a sample image
2. Dataset download from Roboflow Universe (boxing-punch detection)
3. Fine-tuning YOLO26 with Comet ML logging
4. Validation on the best checkpoint
5. Inference and annotated prediction on the test set

---

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
