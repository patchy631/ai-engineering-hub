import os
import nest_asyncio
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core.settings import Settings
from llama_index.core.workflow import Event, Context, Workflow, StartEvent, StopEvent, step
from llama_index.core.schema import NodeWithScore
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.response_synthesizers import CompactAndRefine

# Add model mapping
MODELS = {
    "Qwen3": "qwen3",
    "DeepSeek-R1": "deepseek-r1"
}

class RetrieverEvent(Event):
    """Result of running retrieval"""
    nodes: list[NodeWithScore]

class RAGWorkflow(Workflow):
    def __init__(self, llm_choice="Qwen3", embedding_model="BAAI/bge-large-en-v1.5"):
        super().__init__()
        # Get the correct model name based on selection
        model_name = MODELS.get(llm_choice)
        if not model_name:
            raise ValueError(f"Invalid LLM choice. Please select from: {', '.join(MODELS.keys())}")
            
        # Initialize LLM and embedding model
        self.llm = Ollama(model=model_name)
        self.embed_model = FastEmbedEmbedding(model_name=embedding_model)
        
        # Configure global settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        
        self.index = None

    @step
    async def ingest(self, ctx: Context, ev: StartEvent) -> StopEvent | None:
        """Entry point to ingest documents from a directory."""
        dirname = ev.get("dirname")
        if not dirname:
            return None

        documents = SimpleDirectoryReader(dirname).load_data()
        self.index = VectorStoreIndex.from_documents(documents=documents)
        return StopEvent(result=self.index)

    @step
    async def retrieve(self, ctx: Context, ev: StartEvent) -> RetrieverEvent | None:
        """Entry point for RAG retrieval."""
        query = ev.get("query")
        index = ev.get("index") or self.index

        if not query:
            return None

        if index is None:
            print("Index is empty, load some documents before querying!")
            return None

        retriever = index.as_retriever(similarity_top_k=2)
        nodes = await retriever.aretrieve(query)
        await ctx.set("query", query)
        return RetrieverEvent(nodes=nodes)

    @step
    async def synthesize(self, ctx: Context, ev: RetrieverEvent) -> StopEvent:
        """Generate a response using retrieved nodes."""
        summarizer = CompactAndRefine(streaming=True, verbose=True)
        query = await ctx.get("query", default=None)
        response = await summarizer.asynthesize(query, nodes=ev.nodes)
        return StopEvent(result=response)

    async def query(self, query_text: str):
        """Helper method to perform a complete RAG query."""
        if self.index is None:
            raise ValueError("No documents have been ingested. Call ingest_documents first.")
        
        result = await self.run(query=query_text, index=self.index)
        return result

    async def ingest_documents(self, directory: str):
        """Helper method to ingest documents."""
        result = await self.run(dirname=directory)
        self.index = result
        return result

# Example usage
async def main():
    # Initialize the workflow
    workflow = RAGWorkflow(llm_choice="Qwen3")
    
    # Ingest documents
    await workflow.ingest_documents("data")
    
    # Perform a query
    result = await workflow.query("How was DeepSeekR1 trained?")
    
    # Print the response
    async for chunk in result.async_response_gen():
        print(chunk, end="", flush=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main()) 