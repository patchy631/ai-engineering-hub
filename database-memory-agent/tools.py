from config import vector_collection
from ingest_data import get_embedding

def vector_search_tool(user_input: str) -> str:
    query_embedding = get_embedding(user_input)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "exact": True,
                "limit": 5,
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
            }
        },
    ]

    results = vector_collection.aggregate(pipeline)
    array_of_results = []
    for doc in results:
        array_of_results.append(doc)
    return array_of_results


def calculator_tool(user_input: str) -> str:
    try:
        result = eval(user_input)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


