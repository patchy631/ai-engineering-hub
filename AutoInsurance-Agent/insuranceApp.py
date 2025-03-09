import json
import asyncio
import nest_asyncio
import streamlit as st
import packages.claim.documents as dc
import packages.claim.insurance as ins
from llama_cloud.client import LlamaCloud
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import Event
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

class LogEvent(Event):
    msg: str
    delta: bool = False

async def stream_workflow(workflow, **workflow_kwargs):
    handler = workflow.run(**workflow_kwargs)
    async for event in handler.stream_events():
        if isinstance(event, LogEvent):
            if event.delta:
                print(event.msg, end="")
            else:
                print(event.msg)

    return await handler

nest_asyncio.apply()
initContext = False

claims = {"data/alice.json": ["Alice Johnson", "alice"], 
          "data/john.json": ["John Smith", "john"]}

for k,v in claims.items():
    with open(k, "r") as f:
        data = json.load(f)
    claims[k].append(data)

st.title("Your AI Insurance Claim Advisor :-)")
st.caption("An AI crew ready to recommend the best course of action based on the current XYZ insurance policies and the claim information")

option = st.selectbox(
    "Which insurance claim would you want to analize?",
    options=list(claims.keys()), format_func=lambda x: claims[x][0],
    index=None,
    placeholder="Select a claim..."
)


if option:
    if initContext==False:
        index = LlamaCloudIndex(
                    #Configure your index in Llama and add the parameters as stated after setting up.
                    #You can also use another Open Source solutions such as Qdrant
                    #name="...", 
                    #project_name="...",
                    #organization_id="...",
                    #api_key="..."
                    )

        declarations_index = LlamaCloudIndex(
                        #Configure your index in Llama and add the parameters as stated after setting up.
                        #You can also use another Open Source solutions such as Qdrant
                        #name="...", 
                        #project_name="...",
                        #organization_id="...",
                        #api_key="..."
                        )

        client = LlamaCloud(
                        #Get the URL and token from your Index Provider. In this case, we will use Llama
                        #base_url="...",
                        #token=os.environ["LLAMA_CLOUD_API_KEY"],
                    )

        retriever = dc.documents(policy_index=index, declarations_index=declarations_index, client=client)
        upserted_documents = retriever.load_data_index(claims)

        llm = OpenAI(model="gpt-4o", 
                     #api_key=os.environ["OPEN_API_KEY"]
                     )

        initContext = True

    st.write("Let's check the data from the claim:", option)
    claim_info = claims[option][2]
    st.json(claim_info)
    
    if st.button("See declaration and Run recommendation"):
        docs = retriever.get_declarations_docs(claim_info["policy_number"])
        st.write(docs[0].get_content())

        retrieverPolicy = retriever.get_policy_retriever()
        workflow = ins.AutoInsuranceWorkflow(
            docs = docs,
            policy_retriever=retrieverPolicy,
            llm=llm,
            verbose=True,
            timeout=None,  
        )
        response = asyncio.run(stream_workflow(workflow, claim_json_path=claim_info))
        st.table(dict(response["decision"]))
        