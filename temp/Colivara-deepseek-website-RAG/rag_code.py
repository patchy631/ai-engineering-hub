import torch
from colivara_py import ColiVara
from Janus.janus.models import MultiModalityCausalLM, VLChatProcessor
from Janus.janus.utils.io import load_pil_images
from transformers import AutoModelForCausalLM
import base64
from io import BytesIO
from tqdm import tqdm
from PIL import Image
import io

def batch_iterate(lst, batch_size):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]


class Retriever:

    def __init__(self, rag_client, collection_name):
        self.rag_client = rag_client
        self.collection_name = collection_name

    def search(self, query):
        results = self.rag_client.search(
            query=query,
            collection_name=self.collection_name,
            top_k=3
        )
        
        # Save the most relevant image locally
        related_image = results.results[0].img_base64
        image_data = base64.b64decode(related_image)
        image = Image.open(io.BytesIO(image_data))
        image.save("tempfile.jpeg")
        
        return "tempfile.jpeg"

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
        return self.retriever.search(query)

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
