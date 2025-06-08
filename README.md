# Outline

This project automatically retrieves the latest AI-related papers from the ArXiv API and sends notifications to Slack with information such as citation counts and publication dates.

## Key Features

- **Automated Paper Collection**: Retrieves the latest AI-related papers from ArXiv API
- **Citation Display**: Shows citation counts using the Semantic Scholar API
- **Smart Filtering**: Filters papers based on keywords, citation counts, and publication dates
- **Scheduled Notifications**: Automatic daily execution via GitHub Actions
- **Customizable**: Flexible settings for search categories, filter conditions, etc.

## Getting Started

### Installation

```bash
# Install uv if not already installed
brew install uv
# Or using pip
pip install uv

# Setup virtual environment and install dependencies in one go
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Configuration

1. **Obtain Slack Webhook URL**

   - Create a new app in your Slack workspace
   - Enable "Incoming Webhooks"
   - Get the Webhook URL

2. **Store Secrets Securely**

   - For local execution: Create a `.env` file with your credentials:
     ```
     SLACK_WEBHOOKS="your-slack-webhook-url"
     GEMINI_API_KEY="your-gemini-api-key"        # Optional: needed for Gemini
     OPENAI_API_KEY="your-openai-api-key"        # Optional: needed for ChatGPT
     ```
   - For GitHub Actions: Add the secrets to your Repository:
     1. Go to your repository on GitHub
     2. Navigate to "Settings" → "Secrets and variables" → "Actions"
     3. Click "New repository secret"
     4. Add the following secrets:
        - `SLACK_WEBHOOKS`: Your Slack webhook URL
        - `GEMINI_API_KEY`: Your Google Gemini API key (optional)
        - `OPENAI_API_KEY`: Your OpenAI API key (optional)
     5. Click "Add secret" for each

3. **Edit Configuration File**
   - Open `config.yaml` to review and customize filtering settings
   - Choose your LLM provider by setting `llm.provider` to one of:
     - `gemini`: Use Google's Gemini for paper summarization
     - `chatgpt`: Use OpenAI's ChatGPT for paper summarization
     - `none`: Don't use any AI summarization

### Execution

```bash
# Run the script
python main.py
```
