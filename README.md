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

   - For local execution: Create a `.env` file with your Webhook URL:
     ```
     WEBHOOK_URL="your-webhook-url"
     ```
   - For GitHub Actions: Add the Webhook URL as a Repository Secret:
     1. Go to your repository on GitHub
     2. Navigate to "Settings" → "Secrets and variables" → "Actions"
     3. Click "New repository secret"
     4. Name: `WEBHOOK_URL`, Value: your webhook URL
     5. Click "Add secret"

3. **Edit Configuration File**
   - Open `config.yaml` to review and customize filtering settings

### Execution

```bash
# Run the script
python main.py
```
