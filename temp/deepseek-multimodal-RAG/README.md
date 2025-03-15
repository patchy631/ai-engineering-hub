# MultiModal RAG with DeepSeek-Janus-Pro

This project implements a MultiModal RAG with DeepSeek's latest model Janus-Pro.

We use the following tools
- DeepSeek-Janus-Pro as the multi-modal LLM
- ColPali as the vision encoder
- Qdrant as the vector database
- Streamlit as the web interface

## Demo

A demo of the project is available below:

![demo](./video-demo.mp4)

---
## Setup and installations

**Setup Janus**:
```
git clone https://github.com/deepseek-ai/Janus.git
pip install -e ./Janus
```

**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install streamlit fastembed flash-attn transformers
   ```

---

## Run the project

Finally, run the project by running the following command:

```bash
streamlit run app.py
```


---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
