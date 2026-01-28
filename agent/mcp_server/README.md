# PV Curve Agent MCP Server (Claude Desktop)

**Use Claude Desktop to control the PV Curve Agent via MCP tools (classification, routing, parameter edits, PV curve generation, and multi-step planning).**

## Table of Contents

- [Overview](#overview)
- [Tools Available in Claude](#tools-available-in-claude)
- [Prerequisites](#prerequisites)
- [Step-by-Step Setup (After Cloning)](#step-by-step-setup-after-cloning)
- [Claude Desktop Configuration (MCP)](#claude-desktop-configuration-mcp)
- [Verify It Works](#verify-it-works)
- [Troubleshooting](#troubleshooting)

## Overview

This repo includes an MCP server built with **FastMCP** that exposes PV Curve Agent capabilities as Claude tools.

**Entry points:**
- `mcp_server.py` (repo root): runs the MCP server
- `python -m agent.mcp_server` (module entry point): runs the MCP server

## Tools Available in Claude

These are the MCP tools that should appear in Claude Desktop after setup:

- `get_session_id`
- `classify_message`, `route_request`
- `question_general`, `question_parameter`
- `modify_parameters`
- `generate_pv_curve`
- `plan_steps`, `step_controller`, `advance_step`
- `handle_error`, `summarize_results`

Note: an `analyze_pv_curve` helper exists in code, but it is **not currently registered as an MCP tool**, so it will not appear in Claude Desktop.

## Prerequisites

- **Claude Desktop**: required (this setup uses Claude Desktop)
- **Python**: 3.12 or higher
- **Git**
- **Ollama**: required for the default local model setup ([Download](https://ollama.com/download))

## Step-by-Step Setup (After Cloning)

1. **Download and install Claude Desktop**
   - Install Claude Desktop for your OS, then open it once (so it creates its config folder).
   - Download: [Claude Desktop](https://claude.com/download)

2. **Clone the repository**

```bash
git clone https://github.com/CURENT/pv-curve-llm.git
cd pv-curve-llm
```

3. **Create a virtual environment**

macOS / Linux:

```bash
python3.12 -m venv venv
source venv/bin/activate
python --version
```

Windows (PowerShell):

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python --version
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Set up Ollama models** (default MCP server uses Ollama)

```bash
ollama pull mxbai-embed-large  # Embedding model for RAG
ollama pull llama3.1:8b
ollama create pv-curve -f agent/Modelfile
```

## Claude Desktop Configuration (MCP)

Claude Desktop needs an MCP config entry that starts this server using the **venv python** (recommended).

### 1) Find / edit Claude Desktop config

Common locations:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`

Or from Claude Desktop:
- **Settings → Developer → Edit Config**

### 2) Add the MCP server entry

Example config (edit paths to match your machine):

```json
{
  "mcpServers": {
    "pv-curve-agent": {
      "command": "/ABSOLUTE/PATH/TO/pv-curve-llm/venv/bin/python3.12",
      "args": ["/ABSOLUTE/PATH/TO/pv-curve-llm/mcp_server.py"],
    }
  }
}
```

Windows example (paths will differ):

```json
{
  "mcpServers": {
    "pv-curve-agent": {
      "command": "C:\\ABSOLUTE\\PATH\\TO\\pv-curve-llm\\venv\\Scripts\\python.exe",
      "args": ["C:\\ABSOLUTE\\PATH\\TO\\pv-curve-llm\\mcp_server.py"],
    }
  }
}
```

### 3) Restart Claude Desktop

Close Claude Desktop completely and reopen it. The tool list should now include the PV Curve MCP tools.

## Verify It Works

In Claude Desktop:

1. Enable the server in **Connectors** (`+` → Connectors). You should see `pv-curve-agent`.
2. Call `get_session_id()` once and copy the returned `session_id`.
3. Run this basic flow:
   - `classify_message(user_message="What is a PV curve?", session_id="...")`
   - `route_request(session_id="...")`
   - Call the tool in `next_tool` (for example, `question_general(...)`)

4. Try a basic workflow:
   - “Set grid to ieee39 and bus to 10”
   - “Generate PV curve”
   - “Summarize the results”

## Troubleshooting

### Claude can’t start the server

- **Symptom**: Claude shows the server as disconnected or tools don’t appear.
- **Fix**: Make sure `command` points to your **venv python**, not the system python.
- **Fix**: Confirm you can import required dependencies using the venv python.

```bash
/ABSOLUTE/PATH/TO/pv-curve-llm/venv/bin/python -c "import fastmcp; import langchain_core"
```

### Ollama errors / model not found

- **Symptom**: server runs but tool calls fail when the LLM is invoked.
- **Fix**: confirm Ollama is running and the model exists:

```bash
ollama list
ollama run pv-curve
```

### No PV curve image / plotting issues

- This project uses a non-interactive matplotlib backend and writes plots to files.
- If Claude can’t open the image, use the returned `image_file_url` (a `file://...` URL) and open it locally.

