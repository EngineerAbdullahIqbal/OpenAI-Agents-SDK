# Simple-Bot

## Overview
**Simple-Bot** is an interactive AI chatbot built using [Chainlit](https://chainlit.io/) and [OpenAI SDK](https://platform.openai.com/docs/guides/tools?api-mode=chat). This lightweight bot leverages OpenAI's powerful language models to provide dynamic and intelligent conversations with users.

## Features
- **Natural Language Processing**: Utilizes OpenAI's GPT models to generate human-like responses.
- **Chainlit Integration**: Provides a seamless and interactive Conversational AI UI.

## Installation

### Prerequisites
Ensure you have the following installed:
- Python 3.8+
- Pip (Python package manager)
- GEMINI API Key

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/simple-bot.git
   cd simple-bot
   ```
2. **Install Dependencies**:
   ```bash
   uv add openai-agents chainlit
   ```
3. **Set Up Environment Variables**:
   Create a `.env` file and add your GEMINI API key:
   ```env
   GEMINI_API_KEY=your_openai_api_key
   ```
4. **Run the Bot**:
   ```bash
   chainlit run main.py
   ```

## Usage
- Launch the chatbot and start interacting with it via the Chainlit interface.
- Modify `main.py` to customize the bot's behavior.

## File Structure
```
/simple-bot
│── main.py            # Core chatbot logic
│── pyproject.toml   # Dependencies
│── .env               # API key storage
│── README.md          # Project documentation
```

## Customization
You can modify `main.py` to:
- Change the prompt behavior
- Use different GEMINI models
- Add additional processing logic

## License
This project is licensed under the MIT License.

## Author
[Your Name](https://github.com/EngineerAbdullahIqbal)

## Contributions
Feel free to open issues or submit pull requests to enhance the bot!

---

Enjoy building with AI! 🚀

