# LaTeX-OCR

This project leverages Llama 3.2 vision and Streamlit to create a LaTeX OCR app that converts images of LaTeX equations to LaTeX code.

## Demo Video

Click below to watch the demo video of the AI Assistant in action:

[Watch the video](LaTeX-OCR.mp4)

## Installation and setup

**Setup Ollama**:

   *On Linux*:
   ```bash 
   curl -fsSL https://ollama.com/install.sh | sh
   # pull llama 3.2 vision model
   ollama run llama3.2-vision 
   ```

   *On MacOS*:
   ```bash 
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"    # get homebrew
   xcode-select --install
   brew install ollama    # install ollama
   ollama pull llama3.2-vision    # pull llama 3.2 vision model
   ollama run llama3.2-vision 
   ```


**Install Dependencies**:
   Ensure you have Python 3.11 or later installed.
   ```bash
   pip install streamlit ollama
   ```

---

## 📬 Stay Updated with Our Newsletter!
**Get a FREE Data Science eBook** 📖 with 150+ essential lessons in Data Science when you subscribe to our newsletter! Stay in the loop with the latest tutorials, insights, and exclusive resources. [Subscribe now!](https://join.dailydoseofds.com)

[![Daily Dose of Data Science Newsletter](https://github.com/patchy631/ai-engineering/blob/main/resources/join_ddods.png)](https://join.dailydoseofds.com)

---

## Contribution

Contributions are welcome! Please fork the repository and submit a pull request with your improvements.
