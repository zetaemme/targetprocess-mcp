# TargetProcess MCP

Model Context Protocol (MCP) server for integrating TargetProcess with Claude Code and other MCP clients.

## Features

- **Secure credential storage** - API tokens stored in macOS Keychain
- **VPN protection** - Optional requirement for VPN connection
- **Async API client** - Built on httpx for efficient HTTP requests
- **Type-safe models** - Dataclass models for TargetProcess entities
- **Self-configuring** - Configure directly from Claude Code

## Requirements

- Python 3.10+
- macOS (for Keychain integration)
- TargetProcess account with API access
- (Optional) VPN for secure access

## Quick Start

### 1. Install

```bash
# Clone and install
cd targetprocess-mcp
pip install -e .

# Or install dependencies directly
pip install fastmcp httpx
```

### 2. Add to Claude Code

```bash
# Using CLI (recommended)
claude mcp add targetprocess --transport stdio --scope user -- python -m targetprocess_mcp.server
```

Or manually add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "targetprocess": {
      "command": "python",
      "args": ["-m", "targetprocess_mcp.server"]
    }
  }
}
```

### 3. Configure

The first time you use a tool, you'll be prompted to configure. Or run the `configure` tool directly:

```
configure(url="https://yourcompany.tpondemand.com", token="your-api-token")
```

This stores:
- **URL**: `~/.config/targetprocess-mcp/config.toml`
- **Token**: macOS Keychain (encrypted)

## Available Tools

| Tool | Description |
|------|-------------|
| `configure` | Configure URL, token, and VPN settings |
| `get_status` | Check if MCP is configured and connected |
| `get_projects` | List all projects (id + name for reference) |
| `search` | Search user stories, bugs, or features by name |
| `get_user_stories` | Query user stories with filters |
| `get_bugs` | Query bugs with filters |
| `get_features` | Query features with filters |
| `get_sprints` | Query sprints/releases |

## Tool Details

### configure

Configure TargetProcess MCP with your credentials. Run this first to set up access.

```
configure(
    url: str,                    # TargetProcess URL
    token: str,                  # API token
    vpn_required: bool = false,  # Require VPN connection
    vpn_check_hosts: str = None  # Comma-separated hosts to check
)
```

Example:
```
configure(url="https://mycompany.tpondemand.com", token="abc123")
```

### get_status

Check if TargetProcess MCP is configured and connected.

### get_projects

Get all projects for quick reference. Use the returned IDs for filtering other queries.

```python
# Returns: [{"id": 1, "name": "My Project"}, ...]
get_projects(take: int = 100)
```

### search

Search entities by name across user stories, bugs, and features.

```python
search(
    query: str,              # Search term
    entity_type: str = None, # UserStory, Bug, Feature, or Task
    project_id: int = None, # Filter by project
    take: int = 20           # Max results
)
```

### get_user_stories

Query user stories with optional filters.

```python
get_user_stories(
    project_id: int = None,   # Filter by project
    feature_id: int = None,   # Filter by feature
    assignee_id: int = None, # Filter by assignee
    state: str = None,        # e.g., "Open", "In Progress", "Done"
    take: int = 100
)
```

### get_bugs

Query bugs with optional filters.

```python
get_bugs(
    project_id: int = None,   # Filter by project
    assignee_id: int = None, # Filter by assignee
    state: str = None,        # e.g., "Open", "Resolved", "Done"
    severity: str = None,    # e.g., "Critical", "Major", "Minor"
    take: int = 100
)
```

### get_features

Query features with optional filters.

```python
get_features(
    project_id: int = None, # Filter by project
    state: str = None,       # e.g., "Proposed", "In Progress"
    take: int = 100
)
```

### get_sprints

Query releases/sprints.

```python
get_sprints(
    project_id: int = None, # Filter by project
    take: int = 50
)
```

## Usage Examples

### Find all open bugs in a project

```
Get all open bugs in project 5
```

### Search for a user story

```
Search for user stories named "login"
```

### Get features for a project

```
Get all features for project 3
```

### Find sprints for a specific project

```
Show me the sprints for project "MyApp"
```

## Natural Language Prompts

Here are examples of how to interact with TargetProcess using natural language:

### Getting Started
```
Configure TargetProcess with my account (url)
Show me my TargetProcess status
```

### Projects & Search
```
What projects do I have access to?
Find projects named "Mobile"
Search for user stories about login
Find bugs tagged as critical
```

### User Stories
```
Show my open user stories
Get all user stories for project 5
List user stories assigned to me that are in progress
Show me user stories for feature 123
```

### Bugs
```
Show me all open bugs
What critical bugs exist in project 3?
List bugs assigned to me
Show bugs in QA state for review
```

### Features
```
What features are in progress?
Show completed features for project "Website Redesign"
```

### Sprints/Releases
```
What sprints are coming up?
Show me the current sprint for project 5
List all releases for project "Mobile App"
```

## Security

### Credential Storage

- **API Token**: Stored in macOS Keychain (encrypted by OS)
- **URL & Settings**: Stored in `~/.config/targetprocess-mcp/config.toml`

### VPN Protection (Optional)

Configure VPN protection when running `configure`:

```
vpn_required: true
vpn_check_hosts: internal-api.company.com
```

When enabled, the MCP will check connectivity to the specified host(s) before making any API calls.

## Configuration

### Re-configure

Run the `configure` tool anytime to update your settings:

```
configure(url="https://yourcompany.tpondemand.com", token="new-token")
configure(url="https://yourcompany.tpondemand.com", token="token", vpn_required=true, vpn_check_hosts="host1,host2")
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `TARGETPROCESS_URL` | Override TargetProcess URL |
| `TARGETPROCESS_TOKEN` | Override API token (not recommended) |
| `TARGETPROCESS_VPN_REQUIRED` | Set to "true" to require VPN |

### Manual Configuration

The configuration file is stored at:

```
~/.config/targetprocess-mcp/config.toml
```

Example:
```toml
URL = "https://yourcompany.tpondemand.com"

VPN_REQUIRED = true
VPN_CHECK_HOSTS = ["internal-api.company.com"]
```

## Troubleshooting

### "TargetProcess not configured" error

Run the configure tool:
```
configure(url="https://yourcompany.tpondemand.com", token="your-api-token")
```

### "VPN connection required" error

Ensure you're connected to your VPN. If you configured VPN protection, the MCP will not work outside your network.

### Claude Code not recognizing the MCP

Try restarting Claude Code or running:
```bash
claude mcp list
```

To verify the server is registered.

### macOS Keychain issues

If you encounter Keychain errors, you can manually manage the token:

```bash
# Add token
security add-generic-password -s targetprocess-mcp -a api-token -w YOUR_TOKEN

# Delete token
security delete-generic-password -s targetprocess-mcp -a api-token
```

## Development

### Project Structure

```
targetprocess_mcp/
├── __init__.py          # Package metadata
├── config.py            # Configuration & Keychain
├── client.py            # TargetProcess API client
├── server.py            # FastMCP server & tools
├── models/              # Dataclass models
│   ├── __init__.py
│   ├── project.py
│   ├── user_story.py
│   └── ...
├── pyproject.toml       # Package configuration
└── .pre-commit-config.yaml
```

### Running Tests

```bash
pip install -e ".[dev]"

# Run with environment variables
TARGETPROCESS_URL="https://test.tpondemand.com" TARGETPROCESS_TOKEN="test-token" pytest tests/
```

### Code Quality

```bash
# Run ruff linter
ruff check targetprocess_mcp/

# Run mypy type checker
mypy targetprocess_mcp/
```

### Pre-commit Hook

Install the pre-commit hook to run type checks and tests before each commit:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually anytime
pre-commit run --all-files
```

The hook runs:
1. `ruff` - Linting and formatting
2. `mypy` - Type checking
3. `pytest` - Tests

Commit is blocked if any check fails.

## License

MIT
