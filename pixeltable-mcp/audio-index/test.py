import pixeltable as pxt
from pixeltable.functions import whisper
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.iterators.string import StringSplitter
from pixeltable.iterators import AudioSplitter

DIRECTORY = 'audio_index'
TABLE_NAME = f'{DIRECTORY}.audio'
CHUNKS_VIEW_NAME = f'{DIRECTORY}.audio_chunks'
SENTENCES_VIEW_NAME = f'{DIRECTORY}.audio_sentence_chunks'
DELETE_INDEX = True

# python -m spacy download en_core_web_sm (run this separately if needed)

if DELETE_INDEX and TABLE_NAME in pxt.list_tables():
    pxt.drop_table(TABLE_NAME, force=True)

if TABLE_NAME not in pxt.list_tables():
    # Create audio table
    pxt.create_dir(DIRECTORY, if_exists='ignore')
    audio_index = pxt.create_table(TABLE_NAME, {'audio_file': pxt.Audio})

    # Create view for audio chunks
    chunks_view = pxt.create_view(
        CHUNKS_VIEW_NAME,
        audio_index,
        iterator=AudioSplitter.create(
            audio=audio_index.audio_file,
            chunk_duration_sec=30.0,  # Split into 30-second chunks
            overlap_sec=2.0,          # 2-second overlap between chunks
            min_chunk_duration_sec=5.0  # Drop last chunk if < 5 seconds
        )
    )

    # Create audio-to-text column on chunks
    chunks_view.add_computed_column(
        transcription=whisper.transcribe(audio=chunks_view.audio_chunk, model='base.en')
    )

    # Create view that chunks text into sentences
    sentences_view = pxt.create_view(
        SENTENCES_VIEW_NAME,
        chunks_view,
        iterator=StringSplitter.create(text=chunks_view.transcription.text, separators='sentence'),
    )

    # Define the embedding model
    embed_model = sentence_transformer.using(model_id='intfloat/e5-large-v2')

    # Create embedding index
    sentences_view.add_embedding_index(column='text', string_embed=embed_model)
else:
    audio_index = pxt.get_table(TABLE_NAME)
    chunks_view = pxt.get_view(CHUNKS_VIEW_NAME)
    sentences_view = pxt.get_view(SENTENCES_VIEW_NAME)

# Add data to the table
audio_index.insert([{'audio_file': 's3://pixeltable-public/audio/10-minute tour of Pixeltable.mp3'}])

# Semantic search
query_text = 'What is Pixeltable?'

# Calculate similarity scores between query and sentences
sim = sentences_view.text.similarity(query_text)

# Get top 5 most similar sentences with their scores
results = sentences_view.order_by(sim, asc=False).select(sentences_view.text, sim=sim).limit(5).collect()
print(results['text'])