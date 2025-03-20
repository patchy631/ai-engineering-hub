import pandas as pd
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import Document
from llama_index.core.node_parser import SentenceSplitter

def create_sample_vector_index(embed_model):
    """
    Create a sample VectorStoreIndex with pre-defined city documents.
    Useful for demonstration if no CSVs are uploaded.
    """
    city_texts = [
        "New York City is the most populous city in the United States. Located at the southern tip of New York State, the city is the center of the New York metropolitan area, the largest metropolitan area in the world by urban area. New York City is known for its iconic landmarks including the Statue of Liberty, Empire State Building, Central Park, and Times Square.",
        "Los Angeles is the largest city in California. It is known for its Mediterranean climate, ethnic and cultural diversity, Hollywood entertainment industry, and sprawling metropolitan area. Popular attractions include the Hollywood Sign, Griffith Observatory, and the Getty Center.",
        "Chicago is the third-most populous city in the United States. Located on the shores of Lake Michigan, Chicago is known for its architecture, skyline featuring the Willis Tower, and cultural attractions like Millennium Park and the Art Institute of Chicago.",
        "Houston is the most populous city in Texas. It is known for being home to the NASA Johnson Space Center, the Museum District, and a diverse culinary scene. Houston has a strong economy based on energy, manufacturing, and healthcare industries.",
        "Miami is known for its beaches, Art Deco architecture in South Beach, and vibrant cultural scene. It has a large Latin American population, giving it a unique cultural atmosphere.",
        "Seattle is famous for its coffee culture, the Space Needle, Pike Place Market, and technology industry with companies like Microsoft and Amazon headquartered in the area. It's surrounded by water, mountains, and evergreen forests."
    ]
    documents = [Document(text=text) for text in city_texts]
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(documents)
    return VectorStoreIndex(nodes, embed_model=embed_model)

def add_csv_rows_to_index(df: pd.DataFrame, embed_model, existing_index=None):
    """
    Convert CSV rows into Document form and add them to an existing index if provided;
    otherwise create a new index from the rows.
    """
    texts = []
    for idx, row in df.iterrows():
        row_text = f"Row {idx+1}: " + ", ".join([f"{col}: {val}" for col, val in row.items()])
        texts.append(row_text)
    
    documents = [Document(text=text) for text in texts]
    splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
    nodes = splitter.get_nodes_from_documents(documents)
    
    if existing_index:
        for node in nodes:
            existing_index.insert_nodes([node])
        return existing_index
    else:
        return VectorStoreIndex(nodes, embed_model=embed_model)