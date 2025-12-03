# RAG-Based PDF Query System

This project demonstrates a Retrieval-Augmented Generation (RAG) system to query information from a PDF using AI models. It uses LangChain, Hugging Face embeddings, Qdrant vector storage, and Groq API for conversational question-answering.

# Demo Video:
https://www.youtube.com/watch?v=aho48B1psXM

## Features
- **PDF Processing**: Extract text from PDF resumes and split into chunks.
- **Vector Embeddings**: Generate embeddings using Hugging Face's `all-MiniLM-L6-v2`.
- **Vector Storage**: Store embeddings in Qdrant (in-memory).
- **Conversational AI**: Answer questions using Groq's `qwen-2.5-32b` model.
- **Multi-Turn Conversations**: Supports follow-up questions with conversation history.

## Installation
1. **Clone the repository**:
   ```bash
   git clone [your-repository-url]
   cd [repository-directory]
   ```
2. **Create virtual environment (optional):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. **Install dependencies:**
   ```bash
   pip install langchain-groq python-dotenv langchain-community pypdf huggingface-hub langchain-qdrant qdrant-client
   ```
4. **Environment setup:**
   - Create a `.env` file and add your Groq API key:
   ```
   groq_api_key=your_api_key_here
   ```

## Usage
Modify the PDF path in the code:
   ```python
   file_path = r"your_file_path"
   ```
Run the system:
   ```python
   # Load PDF
   loader = PyPDFLoader(file_path)
   docs = loader.load()

   # Split text
   text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)
   splits = text_splitter.split_documents(docs)

   # Create embeddings
   embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

   # Initialize Qdrant
   client = QdrantClient(":memory:")
   client.create_collection(
       collection_name="demo_collection",
       vectors_config=VectorParams(size=384, distance=Distance.COSINE)
   )

   # Create vector store
   vector_store = QdrantVectorStore(
       client=client,
       collection_name="demo_collection",
       embedding=embeddings
   )

   # Add documents
   vector_store.add_documents(splits)

   # Initialize conversation chain
   chain = ConversationalRetrievalChain.from_llm(
       llm=ChatGroq(model="qwen-2.5-32b"),
       retriever=vector_store.as_retriever(),
       memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
       verbose=True
   )

   # Ask questions
   print(chain.invoke({"question": "question 1?"})["answer"])
   print(chain.invoke({"question": "question 2?"})["answer"])
   ```

## Configuration
- **Model**: Default is Groq `qwen-2.5-32b`
- **Embeddings**: `all-MiniLM-L6-v2` from Hugging Face
- **Chunking**: Adjust via `RecursiveCharacterTextSplitter(chunk_size=..., chunk_overlap=...)`


## Contributing
Open an issue to discuss major changes before submitting PRs.

## License
Open-source. Modify as needed.

## Contact
For questions: www.linkedin.com/in/rohitvyavahare2001@gmail.com
