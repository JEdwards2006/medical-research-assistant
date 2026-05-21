# Medical Research Assistant - Setup Instructions

## Prerequisites

Before using this tool, you'll need:

1. **Python 3.x** - Download from [python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"

2. **NCBI Account & API Key**
   - Go to [NCBI Account Settings](https://www.ncbi.nlm.nih.gov/account/settings/)
   - Create an API key
   - You'll also need the email associated with your NCBI account

3. **Anthropic API Key**
   - Go to [Anthropic Console](https://console.anthropic.com/)
   - Create an API key

## Local Setup

1. Clone or download this repository
2. Navigate to the `pubmed_tool` folder
3. Run `START - Medical Research Assistant.bat` (Windows)
   - Or run `python server.py` directly from terminal

## API Keys

- API keys are stored **locally in your browser** using localStorage
- They are NOT sent to any external service except NCBI and Anthropic
- To reset keys, open browser dev tools → Application → Local Storage and delete the entry

## First Run

1. Start the server using the batch file or Python
2. Open browser to `http://localhost:8000`
3. Click "API settings"
4. Enter your NCBI API key, email, and Anthropic API key
5. Click "Save settings"
6. Perform your first search

See [README.md](README.md) for full feature documentation.
