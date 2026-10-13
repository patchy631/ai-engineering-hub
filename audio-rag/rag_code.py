import os
import time
import asyncio
from typing import List, Dict

import voyageai
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel

from llama_index.llms.openrouter import OpenRouter

from speechmatics.batch import AsyncClient, TranscriptionConfig

load_dotenv()

# RAG defaults (secrets live in .env)
EMBED_MODEL = "voyage-context-3"
LLM_MODEL = "deepseek/deepseek-v3.2"
INGEST_BATCH_SIZE = 512
RETRIEVAL_TOP_K = 2
DB_NAME = "rag_audio_db"
COLLECTION_NAME = "chat_with_audios"
VECTOR_DIM = 1024


def batch_iterate(lst, batch_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]


class EmbedData:
    """Generates contextualized chunk embeddings using Voyage AI voyage-context-3."""

    def __init__(self, embed_model_name=EMBED_MODEL):
        self.embed_model_name = embed_model_name
        self.embeddings = []
        self.contexts = []
        self.client = voyageai.Client(api_key=os.getenv("VOYAGE_API_KEY"))

    def embed(self, contexts):
        # All speaker turns from one audio file are embedded together so each chunk
        # carries full transcript context (voyage-context-3's key advantage).
        self.contexts = contexts
        result = self.client.contextualized_embed(
            inputs=[contexts],
            model=self.embed_model_name,
            input_type="document",
        )
        self.embeddings = result.results[0].embeddings

    def embed_query(self, query):
        result = self.client.contextualized_embed(
            inputs=[[query]],
            model=self.embed_model_name,
            input_type="query",
        )
        return result.results[0].embeddings[0]


class MongoVDB:
    """MongoDB Atlas Vector Search store. Requires an Atlas cluster (M0 free tier works)."""

    EMBEDDING_FIELD = "embedding"
    VECTOR_INDEX_NAME = "vector_index"

    def __init__(
        self,
        db_name=DB_NAME,
        collection_name=COLLECTION_NAME,
        vector_dim=VECTOR_DIM,
    ):
        self.db_name = db_name
        self.collection_name = collection_name
        self.vector_dim = vector_dim

    def define_client(self):
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def create_collection(self):
        # Atlas requires the collection to exist before creating a search index.
        if self.collection_name not in self.db.list_collection_names():
            self.db.create_collection(self.collection_name)

        existing = list(self.collection.list_search_indexes())
        if any(idx["name"] == self.VECTOR_INDEX_NAME for idx in existing):
            return

        search_index_model = SearchIndexModel(
            definition={
                "fields": [
                    {
                        "type": "vector",
                        "path": self.EMBEDDING_FIELD,
                        "numDimensions": self.vector_dim,
                        "similarity": "dotProduct",
                    }
                ]
            },
            name=self.VECTOR_INDEX_NAME,
            type="vectorSearch",
        )
        self.collection.create_search_index(model=search_index_model)
        self._wait_for_index_ready()

    def _wait_for_index_ready(self, timeout=120):
        # Atlas builds search indexes asynchronously; poll until queryable.
        start = time.time()
        while time.time() - start < timeout:
            indexes = list(self.collection.list_search_indexes(self.VECTOR_INDEX_NAME))
            if indexes and indexes[0].get("queryable"):
                return
            time.sleep(2)

    def ingest_data(self, embeddata):
        # Clear any previous data for this demo collection so re-uploads don't duplicate.
        self.collection.delete_many({})

        docs = [
            {"context": context, self.EMBEDDING_FIELD: embedding}
            for context, embedding in zip(embeddata.contexts, embeddata.embeddings)
        ]
        for batch in batch_iterate(docs, INGEST_BATCH_SIZE):
            self.collection.insert_many(batch)


class Retriever:
    def __init__(self, vector_db, embeddata):
        self.vector_db = vector_db
        self.embeddata = embeddata

    def search(self, query, top_k=RETRIEVAL_TOP_K, num_candidates=50):
        query_embedding = self.embeddata.embed_query(query)

        pipeline = [
            {
                "$vectorSearch": {
                    "index": self.vector_db.VECTOR_INDEX_NAME,
                    "path": self.vector_db.EMBEDDING_FIELD,
                    "queryVector": query_embedding,
                    "numCandidates": num_candidates,
                    "limit": top_k,
                }
            },
            {
                "$project": {
                    "context": 1,
                    "score": {"$meta": "vectorSearchScore"},
                }
            },
        ]

        return list(self.vector_db.collection.aggregate(pipeline))


class RAG:
    def __init__(self, retriever, llm_name=LLM_MODEL):
        self.retriever = retriever
        self.llm = OpenRouter(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            model=llm_name,
            temperature=0.7,
            context_window=128000,
        )
        self.qa_prompt_tmpl_str = (
            "Context information is below.\n"
            "---------------------\n"
            "{context}\n"
            "---------------------\n"
            "Given the context information above I want you to think step by step to answer "
            "the query in a crisp manner; if you don't know the answer say 'I don't know!'.\n"
            "Query: {query}\n"
            "Answer: "
        )

    def generate_context(self, query):
        results = self.retriever.search(query, top_k=RETRIEVAL_TOP_K)
        return "\n\n---\n\n".join(doc["context"] for doc in results)

    def query(self, query):
        prompt = self.qa_prompt_tmpl_str.format(
            context=self.generate_context(query),
            query=query,
        )
        return self.llm.stream_complete(prompt)


class Transcribe:
    """Transcribes audio with speaker diarization using Speechmatics batch API."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def transcribe_audio(self, audio_path: str) -> List[Dict[str, str]]:
        return asyncio.run(self._transcribe_async(audio_path))

    async def _transcribe_async(self, audio_path: str) -> List[Dict[str, str]]:
        async with AsyncClient(api_key=self.api_key) as client:
            result = await client.transcribe(
                audio_path,
                transcription_config=TranscriptionConfig(
                    language="en",
                    diarization="speaker",
                    speaker_diarization_config={
                        "speaker_sensitivity": 0.85,
                        "prefer_current_speaker": True,
                    },
                ),
            )

        # Group consecutive words from the same Speechmatics speaker tag (S1, S2, ...).
        # Only split on speaker changes — same logic as the Speechmatics SDK formatter.
        speaker_turns = []
        current_speaker = None
        current_words = []

        for item in result.results:
            if not item.alternatives:
                continue
            alt = item.alternatives[0]
            speaker = alt.speaker or "Unknown"
            content = alt.content

            if speaker != current_speaker:
                if current_words:
                    speaker_turns.append({"speaker": current_speaker, "text": " ".join(current_words)})
                current_speaker = speaker
                current_words = []
            if item.type == "punctuation" and current_words:
                current_words[-1] += content
            elif content:
                current_words.append(content)

        if current_words:
            speaker_turns.append({"speaker": current_speaker, "text": " ".join(current_words)})

        return speaker_turns


def format_speaker(speaker_id: str) -> str:
    """Map Speechmatics speaker tags (S1, S2, ...) to display labels."""
    if speaker_id.startswith("S") and speaker_id[1:].isdigit():
        return f"Speaker {chr(ord('A') + int(speaker_id[1:]) - 1)}"
    return speaker_id


def build_rag_pipeline(file_path: str) -> tuple[RAG, List[Dict[str, str]]]:
    """Transcribe audio, embed speaker turns, and return a ready RAG instance."""
    transcripts = Transcribe(api_key=os.getenv("SPEECHMATICS_API_KEY")).transcribe_audio(file_path)
    documents = [f"{format_speaker(t['speaker'])}: {t['text']}" for t in transcripts]

    embeddata = EmbedData()
    embeddata.embed(documents)

    mongo_vdb = MongoVDB()
    mongo_vdb.define_client()
    mongo_vdb.create_collection()
    mongo_vdb.ingest_data(embeddata=embeddata)

    retriever = Retriever(vector_db=mongo_vdb, embeddata=embeddata)
    return RAG(retriever=retriever), transcripts
