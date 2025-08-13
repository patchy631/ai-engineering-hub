# ---------------------------------------------  Libraries  ----------------------------------------------------------#
import gradio as gr
from PyPDF2 import PdfReader
import nbformat

from langchain.text_splitter import CharacterTextSplitter, RecursiveCharacterTextSplitter, MarkdownTextSplitter, PythonCodeTextSplitter, Language
from langchain.docstore.document import Document
from langchain_community.document_loaders import Docx2txtLoader, CSVLoader

# ---------------------------------------------  Functions  ----------------------------------------------------------#

def process_uploaded_file(uploaded_file):
    text = ""
    display_content = ""
    file_extension = uploaded_file.name.split(".")[-1]

    if file_extension == "pdf":
        try:
            # Gradio's uploaded_file.name provides the path to the temporary file
            pdf = PdfReader(uploaded_file.name)
            for page in pdf.pages:
                page_text = page.extract_text()
                text += page_text + "\n"
                display_content += page_text + "\n"
        except Exception as e:
            display_content = f"Error reading PDF file: {e}"
            text = ""

    elif file_extension == "docx":
        try:
            docx_loader = Docx2txtLoader(uploaded_file.name)
            documents = docx_loader.load()
            text = "\n".join([doc.page_content for doc in documents])
            display_content = text
        except Exception as e:
            display_content = f"Error reading DOCX file: {e}"
            text = ""

    elif file_extension in ["html", "css", "py", "txt"]:
        try:
            with open(uploaded_file.name, "r", encoding="utf-8") as f:
                file_content = f.read()
            display_content = file_content  # Display as plain text in Textbox
            text = file_content
        except Exception as e:
            display_content = f"Error reading {file_extension.upper()} file: {e}"
            text = ""

    elif file_extension == "ipynb":
        try:
            # nbformat.read can take a file path
            nb_content = nbformat.read(uploaded_file.name, as_version=4)
            nb_filtered = [cell for cell in nb_content["cells"] if cell["cell_type"] in ["code", "markdown"]]
            
            for cell in nb_filtered:
                if cell["cell_type"] == "code":
                    display_content += f"```python\n{cell['source']}\n```\n"
                    text += cell["source"] + "\n"
                elif cell["cell_type"] == "markdown":
                    display_content += f"{cell['source']}\n"
                    text += cell["source"] + "\n"
        except Exception as e:
            display_content = f"Error reading IPYNB file: {e}"
            text = ""

    elif file_extension == "csv":
        try:
            loader = CSVLoader(file_path=uploaded_file.name, encoding="utf-8", csv_args={'delimiter': ','})
            documents = loader.load()
            text = "\n".join([doc.page_content for doc in documents])
            display_content = text # For CSV, display the concatenated text
        except Exception as e:
            display_content = f"Error reading CSV file: {e}"
            text = ""
    else:
        display_content = "Unsupported file type."
        text = ""

    return text, display_content


def chunk_recursive(text, chunk_size, chunk_overlap, keep_separator, add_start_index, strip_whitespace):
    if not text:
        return [], ""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        keep_separator=keep_separator,
        add_start_index=add_start_index,
        strip_whitespace=strip_whitespace,
    )
    chunks = text_splitter.create_documents([text])
    formatted_chunks = []
    for chunk in chunks:
        if isinstance(chunk, Document):
            formatted_chunks.append({"content": chunk.page_content, "metadata": chunk.metadata})
        else:
            formatted_chunks.append({"content": str(chunk), "metadata": {}})
    
    code_example = f"""
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_content = \"\"\"{text[:50]}...\"\"\" # Truncated for example

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size={chunk_size},
    chunk_overlap={chunk_overlap},
    length_function=len,
    keep_separator={keep_separator},
    add_start_index={add_start_index},
    strip_whitespace={strip_whitespace},
)
chunks = text_splitter.create_documents([text_content])
# Access chunks: chunks[0].page_content, chunks[0].metadata
"""
    return formatted_chunks, code_example

def chunk_character(text, chunk_size, chunk_overlap, separator, keep_separator, add_start_index, strip_whitespace):
    if not text:
        return [], ""
    
    if isinstance(separator, list):
        separator_str = "".join(separator)
    else:
        separator_str = separator

    text_splitter = CharacterTextSplitter(
        separator=separator_str,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        keep_separator=keep_separator,
        add_start_index=add_start_index,
        strip_whitespace=strip_whitespace,
    )
    chunks = text_splitter.create_documents([text])
    formatted_chunks = []
    for chunk in chunks:
        if isinstance(chunk, Document):
            formatted_chunks.append({"content": chunk.page_content, "metadata": chunk.metadata})
        else:
            formatted_chunks.append({"content": str(chunk), "metadata": {}})

    code_example = f"""
from langchain.text_splitter import CharacterTextSplitter

text_content = \"\"\"{text[:50]}...\"\"\" # Truncated for example

text_splitter = CharacterTextSplitter(
    separator=\"\"\"{separator_str}\"\"\",
    chunk_size={chunk_size},
    chunk_overlap={chunk_overlap},
    length_function=len,
    keep_separator={keep_separator},
    add_start_index={add_start_index},
    strip_whitespace={strip_whitespace},
)
chunks = text_splitter.create_documents([text_content])
# Access chunks: chunks[0].page_content, chunks[0].metadata
"""
    return formatted_chunks, code_example

def chunk_python_code(text, chunk_size, chunk_overlap, keep_separator, add_start_index, strip_whitespace):
    if not text:
        return [], ""
    text_splitter = PythonCodeTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        keep_separator=keep_separator,
        add_start_index=add_start_index,
        strip_whitespace=strip_whitespace,
    )
    chunks = text_splitter.create_documents([text])
    formatted_chunks = []
    for chunk in chunks:
        if isinstance(chunk, Document):
            formatted_chunks.append({"content": chunk.page_content, "metadata": chunk.metadata})
        else:
            formatted_chunks.append({"content": str(chunk), "metadata": {}})

    code_example = f"""
from langchain.text_splitter import PythonCodeTextSplitter

text_content = \"\"\"{text[:50]}...\"\"\" # Truncated for example

text_splitter = PythonCodeTextSplitter(
    chunk_size={chunk_size},
    chunk_overlap={chunk_overlap},
    keep_separator={keep_separator},
    add_start_index={add_start_index},
    strip_whitespace={strip_whitespace},
)
chunks = text_splitter.create_documents([text_content])
# Access chunks: chunks[0].page_content, chunks[0].metadata
"""
    return formatted_chunks, code_example

def chunk_javascript_code(text, chunk_size, chunk_overlap, keep_separator, add_start_index, strip_whitespace):
    if not text:
        return [], ""
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JS,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        keep_separator=keep_separator,
        add_start_index=add_start_index,
        strip_whitespace=strip_whitespace,
    )
    chunks = text_splitter.create_documents([text])
    formatted_chunks = []
    for chunk in chunks:
        if isinstance(chunk, Document):
            formatted_chunks.append({"content": chunk.page_content, "metadata": chunk.metadata})
        else:
            formatted_chunks.append({"content": str(chunk), "metadata": {}})

    code_example = f"""
from langchain.text_splitter import RecursiveCharacterTextSplitter, Language

text_content = \"\"\"{text[:50]}...\"\"\" # Truncated for example

text_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.JS,
    chunk_size={chunk_size},
    chunk_overlap={chunk_overlap},
    keep_separator={keep_separator},
    add_start_index={add_start_index},
    strip_whitespace={strip_whitespace},
)
chunks = text_splitter.create_documents([text_content])
# Access chunks: chunks[0].page_content, chunks[0].metadata
"""
    return formatted_chunks, code_example

def chunk_markdown(text, chunk_size, chunk_overlap, keep_separator, add_start_index, strip_whitespace):
    if not text:
        return [], ""
    text_splitter = MarkdownTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        keep_separator=keep_separator,
        add_start_index=add_start_index,
        strip_whitespace=strip_whitespace,
    )
    chunks = text_splitter.create_documents([text])
    formatted_chunks = []
    for chunk in chunks:
        if isinstance(chunk, Document):
            formatted_chunks.append({"content": chunk.page_content, "metadata": chunk.metadata})
        else:
            formatted_chunks.append({"content": str(chunk), "metadata": {}})

    code_example = f"""
from langchain.text_splitter import MarkdownTextSplitter

text_content = \"\"\"{text[:50]}...\"\"\" # Truncated for example

text_splitter = MarkdownTextSplitter(
    chunk_size={chunk_size},
    chunk_overlap={chunk_overlap},
    length_function=len,
    keep_separator={keep_separator},
    add_start_index={add_start_index},
    strip_whitespace={strip_whitespace},
)
chunks = text_splitter.create_documents([text_content])
# Access chunks: chunks[0].page_content, chunks[0].metadata
"""
    return formatted_chunks, code_example

def main_interface(uploaded_file, chunk_size, chunk_overlap, separator, keep_separator, add_start_index, strip_whitespace):
    if uploaded_file is None:
        return "", "", [], [], [], [], [], "", "", "", "", "", "", "", "", "", "", ""

    # Ensure chunk_size and chunk_overlap are integers
    chunk_size = int(chunk_size)
    chunk_overlap = int(chunk_overlap)

    raw_text, display_content = process_uploaded_file(uploaded_file)

    recursive_chunks, recursive_code = chunk_recursive(raw_text, chunk_size, chunk_overlap, keep_separator, add_start_index, strip_whitespace)
    character_chunks, character_code = chunk_character(raw_text, chunk_size, chunk_overlap, separator, keep_separator, add_start_index, strip_whitespace)
    markdown_chunks, markdown_code = chunk_markdown(raw_text, chunk_size, chunk_overlap, keep_separator, add_start_index, strip_whitespace)
    python_chunks, python_code = chunk_python_code(raw_text, chunk_size, chunk_overlap, keep_separator, add_start_index, strip_whitespace)
    javascript_chunks, javascript_code = chunk_javascript_code(raw_text, chunk_size, chunk_overlap, keep_separator, add_start_index, strip_whitespace)

    return (
        display_content,
        raw_text,
        recursive_chunks,
        character_chunks,
        markdown_chunks,
        python_chunks,
        javascript_chunks,
        f"Number of chunks: {len(recursive_chunks)}",
        f"Number of chunks: {len(character_chunks)}",
        f"Number of chunks: {len(markdown_chunks)}",
        f"Number of chunks: {len(python_chunks)}",
        f"Number of chunks: {len(javascript_chunks)}",
        recursive_code,
        character_code,
        markdown_code,
        python_code,
        javascript_code
    )

# ---------------------------------------------  Gradio Interface  ----------------------------------------------------------#

with gr.Blocks(theme=gr.themes.Soft(), title="🦜️🔗 LangChain Text Chunker") as demo:
    gr.Markdown(
        """
        # 🦜️🔗 LangChain Text Chunker
        Welcome to the LangChain Text Chunker application! This tool allows you to upload various document types,
        extract their text content, and then apply different LangChain text splitting (chunking) methods.
        You can observe how each method breaks down the text into smaller, manageable chunks, along with their metadata.

        ### How to Use:
        1.  **Upload your document**: Select a file (PDF, DOCX, TXT, HTML, CSS, PY, IPYNB, CSV) using the file input.
        2.  **Adjust Chunking Parameters**: Use the sliders and dropdowns to customize `Chunk Size`, `Chunk Overlap`,
            `Character Splitter Separator`, `Keep Separator` behavior, `Add Start Index` to metadata, and `Strip Whitespace`.
        3.  **Process Document**: Click the "Process Document" button to see the extracted raw text and the results
            of various chunking methods in their respective tabs.
        4.  **Explore Chunks**: Each tab will display the chunks as JSON, along with the total number of chunks created.
        5.  **Python Example Code**: You can view dynamically generated Python 🐍 example code. 
        6.  **Inference**: This Gradio app is inferred from [Mervin Praison's work](https://mer.vin/2024/03/chunking-strategy/) about "Advanced Chunking Strategies".
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            file_input = gr.File(label="Upload your document", file_types=[".pdf", ".docx", ".txt", ".html", ".css", ".py", ".ipynb", ".csv"])
            process_button = gr.Button("Process Document", variant="primary")
            
            with gr.Accordion("Chunking Parameters", open=False):
                chunk_size_input = gr.Slider(minimum=100, maximum=2000, value=250, step=50, label="Chunk Size", info="Maximum size of chunks to return.")
                chunk_overlap_input = gr.Slider(minimum=0, maximum=500, value=0, step=10, label="Chunk Overlap", info="Overlap in characters between chunks.")
                separator_input = gr.Dropdown(
                    label="Character Splitter Separator",
                    choices=["\\n\\n", "\\n", " ", "", "\n", "." ,",", ";", ":", "!", "?", "-", 
                        "—", "(", ")", "[", "]", "{", "}", '"', "'", 
                        "“", "”", "‘", "’", "..."], # Representing common separators
                    value="\\n\\n",
                    allow_custom_value=True,
                    multiselect=True,
                    info="Characters to split on for Character Chunking. Multiple selections will be joined."
                )
                keep_separator_input = gr.Dropdown(
                    label="Keep Separator",
                    choices=[True, False, "start", "end"],
                    value=False,
                    info="Whether to keep the separator and where to place it in each corresponding chunk (True='start')."
                )
                add_start_index_input = gr.Checkbox(label="Add Start Index to Metadata", value=True, info="If checked, includes chunk’s start index in metadata.")
                strip_whitespace_input = gr.Checkbox(label="Strip Whitespace", value=True, info="If checked, strips whitespace from the start and end of every document.")
        
        with gr.Column(scale=2):
            raw_text_display = gr.Textbox(label="Extracted Raw Text", lines=10, interactive=False, show_copy_button=True)
            hidden_raw_text = gr.State("") # To store the actual raw text for chunking

    with gr.Tabs():
        with gr.TabItem("Recursive Chunking"):
            recursive_count_output = gr.Markdown()
            recursive_output = gr.JSON(label="Recursive Chunks")
            recursive_code_output = gr.Code(label="Python Code Example", language="python", interactive=False)
        with gr.TabItem("Character Chunking"):
            character_count_output = gr.Markdown()
            character_output = gr.JSON(label="Character Chunks")
            character_code_output = gr.Code(label="Python Code Example", language="python", interactive=False)
        with gr.TabItem("Markdown Chunking"):
            markdown_count_output = gr.Markdown()
            markdown_output = gr.JSON(label="Markdown Chunks")
            markdown_code_output = gr.Code(label="Python Code Example", language="python", interactive=False)
        with gr.TabItem("Python Code Chunking"):
            python_count_output = gr.Markdown()
            python_output = gr.JSON(label="Python Code Chunks")
            python_code_output = gr.Code(label="Python Code Example", language="python", interactive=False)
        with gr.TabItem("JavaScript Code Chunking"):
            javascript_count_output = gr.Markdown()
            javascript_output = gr.JSON(label="JavaScript Code Chunks")
            javascript_code_output = gr.Code(label="Python Code Example", language="python", interactive=False)

    process_button.click(
        fn=main_interface,
        inputs=[
            file_input,
            chunk_size_input,
            chunk_overlap_input,
            separator_input,
            keep_separator_input,
            add_start_index_input,
            strip_whitespace_input
        ],
        outputs=[
            raw_text_display,
            hidden_raw_text,
            recursive_output,
            character_output,
            markdown_output,
            python_output,
            javascript_output,
            recursive_count_output,
            character_count_output,
            markdown_count_output,
            python_count_output,
            javascript_count_output,
            recursive_code_output,
            character_code_output,
            markdown_code_output,
            python_code_output,
            javascript_code_output
        ]
    )

demo.launch()
