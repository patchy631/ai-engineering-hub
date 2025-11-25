from beam import Image, Pod

def load_model():
    import subprocess
    import time

    subprocess.Popen(["ollama", "serve"])
    time.sleep(5)
    subprocess.run(["ollama", "pull", "gemma3:4b"], check=True)


image = Image().add_python_packages([
        "streamlit",
        "nest-asyncio",
        "load_dotenv",
        "llama-index==0.12.33",
        "llama-index-embeddings-fastembed==0.3.1",
        "llama-index-vector-stores-milvus==0.8.4",
        "llama-index-llms-ollama==0.6.2",
        "llama-index-llms-openai==0.3.12",
        "llama-index-readers-web==0.3.9",
        "IPython",
        "ollama",
        "llama-index-core==0.12.33.post1",
    ])

streamlit_server = Pod(
    image=image,
    ports=[8501],  # Default port for streamlit
    gpu="T4",
    memory="2Gi",
    entrypoint=["streamlit", "run", "app.py"],
    env={"OPENAI_API_KEY": "...",
         "FIRECRAWL_API_KEY": "..."}
)
res = streamlit_server.create()

print("✨ Streamlit server hosted at:", res.url)