# qgis_mcp setup

Personal setup repo for connecting **QGIS** to **Claude** (via VS Code + GitHub Copilot) using the [Model Context Protocol](https://modelcontextprotocol.io/).

## Quick start

See **[SETUP.md](./SETUP.md)** for the full Windows walkthrough.

This repo intentionally contains almost no code — the actual QGIS plugin and MCP server come from [`nkarasiak/qgis-mcp`](https://github.com/nkarasiak/qgis-mcp). The only thing here that matters is `.vscode/mcp.json`, which tells VS Code Copilot how to launch Karasiak's MCP server via `uvx`.

## Why this layout?

- **Plugin** is installed via QGIS Plugin Manager (auto-updates)
- **MCP server** is fetched on demand by `uvx` from Karasiak's GitHub (always latest)
- **Workspace config** (`.vscode/mcp.json`) lives here so cloning the repo on a new laptop instantly wires everything up

## Credit

All the actual MCP work is by [Nicolas Karasiak](https://github.com/nkarasiak). This repo is just my personal setup glue.
