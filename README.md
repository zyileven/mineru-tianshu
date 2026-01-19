# MinerU Tianshu Plugin for Dify

> Enterprise-level multi-GPU document parsing service powered by MinerU

[![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/zyileven/mineru-tianshu)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/zyileven/mineru-tianshu/blob/main/LICENSE)
[![Dify Plugin](https://img.shields.io/badge/Dify-Plugin-orange.svg)](https://dify.ai)
[![GitHub](https://img.shields.io/badge/GitHub-zyileven%2Fmineru--tianshu-181717?logo=github)](https://github.com/zyileven/mineru-tianshu)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [API Server Setup](#api-server-setup)
- [Troubleshooting](#troubleshooting)
- [Performance Tips](#performance-tips)
- [Development](#development)
- [Contributing](#contributing)
- [Support](#support)

## Overview

MinerU Tianshu is a powerful Dify plugin that enables high-quality document parsing capabilities through MinerU's enterprise-level infrastructure.

**📌 Prerequisites**: This plugin requires the [MinerU Tianshu API Server](https://github.com/magicyuan876/mineru-tianshu) to be deployed first. Please deploy the upstream project before installing this plugin.

Convert PDFs, images, and Office documents into structured Markdown format with support for:

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
- **MinerU Tianshu API Server (required)** - You must deploy the upstream project first
- Python 3.11+ (for plugin runtime)

### ⚠️ Important: Deploy API Server First

**This plugin requires the MinerU Tianshu API Server to be deployed and running.** The API server is provided by the upstream project:

**Upstream Project**: [https://github.com/magicyuan876/mineru-tianshu](https://github.com/magicyuan876/mineru-tianshu)

**You MUST deploy this project before using this plugin**, as it provides all the backend API services for document parsing. Please follow the deployment instructions in the upstream project repository.

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

#### Option 1: Install from Dify Plugin Marketplace (Recommended)

1. **Install the plugin** in your Dify instance:
   - Navigate to **Tools & Plugins** → **Plugin Marketplace**
   - Search for **"MinerU Tianshu"**
   - Click **Install**

2. **Configure API Server**:
   - Go to plugin settings
   - Enter your MinerU Tianshu API Server URL
   - Example: `http://localhost:8100`
   - (Optional) Add API key if your server requires authentication

3. **Start using** in your workflows or agents!

#### Option 2: Manual Installation

1. **Download the plugin package** from [GitHub Releases](https://github.com/zyileven/mineru-tianshu/releases)

2. **Upload to Dify**:
   - Go to **Tools & Plugins** → **Custom Plugins**
   - Click **Upload Plugin**
   - Select the downloaded package

3. **Configure and use** as described in Option 1

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
  {{parse_document_async.text}}  # Returns task_id directly as a string
```

**Step 2: Retrieve Result Later**
```yaml
Tool: get_parse_result
Inputs:
  - task_id: {{parse_document_async.text}}  # Use the task_id from previous step

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

**IMPORTANT**: This plugin requires the MinerU Tianshu API Server from the upstream project:

**🔗 Upstream Project**: [https://github.com/magicyuan876/mineru-tianshu](https://github.com/magicyuan876/mineru-tianshu)

### Deployment Steps

1. **Clone the upstream project**:
   ```bash
   git clone https://github.com/magicyuan876/mineru-tianshu.git
   cd mineru-tianshu
   ```

2. **Follow the deployment instructions** in the upstream project's README:
   - Docker deployment (recommended)
   - Source code deployment
   - Configuration and setup

3. **Verify the API server is running**:
   - Default port: `8100` (or as configured)
   - Test endpoint: `http://your-server:8100/health` (if available)

4. **Use the API server URL** when configuring this plugin in Dify:
   - Example: `http://localhost:8100`
   - Example: `http://your-server-ip:8100`

For detailed deployment instructions, configuration options, and troubleshooting, please refer to the [upstream project documentation](https://github.com/magicyuan876/mineru-tianshu).

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

1. **Clone the repository**
   ```bash
   git clone https://github.com/zyileven/mineru-tianshu.git
   cd mineru-tianshu
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   - Copy `.env.example` to `.env`
   - Add your Dify debug credentials
   - Configure MinerU Tianshu API Server URL

4. **Run the plugin**
   ```bash
   python -m main
   ```

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
├── LICENSE
└── README.md
```

### Running Tests

```bash
# Run unit tests
pytest tests/

```

## Contributing

Contributions are welcome! Please:

1. Fork the repository at [github.com/zyileven/mineru-tianshu](https://github.com/zyileven/mineru-tianshu)
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

See [CONTRIBUTING.md](https://github.com/zyileven/mineru-tianshu/blob/main/CONTRIBUTING.md) for more details.

## License

Apache License 2.0 - see [LICENSE](LICENSE) for details.

## Support

If you encounter any issues or have questions:

- **GitHub Issues**: [Report issues or request features](https://github.com/zyileven/mineru-tianshu/issues)
- **Email Support**: zyileven@gmail.com
- **Documentation**: Check out our [detailed documentation](https://github.com/zyileven/mineru-tianshu#readme)

We strive to respond to all support requests within 48 hours.

## Acknowledgments

- [MinerU Tianshu API Server](https://github.com/magicyuan876/mineru-tianshu) - The upstream project providing the document parsing API
- [MinerU](https://github.com/opendatalab/MinerU) - Powerful document extraction toolkit
- [Dify](https://dify.ai) - LLM application development platform

---

**Made with ❤️ by [zyileven](https://github.com/zyileven)**

⭐ If you find this plugin helpful, please consider giving it a star on [GitHub](https://github.com/zyileven/mineru-tianshu)!
