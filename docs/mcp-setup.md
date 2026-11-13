# Setting up the MCP server (Windows)

The MCP server lets Claude Desktop read Propfein's picks and record through the Propfein API.

## 1. Install

In PowerShell, from the repo folder with the virtual environment active:

```powershell
pip install -r requirements.txt
```

## 2. Settings

Open `.env` and add two lines (see `.env.example`):

```
PROPFEIN_API_URL=https://<project-ref>.supabase.co/functions/v1/propfein-api
PROPFEIN_API_KEY=<your key>
```

To try it before you have a key, use `PROPFEIN_API_URL=mock`. That serves invented sample data.

Never commit `.env`, and never paste the key anywhere else.

## 3. Check it starts

```powershell
python -m propfein_mcp
```

Nothing prints and it waits: that is correct (it is listening for a client). Press Ctrl+C to stop. An error about `PROPFEIN_API_URL` means step 2 is not done.

## 4. Connect Claude Desktop

Open `%AppData%\Claude\claude_desktop_config.json` (create it if it is missing) and add the server. Use the full paths to this repo on your machine:

```json
{
  "mcpServers": {
    "propfein": {
      "command": "C:\\path\\to\\propfein-ai\\.venv\\Scripts\\python.exe",
      "args": ["-m", "propfein_mcp"],
      "env": { "PYTHONPATH": "C:\\path\\to\\propfein-ai" }
    }
  }
}
```

Quit Claude Desktop fully (from the system tray) and open it again. The Propfein tools appear in the tools menu.

## 5. Test question

> How did NBA overs priced between -150 and -200 do in the last 30 days? Count per bet.

Claude should call `get_record` and quote its numbers. If a number in the answer is not in the tool result, that is a faithfulness failure worth logging.
