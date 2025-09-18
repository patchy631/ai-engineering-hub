# Multilingual Meeting Notes Generator

We're building a multilingual meeting notes generator that automatically detects the language spoken in meetings and provides comprehensive English summaries with speaker-level analysis and action item extraction.

## How It Works

1. **Audio Input**: User uploads meeting audio file
2. **Language Detection**: AssemblyAI automatically detects the spoken language (supports 99 languages)
3. **Transcription**: High-quality transcription with speaker diarization(supports 95 languages) to identify individual speakers
4. **Processing**: AI-powered summarization and action item extraction using any multilingual LLM
5. **Results**: Comprehensive meeting notes including English summary, speaker analysis, and action items

We use:

- [AssemblyAI Universal](https://www.assemblyai.com/blog/99-languages) for language detection and transcription
- Any multilingual LLM of your choice
- [Streamlit](https://streamlit.io/) for the user interface

## Set Up

Follow these steps one by one:

### Create .env File

Create a `.env` file in the root directory of your project with the following content:

```env
ASSEMBLYAI_API_KEY=<your_assemblyai_api_key>
```

### Install Dependencies

```bash
uv sync
```

This command will install all the required dependencies for the project using uv.

## Run the Application

To run the meeting notes generator, execute the following command:

```bash
uv run streamlit run app.py
```

Running this command will start the Streamlit application, which will handle the complete workflow from audio processing to meeting notes generation.

## Usage

1. **Upload Audio**: Upload an audio file (MP3, WAV, M4A, MP4) 
2. **Generate Notes**: Click "Start Processing" to process audio 
4. **View Results**: Review the comprehensive meeting analysis including:
   - English summary
   - Speaker-wise contributions
   - Action items and tasks
   - Full transcript
5. **Download Reports**: Export summaries, action items, and transcripts as text files

## Supported Languages

The application supports 99 languages including English, Spanish, French, German, Italian, Portuguese, Russian, Japanese, Korean, Chinese, Arabic, Hindi, and many more.

## 📬 Stay Updated with Our Newsletter!

**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

## Contribution

Contributions are welcome! Feel free to fork this repository and submit pull requests with your improvements.