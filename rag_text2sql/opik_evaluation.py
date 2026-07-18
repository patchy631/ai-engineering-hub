import asyncio
# import nest_asyncio
# nest_asyncio.apply()
import opik
from opik import track
#opik.configure(use_local=False)

from dotenv import load_dotenv

load_dotenv()

from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from opik.integrations.llama_index import LlamaIndexCallbackHandler

from app import RouterOutputAgentWorkflow
from db_init import create_sql_tool, create_llama_cloud_tool

MODEL = "gpt-4o-mini"
sql_tool = create_sql_tool()
llama_cloud_tool = create_llama_cloud_tool()

opik_callback_handler = LlamaIndexCallbackHandler()
Settings.callback_manager = CallbackManager([opik_callback_handler])

from opik import Opik
import pandas as pd

df = pd.read_csv("test2.csv")

def ingest_data():
    client = Opik()
    dataset1 = client.get_or_create_dataset(name="RAG Evaluation dataset")

    qa_pairs = [
        {"input": row["Question"],
         "expected_output": row["Answer"],
         "context": row["Context"]}

        for _, row in df.iterrows()
    ]

    dataset1.insert(qa_pairs)
    return dataset1

dataset = ingest_data()

import openai
from opik.integrations.openai import track_openai

# Define the task to evaluate
openai_client = track_openai(openai.OpenAI())

wf = RouterOutputAgentWorkflow(tools=[sql_tool, llama_cloud_tool], verbose=True, timeout=300)


async def single(query):
    single_response = await wf.run(message=query)
    print(f"single response {single_response}")
    return single_response

test_df= pd.read_csv("test1.csv")

def get_answers(test_df):
    responses= {}
    for _, row in test_df.iterrows():
        query = row['Question']
        response = asyncio.run(single(query))
        responses[query] = response

    return responses

responses = get_answers(test_df)

print(f"responses {responses}")

def evaluation_task(x):
    input_question = x['input']
    if input_question in responses:
        expected_output = responses[input_question]
        return {
            "output": expected_output
        }


from opik.evaluation.metrics import (
    Hallucination,
    AnswerRelevance,
    ContextPrecision,
    ContextRecall
)

hallucination_metric = Hallucination()
answer_relevance_metric = AnswerRelevance()
context_precision_metric = ContextPrecision()
context_recall_metric = ContextRecall()

from opik.evaluation import evaluate

evaluation = evaluate(
    dataset=dataset,
    task=evaluation_task,
    scoring_metrics=[hallucination_metric, answer_relevance_metric,
                     context_precision_metric, context_recall_metric],
    experiment_config={
        "model": MODEL
    }
)

print(evaluation)


