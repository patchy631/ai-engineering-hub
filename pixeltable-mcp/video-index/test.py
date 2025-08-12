from datetime import datetime
import pixeltable as pxt
from pixeltable.functions import openai
from pixeltable.functions.huggingface import sentence_transformer
from pixeltable.functions.video import extract_audio
from pixeltable.iterators import AudioSplitter, FrameIterator
from pixeltable.iterators.string import StringSplitter
from pixeltable.functions.openai import vision

EMBED_MODEL = sentence_transformer.using(model_id='intfloat/e5-large-v2')

# Set to True to delete existing index
directory = 'video_index'
table_name = f'{directory}.video'

# Create video table
pxt.create_dir(directory, if_exists='replace_force')
video_index = pxt.create_table(table_name, {'video': pxt.Video, 'uploaded_at': pxt.Timestamp})
video_index.add_computed_column(audio_extract=extract_audio(video_index.video, format='mp3')) 

# Create view for frames
frames_view = pxt.create_view(
    f'{directory}.video_frames',
    video_index,
    iterator=FrameIterator.create(
        video=video_index.video,
        fps=1
    )
)

frames_view.add_computed_column(
    image_description=vision(
        prompt="Provide quick caption for the image.",
        image=frames_view.frame,
        model="gpt-4o-mini"
    )
)    

frames_view.add_embedding_index('image_description', string_embed=EMBED_MODEL)    

# Create view for audio chunks
chunks_view = pxt.create_view(
    f'{directory}.video_chunks',
    video_index,
    iterator=AudioSplitter.create(
        audio=video_index.audio_extract,
        chunk_duration_sec=30.0,
        overlap_sec=2.0,
        min_chunk_duration_sec=5.0
    )
)

# Audio-to-text for chunks
chunks_view.add_computed_column(
    transcription=openai.transcriptions(audio=chunks_view.audio_chunk, model='whisper-1')
)

# Create view that chunks text into sentences
transcription_chunks = pxt.create_view(
    f'{directory}.video_sentence_chunks',
    chunks_view,
    iterator=StringSplitter.create(text=chunks_view.transcription.text, separators='sentence'),
)

# Create embedding index
transcription_chunks.add_embedding_index('text', string_embed=EMBED_MODEL)

# Insert Videos
videos = [
    'https://github.com/pixeltable/pixeltable/raw/release/docs/resources/audio-transcription-demo/'
    f'Lex-Fridman-Podcast-430-Excerpt-{n}.mp4'
    for n in range(3)
]

video_index.insert({'video': video, 'uploaded_at': datetime.now()} for video in videos[:2])

# Get similarity scores
audio_sim = transcription_chunks.text.similarity('What is happiness?')
image_sim = frames_view.image_description.similarity('Black Suit')

# Fetch 5 most similar audio chunks
audio_results = (
    transcription_chunks.order_by(audio_sim, transcription_chunks.uploaded_at, asc=False)
    .limit(5)
    .select(transcription_chunks.text, transcription_chunks.uploaded_at, similarity=audio_sim)
    .collect()
)

# Fetch 5 most similar frames
frame_results = (
    frames_view.order_by(image_sim, frames_view.uploaded_at, asc=False)
    .limit(5)
    .select(frames_view.image_description, frames_view.uploaded_at, similarity=image_sim)
    .collect()
)

print(audio_results)
print(frame_results)