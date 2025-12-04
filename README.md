# MinerU Tianshu Plugin for Dify

> Enterprise-level multi-GPU document parsing service powered by MinerU

[![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/your-username/mineru-tianshu-plugin)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](LICENSE)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-orange.svg)](https://dify.ai)

## Overview

MinerU Tianshu is a powerful Dify plugin that enables high-quality document parsing capabilities through MinerU's enterprise-level infrastructure. Convert PDFs, images, and Office documents into structured Markdown format with support for:

- 📄 **Multi-format Support**: PDF, images (PNG, JPG), Office files (Word, Excel, PowerPoint)
- 🔢 **Formula Recognition**: Extract mathematical formulas in LaTeX format
- 📊 **Table Extraction**: Preserve table structure and formatting
- 🌍 **Multi-language**: Chinese, English, Korean, Japanese, and more
- ⚡ **Multi-GPU Acceleration**: Leverage GPU infrastructure for fast processing
- 🎯 **Multiple Backends**: Choose from pipeline, VLM-transformers, or VLM-vLLM engine

## Features

This plugin provides **3 tools** for flexible document processing workflows:

### 1. Parse Document (Synchronous)
**`parse_document`** - One-click document parsing with automatic wait

- Submit document and wait for completion
- Returns parsed Markdown content directly
- Ideal for interactive workflows
- Configurable timeout (default: 300 seconds)

### 2. Parse Document Async (Asynchronous)
**`parse_document_async`** - Submit and continue workflow

- Submit document for background processing
- Returns task ID immediately
- Useful for large documents or batch processing
- Support priority queue

### 3. Get Parse Result
**`get_parse_result`** - Retrieve results later

- Check task status (pending/processing/completed/failed)
- Retrieve parsed Markdown when ready
- Works with task IDs from async submissions

## Installation

### Prerequisites

- Dify instance (self-hosted or cloud)
- MinerU Tianshu API Server (required)
- Python 3.11+ (for plugin runtime)

### ⚠️ Important: Dify Server Configuration

**For self-hosted Dify instances**, you MUST configure the `FILES_URL` environment variable in your Dify server's `.env` file:

```bash
# Add this to your Dify server's .env file
FILES_URL=http://your-dify-server:port
# Example: FILES_URL=http://localhost:3000
# Example: FILES_URL=https://your-dify-domain.com
```

This allows the plugin to download files from your Dify instance. Without this configuration, you'll see errors like:
```
Error: Invalid file URL '/files/...': Request URL is missing an 'http://' or 'https://' protocol
```

**Note**: Dify Cloud users don't need this configuration as it's already set up.

### Quick Start

1. **Install the plugin** in your Dify instance:
   - Navigate to Tools & Plugins
   - Search for "MinerU Tianshu"
   - Click Install

2. **Configure API Server**:
   - Go to plugin settings
   - Enter your MinerU Tianshu API Server URL
   - Example: `http://localhost:8100`

3. **Start using** in your workflows or agents!

## Usage Examples

### Example 1: Synchronous Parsing in Workflow

```yaml
Tool: parse_document
Inputs:
  - file: {{uploaded_document}}
  - backend: pipeline
  - lang: ch
  - formula_enable: true
  - table_enable: true
  - max_wait_time: 300

Output:
  {{markdown_content}}
```

### Example 2: Asynchronous Processing

**Step 1: Submit Document**
```yaml
Tool: parse_document_async
Inputs:
  - file: {{document}}
  - priority: 5

Output:
  {{task_id}}
```

**Step 2: Retrieve Result Later**
```yaml
Tool: get_parse_result
Inputs:
  - task_id: {{task_id}}

Output:
  {{markdown_content}}
```

### Example 3: Agent with Document Analysis

Create an agent that:
1. Uses `parse_document` to convert PDF to Markdown
2. Analyzes the content with LLM
3. Extracts key information

## Configuration

### API Server URL
- **Required**: Yes
- **Format**: `http://your-server:port`
- **Example**: `http://localhost:8100`

### Tool Parameters

#### Backend Options
- `pipeline` (Recommended): Balanced performance and accuracy
- `vlm-transformers`: Vision-language model with Transformers
- `vlm-vllm-engine`: Optimized VLM engine for large-scale processing

#### Language Support
- `ch`: Chinese (Simplified)
- `en`: English
- `korean`: Korean
- `japan`: Japanese

#### Processing Options
- **Formula Recognition**: Extract mathematical formulas
- **Table Recognition**: Preserve table structure
- **Priority**: Queue priority (0-100, higher = faster)

## API Server Setup

If you don't have a MinerU Tianshu server, you can deploy one:

### Using Docker

```bash
docker run -d \
  --name mineru-tianshu \
  --gpus all \
  -p 8100:8000 \
  -e API_PORT=8000 \
  your-registry/mineru-tianshu:latest
```

### From Source

```bash
cd MinerU/projects/mineru_tianshu
pip install -r requirements.txt
python api_server.py
```

See the [MinerU Tianshu Documentation](https://github.com/opendatalab/MinerU) for more details.

## Troubleshooting

### Connection Errors

**Error**: "API Server URL is not configured"
- **Solution**: Configure the API Server URL in plugin settings

**Error**: "Network error: Connection refused"
- **Solution**: Check if the MinerU Tianshu server is running and accessible

### Timeout Issues

**Error**: "Timeout: Processing exceeded 300 seconds"
- **Solution**:
  - Increase `max_wait_time` parameter
  - Use `parse_document_async` + `get_parse_result` for large documents
  - Check server GPU availability

### Result Not Found

**Warning**: "Task completed but no content found"
- **Cause**: Result files cleaned up (retention period expired)
- **Solution**: Configure longer retention period on server

## Performance Tips

1. **Choose the right backend**:
   - `pipeline`: Best for general documents
   - `vlm-vllm-engine`: Best for large-scale batch processing

2. **Use async mode for large documents**:
   - Files > 50 pages → use `parse_document_async`
   - Monitor task status with `get_parse_result`

3. **Optimize parameters**:
   - Disable formula/table recognition if not needed
   - Adjust priority for urgent tasks

## Development

### Local Testing

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure `.env` file with Dify debug credentials
4. Run: `python -m main`

### Project Structure

```
mineru-tianshu/
├── manifest.yaml              # Plugin metadata
├── provider/
│   ├── mineru-tianshu.yaml   # Provider configuration
│   └── mineru-tianshu.py     # Provider implementation
├── tools/
│   ├── parse_document.yaml   # Sync tool definition
│   ├── parse_document.py     # Sync tool implementation
│   ├── parse_document_async.yaml
│   ├── parse_document_async.py
│   ├── get_parse_result.yaml
│   └── get_parse_result.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please:

1. Fork this repository
2. Create a feature branch
3. Submit a pull request

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Support

If you encounter any issues or have questions:

- **GitHub Issues**: [Report issues or request features](https://github.com/your-username/mineru-tianshu-plugin/issues)
- **Email Support**: support@your-domain.com

We strive to respond to all support requests within 48 hours.

## Acknowledgments

- [MinerU](https://github.com/opendatalab/MinerU) - Powerful document extraction toolkit
- [Dify](https://dify.ai) - LLM application development platform

---

Made with ❤️ by the Tavan Team
