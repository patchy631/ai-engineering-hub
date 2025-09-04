from beam import Image, Pod

streamlit_server = Pod(
    image=Image().add_python_packages([
        "streamlit",
        "groundx",
        "python-dotenv",
        "requests",
        "openai",
        "opik",
        "PyMuPDF"
    ]),
    ports=[8501],  # Default port for streamlit
    cpu=4,
    memory="2Gi",
    entrypoint=["streamlit", "run", "app.py"],
)

res = streamlit_server.create()

print("✨ Streamlit server hosted at:", res.url)
