import torch
from qdrant_client import models
from qdrant_client import QdrantClient
from colpali_engine.models import ColPali, ColPaliProcessor
from Janus.janus.models import MultiModalityCausalLM, VLChatProcessor
from Janus.janus.utils.io import load_pil_images
from transformers import AutoModelForCausalLM
import base64
from io import BytesIO
from tqdm import tqdm

def batch_iterate(lst, batch_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]

def image_to_base64(image):
    buffered = BytesIO()

    image.save(buffered, format="JPEG")

    return base64.b64encode(buffered.getvalue()).decode("utf-8")

class EmbedData:

    def __init__(self, embed_model_name="vidore/colpali-v1.2", batch_size = 4):
        self.embed_model_name = embed_model_name
        self.embed_model, self.processor = self._load_embed_model()
        self.batch_size = batch_size
        self.embeddings = []
        
    def _load_embed_model(self):
        embed_model = ColPali.from_pretrained(
            self.embed_model_name,
            torch_dtype=torch.bfloat16,
            device_map="mps",
            trust_remote_code=True, 
            cache_dir="./Janus/hf_cache"
        )

        processor = ColPaliProcessor.from_pretrained(self.embed_model_name)
        return embed_model, processor
    
    def get_query_embedding(self, query):
        
        with torch.no_grad():
            query = self.processor.process_queries([query]).to(self.embed_model.device)
            
            query_embedding = self.embed_model(**query)

        return query_embedding[0].cpu().float().numpy().tolist()

    def generate_embedding(self, images):
        with torch.no_grad():
            batch_images = self.processor.process_images(images).to(self.embed_model.device)
            image_embeddings = self.embed_model(**batch_images).cpu().float().numpy().tolist()
        
        return image_embeddings
        
    def embed(self, images):
        
        self.images = images
        self.all_embeddings = []

        for batch_images in tqdm(batch_iterate(images, self.batch_size), desc="Generating embeddings"):
            batch_embeddings = self.generate_embedding(batch_images)
            self.embeddings.extend(batch_embeddings)

class QdrantVDB_QB:

    def __init__(self, collection_name, vector_dim = 128, batch_size=4):
        self.collection_name = collection_name
        self.batch_size = batch_size
        self.vector_dim = vector_dim
        
    def define_client(self):
        
        self.client = QdrantClient(url="http://localhost:6333", prefer_grpc=True)
        
    def create_collection(self):
        
        if not self.client.collection_exists(collection_name=self.collection_name):

            self.client.create_collection(
                collection_name=self.collection_name,
                on_disk_payload=True,
                vectors_config=models.VectorParams(
                    size=self.vector_dim,
                    distance=models.Distance.COSINE,
                    on_disk=True,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM
                    ),
                ),
            )

    def ingest_data(self, embeddata):
    
        for i, batch_embeddings in tqdm(enumerate(batch_iterate(embeddata.embeddings, self.batch_size)), desc="Ingesting data"):

            points = []
            for j, embedding in enumerate(batch_embeddings):

                image_bs64 = image_to_base64(embeddata.images[i*self.batch_size + j])
                                    
                current_point = models.PointStruct(id=i*self.batch_size + j,
                                                   vector=embedding,
                                                   payload={"image": image_bs64})

                points.append(current_point)
    
            self.client.upsert(collection_name=self.collection_name, points=points, wait=True)
        
class Retriever:

    def __init__(self, vector_db, embeddata):
        
        self.vector_db = vector_db
        self.embeddata = embeddata

    def search(self, query):
        query_embedding = self.embeddata.get_query_embedding(query)
        
        query_result = self.vector_db.client.query_points(collection_name=self.vector_db.collection_name,
                                        query=query_embedding,
                                        limit=4,
                                        search_params=models.SearchParams(
                                        quantization=models.QuantizationSearchParams(
                                        ignore=True,
                                            rescore=True,
                                            oversampling=2.0
                                            )
                                        )
                                    )

        return query_result
    
class RAG:

    def __init__(self,
                 retriever,
                 llm_name = "deepseek-ai/Janus-Pro-1B"
                 ):
        
        self.llm_name = llm_name
        self._setup_llm()
        self.retriever = retriever

    def _setup_llm(self):

        self.vl_chat_processor = VLChatProcessor.from_pretrained(self.llm_name, cache_dir="./Janus/hf_cache")
        self.tokenizer = self.vl_chat_processor.tokenizer

        self.vl_gpt = AutoModelForCausalLM.from_pretrained(
            self.llm_name, trust_remote_code=True, cache_dir="./Janus/hf_cache"
        ).to(torch.bfloat16).eval()

    def generate_context(self, query):

        result = self.retriever.search(query)
        return f"./images/page{result.points[0].id}.jpg"

    def query(self, query):
        image_context = self.generate_context(query=query)

        qa_prompt_tmpl_str = f"""The user has asked the following question:

                        ---------------------
                        
                        Query: {query}
                        
                        ---------------------

                        Some images are available to you
                        for this question. You have
                        to understand these images thoroughly and 
                        extract all relevant information that will 
                        help you answer the query.
                                     
                        ---------------------
                        """
        
        conversation = [
            {
                "role": "User",
                "content": f"<image_placeholder> \n {qa_prompt_tmpl_str}",
                "images": [image_context],
            },
            {"role": "Assistant", "content": ""},
        ]

        pil_images = load_pil_images(conversation)
        prepare_inputs = self.vl_chat_processor(
            conversations=conversation, images=pil_images, force_batchify=True
        ).to(self.vl_gpt.device)

        inputs_embeds = self.vl_gpt.prepare_inputs_embeds(**prepare_inputs)

        outputs = self.vl_gpt.language_model.generate(
            inputs_embeds=inputs_embeds,
            attention_mask=prepare_inputs.attention_mask,
            pad_token_id=self.tokenizer.eos_token_id,
            bos_token_id=self.tokenizer.bos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
            max_new_tokens=512,
            do_sample=False,
            use_cache=True,
        )
        streaming_response = self.tokenizer.decode(outputs[0].cpu().tolist(), skip_special_tokens=True)
        
        return streaming_response
