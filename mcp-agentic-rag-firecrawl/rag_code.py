from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from tqdm import tqdm
from qdrant_client import models
from qdrant_client import QdrantClient

faq_text = """Question 1: What is the first step before building a machine learning model?
Answer 1: Understand the problem, define the objective, and identify the right metrics for evaluation.

Question 2: How important is data cleaning in ML?
Answer 2: Extremely important. Clean data improves model performance and reduces the chance of misleading results.

Question 3: Should I normalize or standardize my data?
Answer 3: Yes, especially for models sensitive to feature scales like SVMs, KNN, and neural networks.

Question 4: When should I use feature engineering?
Answer 4: Always consider it. Well-crafted features often yield better results than complex models.

Question 5: How to handle missing values?
Answer 5: Use imputation techniques like mean/median imputation, or model-based imputation depending on the context.

Question 6: Should I balance my dataset for classification tasks?
Answer 6: Yes, especially if the classes are imbalanced. Techniques include resampling, SMOTE, and class-weighting.

Question 7: How do I select features for my model?
Answer 7: Use domain knowledge, correlation analysis, or techniques like Recursive Feature Elimination or SHAP values.

Question 8: Is it good to use all features available?
Answer 8: Not always. Irrelevant or redundant features can reduce performance and increase overfitting.

Question 9: How do I avoid overfitting?
Answer 9: Use techniques like cross-validation, regularization, pruning (for trees), and dropout (for neural nets).

Question 10: Why is cross-validation important?
Answer 10: It provides a more reliable estimate of model performance by reducing bias from a single train-test split.

Question 11: What’s a good train-test split ratio?
Answer 11: Common ratios are 80/20 or 70/30, but use cross-validation for more robust evaluation.

Question 12: Should I tune hyperparameters?
Answer 12: Yes. Use grid search, random search, or Bayesian optimization to improve model performance.

Question 13: What’s the difference between training and validation sets?
Answer 13: Training set trains the model, validation set tunes hyperparameters, and test set evaluates final performance.

Question 14: How do I know if my model is underfitting?
Answer 14: It performs poorly on both training and test sets, indicating it hasn’t learned patterns well.

Question 15: What are signs of overfitting?
Answer 15: High accuracy on training data but poor generalization to test or validation data.

Question 16: Is ensemble modeling useful?
Answer 16: Yes. Ensembles like Random Forests or Gradient Boosting often outperform individual models.

Question 17: When should I use deep learning?
Answer 17: Use it when you have large datasets, complex patterns, or tasks like image and text processing.

Question 18: What is data leakage and how to avoid it?
Answer 18: Data leakage is using future or target-related information during training. Avoid by carefully splitting and preprocessing.

Question 19: How do I measure model performance?
Answer 19: Choose appropriate metrics: accuracy, precision, recall, F1, ROC-AUC for classification; RMSE, MAE for regression.

Question 20: Why is model interpretability important?
Answer 20: It builds trust, helps debug, and ensures compliance—especially important in high-stakes domains like healthcare.
"""

new_faq_text = [i.replace("\n", " ") for i in faq_text.split("\n\n")]
def batch_iterate(lst, batch_size):
    for i in range(0, len(lst), batch_size):
        yield lst[i : i + batch_size]

class EmbedData:

    def __init__(self, 
                 embed_model_name="nomic-ai/nomic-embed-text-v1.5",
                 batch_size=32):
        
        self.embed_model_name = embed_model_name
        self.embed_model = self._load_embed_model()
        self.batch_size = batch_size
        self.embeddings = []

    def _load_embed_model(self):
        embed_model = HuggingFaceEmbedding(model_name=self.embed_model_name,
                                           trust_remote_code=True,
                                        #    cache_folder='./hf_cache'
                                           )
        return embed_model
    
    def generate_embedding(self, context):
        return self.embed_model.get_text_embedding_batch(context)
    
    def embed(self, contexts):
        self.contexts = contexts
        
        for batch_context in tqdm(batch_iterate(contexts, self.batch_size),
                                  total=len(contexts)//self.batch_size,
                                  desc="Embedding data in batches"):
                                  
            batch_embeddings = self.generate_embedding(batch_context)
            
            self.embeddings.extend(batch_embeddings)



class QdrantVDB:

    def __init__(self, collection_name, vector_dim=768, batch_size=512):
        self.collection_name = collection_name
        self.batch_size = batch_size
        self.vector_dim = vector_dim
        self.define_client()

    def define_client(self):
        self.client = QdrantClient(url="http://localhost:6333",
                                   prefer_grpc=True)
        
    def create_collection(self):
        
        if not self.client.collection_exists(collection_name=self.collection_name):

            self.client.create_collection(collection_name=self.collection_name,
                                          
                                          vectors_config=models.VectorParams(
                                                              size=self.vector_dim,
                                                              distance=models.Distance.DOT,
                                                              on_disk=True),
                                          
                                          optimizers_config=models.OptimizersConfigDiff(
                                                                            default_segment_number=5,
                                                                            indexing_threshold=0)
                                         )
            
    def ingest_data(self, embeddata):
        
        for batch_context, batch_embeddings in tqdm(zip(batch_iterate(embeddata.contexts, self.batch_size), 
                                                        batch_iterate(embeddata.embeddings, self.batch_size)), 
                                                    total=len(embeddata.contexts)//self.batch_size, 
                                                    desc="Ingesting in batches"):
        
            self.client.upload_collection(collection_name=self.collection_name,
                                        vectors=batch_embeddings,
                                        payload=[{"context": context} for context in batch_context])

        self.client.update_collection(collection_name=self.collection_name,
                                    optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000)
                                    )
        
class Retriever:

    def __init__(self, vector_db, embeddata):
        
        self.vector_db = vector_db
        self.embeddata = embeddata

    def search(self, query):
        query_embedding = self.embeddata.embed_model.get_query_embedding(query)

        # select the top 3 results
        result = self.vector_db.client.search(
            collection_name=self.vector_db.collection_name,
            
            query_vector=query_embedding,
            
            search_params=models.SearchParams(
                quantization=models.QuantizationSearchParams(
                    ignore=True,
                    rescore=True,
                    oversampling=2.0,
                )
            ),
            limit=3,
            timeout=1000,
        )

        context = [dict(data) for data in result]
        combined_prompt = []

        for entry in context[:3]:
            context = entry["payload"]["context"]

            combined_prompt.append(context)

        final_output = "\n\n---\n\n".join(combined_prompt)
        return final_output