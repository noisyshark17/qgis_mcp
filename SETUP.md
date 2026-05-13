# QGIS MCP Setup (Windows + VS Code Copilot)

This project uses [Nicolas Karasiak's qgis-mcp](https://github.com/nkarasiak/qgis-mcp) for both the QGIS plugin and the MCP server. The MCP server is fetched on demand via `uvx` — no local clone of the server is required.

## Prerequisites

- **QGIS** 3.28 or newer — https://qgis.org/download/
- **VS Code** with **GitHub Copilot** + **GitHub Copilot Chat** extensions — https://code.visualstudio.com/
- **Git** — `winget install --id Git.Git -e --source winget`
- **uv** package manager — `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

## One-time setup on a new laptop

### 1. Clone this repo

```powershell
mkdir C:\Github -Force
cd C:\Github
git clone https://github.com/noisyshark17/qgis_mcp.git
cd qgis_mcp
```

> Avoid cloning into OneDrive — Git and OneDrive don't play nicely together.

### 2. Install the QGIS MCP plugin (Karasiak's)

1. Open QGIS
2. **Plugins → Manage and Install Plugins → All** tab
3. Search for **QGIS MCP**
4. Install the entry by **Nicolas Karasiak**
5. Switch to the **Installed** tab and ensure the box is checked

### 3. Open this folder in VS Code

```powershell
code C:\Github\qgis_mcp
```

VS Code will detect `.vscode/mcp.json` and offer to start the `qgis` MCP server.

The first time it starts, `uvx` downloads Karasiak's MCP server from GitHub (~10–30 seconds). Subsequent launches are instant.

### 4. Start the QGIS server

1. In QGIS, click the **QGIS MCP** toolbar button (or open the dock from `Plugins → QGIS MCP`)
2. Confirm the port is **9876** and click **Start Server**

### 5. Use it from Copilot Chat

1. Open Copilot Chat in VS Code
2. Switch the chat mode dropdown to **Agent**
3. Pick a Claude model
4. Try: *"Run the diagnose tool against QGIS"*

You should see all 51 tools available, including `diagnose`, `get_field_statistics`, `set_layer_style`, `list_processing_algorithms`, etc.

## Updating Karasiak's server

Because `uvx` fetches from `git+https://github.com/nkarasiak/qgis-mcp` on each launch, you get the latest version automatically. To force a refresh of the cached install:

```powershell
uv cache clean
```

## Troubleshooting

- **"Tool diagnose not found"** — VS Code is still running the old MCP server. Fully quit VS Code (check system tray) and reopen.
- **"Connection refused on localhost:9876"** — The QGIS plugin isn't running. Open QGIS and click Start Server.
- **Wrong plugin loaded** — Delete `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\qgis_mcp_plugin` and reinstall via QGIS Plugin Manager.

## Architecture

```
VS Code Copilot ←→ MCP Server (uvx, Karasiak) ←→ TCP socket :9876 ←→ QGIS Plugin (Karasiak) ←→ PyQGIS
```
