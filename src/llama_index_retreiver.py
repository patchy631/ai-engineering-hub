import os
from llama_index.indices.managed.llama_cloud import LlamaCloudIndex

# https://www.jaad.org/action/showPdf?pii=S0190-9622%2823%2902878-5
# https://www.nhlbi.nih.gov/resources/2020-focused-updates-asthma-management-guidelines

# Create a new LlamaCloudIndex for the docs mentioned in the url above
# index = LlamaCloudIndex.from_documents(
#     documents,
#     index_id="medical_guidelines",
#     project_name="llamacloud_demo",
#     api_key= os.environ.get("LLAMA_CLOUD_API_KEY"),  # Replace with your API key
#     verbose=True,
# )


retreiver_index = LlamaCloudIndex(
  name="medical_guidelines", 
  project_name="llamacloud_demo",
  api_key= os.environ.get("LLAMA_CLOUD_API_KEY")
)

retriever = retreiver_index.as_retriever(similarity_top_k=3)