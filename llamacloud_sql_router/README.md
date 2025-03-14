# Combining RAG and Text-to-SQL in a Single Query Interface

In this project, we use:
- OpenAI GPT 3.5 Turbo model as the LLM
- streamlit to build a UI
- llama_index for orchestration

A demo is shown below: \
[Video demo](https://github.com/Umamahesh-J/ai-engineering-hub/blob/RAG_and_Text-to-SQL/llamacloud_sql_router/demo.mkv)

## Installation and setup
In Linux, include the following statements in .bashrc file: 

To setup OpenAI: \
`export OPENAI_API_KEY = <YOUR_OPENAI_API_KEY>`

To setup ARIZE_PHOENIX: \
`export ARIZE_PHOENIX_API_KEY = <ARIZE_PHOENIX_API_KEY>`

To setup LLAMA_CLOUD: \
`export LLAMA_CLOUD_API_KEY = <YOUR_LLAMA_CLOUD_API_KEY>`

## Install Dependencies:

`pip install -U llama-index-callbacks-arize-phoenix` \
`pip install -q arize-phoenix` \
`pip install --upgrade llama-index` \
`pip install llama-index-utils-workflow` \
`pip install streamlit `

## Run the app:

Run the app by running the following command:

`streamlit run llamacloud_sql_router.py`




