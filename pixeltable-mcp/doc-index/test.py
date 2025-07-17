import pixeltable as pxt
from pixeltable.iterators import DocumentSplitter
from pixeltable.functions.huggingface import sentence_transformer

# Initialize app structure
pxt.drop_dir("pdf_search", force=True)
pxt.create_dir("pdf_search")

# Create documents table
documents_t = pxt.create_table(
    "pdf_search.documents", 
    {"pdf": pxt.Document}
)

# Create chunked view for efficient processing
documents_chunks = pxt.create_view(
    "pdf_search.document_chunks",
    documents_t,
    iterator=DocumentSplitter.create(
        document=documents_t.pdf,
        separators="token_limit",
        limit=300  # Tokens per chunk
    )
)

# Configure embedding model
embed_model = sentence_transformer.using(
    model_id="intfloat/e5-large-v2"
)

# Add search capability
documents_chunks.add_embedding_index(
    column="text",
    string_embed=embed_model
)

# Define search query
@pxt.query
def search_documents(query_text: str, limit: int = 5):
    sim = documents_chunks.text.similarity(query_text)
    return (
        documents_chunks.order_by(sim, asc=False)
        .select(
            documents_chunks.text,
            similarity=sim
        )
        .limit(limit)
    )

# Sample document URLs
DOCUMENT_URL = (
    "https://github.com/pixeltable/pixeltable/raw/release/docs/resources/rag-demo/"
)

document_urls = [
    DOCUMENT_URL + doc for doc in [
        "Argus-Market-Digest-June-2024.pdf",
        "Company-Research-Alphabet.pdf",
        "Zacks-Nvidia-Report.pdf",
    ]
]

# Add documents to database
documents_t.insert({"pdf": url} for url in document_urls)

# Search documents
@pxt.query
def find_relevant_text(query: str, top_k: int = 5):
    sim = documents_chunks.text.similarity(query)
    return (
        documents_chunks.order_by(sim, asc=False)
        .select(
            documents_chunks.text,
            similarity=sim
        )
        .limit(top_k)
    )

# Example search
results = find_relevant_text(
    "What are the growth projections for tech companies?"
).collect()

# Print results
for r in results:
    print(f"Similarity: {r['similarity']:.3f}")
    print(f"Text: {r['text']}\n")