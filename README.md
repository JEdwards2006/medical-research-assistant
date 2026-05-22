# Medical Research Assistant

A local browser-based interface for searching PubMed and generating plain-English article summaries using Anthropic Claude.

## What this tool does

- Serves a simple web UI from `index.html`.
- Proxies PubMed (`NCBI E-utilities`) requests through `server.py` to avoid CORS issues.
- Loads PubMed search results and article abstracts in the browser.
- Sends a summary prompt to Anthropic Claude via the local proxy and displays the returned summary.
- Shows individual "Ask Claude about this article" links for each PubMed result, letting the user summarize one article at a time.
- Saves API settings locally in the browser so you don't need to re-enter keys after reloads.

## Files

- `index.html` - main front-end page and JavaScript logic.
- `server.py` - local HTTP proxy server for PubMed and Anthropic API calls.
- `START - Medical Research Assistant.bat` - Windows launcher script.
- `favicon.ico` - browser tab icon.
- `app.log` - optional rolling server log file created during runtime.

## Prerequisites

- Python 3 installed and available on `PATH`.
- Internet access.
- Valid NCBI API key and email address.
- Valid Anthropic API key.

## How to run

1. Open the folder in VS Code or File Explorer.
2. Double-click `START - Medical Research Assistant.bat`.
3. The script will launch your browser at `http://localhost:8000`.
4. Keep the terminal window open while using the app.

## How to use

1. Open the API settings panel by clicking `API settings`.
2. Enter your:
   - NCBI API key
   - Email address
   - Anthropic API key
   - Max results (1-20)
3. Click `Save settings`.
   - These values are stored in the browser using `localStorage`.
4. Enter a PubMed search query and click `Search`.

## What happens during a search

1. The app uses the NCBI `esearch.fcgi` endpoint to find PubMed IDs matching your query.
2. It then fetches the abstracts via `efetch.fcgi`.
3. Articles are displayed in the UI with title, authors, journal, year, and truncated abstract.
4. The top 5 articles are summarized by Claude using a shortened prompt.
5. A plain-English summary appears in the page.
6. Each article also includes a dedicated "Ask Claude about this article" link to summarize that article individually.

## Notes and behavior

- The summary is limited to the first 5 articles to avoid sending too much text to Anthropic.
- If more than 5 articles are retrieved, the UI displays a note explaining that the summary is based on the top 5 articles.
- Each search result also offers an individual article summary link that sends only that one article to Claude.
- API settings are saved in browser storage and restored on page load.
- The server proxy provides CORS support and forwards requests from the browser.
- The server maintains a rolling `app.log` file limited to 10,000 lines for debugging.

## Troubleshooting

- If the browser says it cannot reach PubMed, make sure `server.py` is still running.
- If Anthropic fails with a prompt length error, the app already truncates prompts and limits article count.
- If the server shows `502`, the local proxy has trouble forwarding the request. Check the terminal for detailed NCBI or Anthropic error output.
- If `python` is not found when running the batch file, install Python and add it to `PATH`.

## Security and privacy

- API keys are stored locally in the browser only.
- Do not commit or share your keys.
- Closing the browser or clearing browser data will remove saved settings.

## Development notes

- `server.py` acts as a proxy for both PubMed and Anthropic requests.
- `index.html` contains embedded styles and application logic for ease of local deployment.
- The app uses `fetch()` in the browser to call the local proxy endpoints.
