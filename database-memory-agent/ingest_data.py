from config import vector_collection, voyage_client, VOYAGE_MODEL
from pymongo.operations import SearchIndexModel
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import time

def get_embedding(data, input_type = "document"):
  embeddings = voyage_client.embed(
      data, model = VOYAGE_MODEL, input_type = input_type
  ).embeddings
  return embeddings[0]

def ingest_data():
    loader = PyPDFLoader("https://investors.mongodb.com/node/13176/pdf")
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=20)
    documents = text_splitter.split_documents(data)
    print(f"Successfully split PDF into {len(documents)} chunks.")

    print("Generating embeddings and ingesting documents...")
    docs_to_insert = []
    for i, doc in enumerate(documents):
        embedding = get_embedding(doc.page_content)
        if embedding:
            docs_to_insert.append({
                "text": doc.page_content,
                "embedding": embedding
            })

    if docs_to_insert:
        result = vector_collection.insert_many(docs_to_insert)
        print(f"Inserted {len(result.inserted_ids)} documents into the collection.")
    else:
        print("No documents were inserted. Check embedding generation process.")

    index_name = "vector_index"
    
    search_index_model = SearchIndexModel(
        definition = {
            "fields": [
                {
                    "type": "vector",
                    "numDimensions": 1024, 
                    "path": "embedding",
                    "similarity": "cosine"
                }
            ]
        },
        name=index_name,
        type="vectorSearch"
    )
    try:
        vector_collection.create_search_index(model=search_index_model)
        print(f"Search index '{index_name}' creation initiated.")
    except Exception as e:
        print(f"Error creating search index: {e}")
        return

    print("Polling to check if the index is ready. This may take up to a minute.")
    predicate=None
    if predicate is None:
       predicate = lambda index: index.get("queryable") is True

    while True:
       indices = list(vector_collection.list_search_indexes(index_name))
       if len(indices) and predicate(indices[0]):
          break
       time.sleep(5)
    print(index_name + " is ready for querying.")
