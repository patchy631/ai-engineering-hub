import pixeltable as pxt
import os
from pixeltable.functions.openai import vision
from pixeltable.functions.huggingface import sentence_transformer

# Set OpenAI API key (replace with your actual key or use an environment variable)
os.environ['OPENAI_API_KEY'] = 'your-openai-api-key-here'

# Base directory for the index
DIRECTORY = 'image_search'
TABLE_NAME = f'{DIRECTORY}.images'
RECREATE = True

# Recreate the directory if specified
if RECREATE:
    pxt.drop_dir(DIRECTORY, force=True)

# Check if table exists, create it if not
if TABLE_NAME not in pxt.list_tables():
    # Create directory and table
    pxt.create_dir(DIRECTORY, if_exists='ignore')
    image_index = pxt.create_table(
        TABLE_NAME,
        {'image_file': pxt.Image},
        if_exists='ignore'
    )

    # Add GPT-4 Vision analysis
    image_index.add_computed_column(
        image_description=vision(
            prompt="Describe the image. Be specific on the colors you see.",
            image=image_index.image_file,
            model="gpt-4o-mini"
        )
    )

    # Define the embedding model and create embedding index
    embed_model = sentence_transformer.using(model_id='intfloat/e5-large-v2')
    image_index.add_embedding_index(
        column='image_description',
        string_embed=embed_model,
        if_exists='ignore'
    )
else:
    image_index = pxt.get_table(TABLE_NAME)

# Sample image URLs
IMAGE_URL = (
    "https://raw.github.com/pixeltable/pixeltable/release/docs/resources/images/"
)
image_urls = [
    IMAGE_URL + doc for doc in [
        "000000000030.jpg",
        "000000000034.jpg",
        "000000000042.jpg",
    ]
]

# Insert images into the table
image_index.insert({'image_file': url} for url in image_urls)

# Perform a sample query
query_text = "Show me images containing blue flowers"
sim = image_index.image_description.similarity(query_text)
results = (
    image_index.order_by(sim, asc=False)
    .select(image_index.image_file, image_index.image_description, sim=sim)
    .limit(3)
    .collect()
)

# Print results
print(f"Query Results for '{query_text}' in '{TABLE_NAME}':\n")
for i, row in enumerate(results.to_pandas().itertuples(), 1):
    print(f"{i}. Score: {row.sim:.4f}")
    print(f"   Description: {row.image_description}")
    print(f"   Image URL: {row.image_file}\n")