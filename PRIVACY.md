# Privacy Policy for MinerU Tianshu Plugin

**Last Updated:** December 4, 2025

## Overview

This privacy policy describes how the MinerU Tianshu plugin for Dify handles user data and protects your privacy.

## Data Collection

**This plugin does NOT collect, store, or transmit any personal user data to third-party services.**

## Data Processing

### Document Processing
- Documents submitted through this plugin are sent directly to **your configured MinerU Tianshu API server**
- All document processing occurs on your own infrastructure or the infrastructure you specify
- The plugin acts as a bridge between Dify and your MinerU Tianshu API server
- No document content is transmitted to any third-party services

### API Communication
- The plugin only communicates with the MinerU Tianshu API server URL that **you provide** in the plugin configuration
- All API requests are made directly from your Dify instance to your specified server
- No intermediate servers or proxies are used

## Credentials and API Keys

### Secure Storage
- API credentials (server URL and optional API key) are stored securely within your Dify instance
- Dify uses encrypted credential storage to protect sensitive information
- Credentials are never exposed in logs or error messages

### API Key Transmission
- If you configure an optional API key, it is transmitted securely to your MinerU Tianshu API server using HTTPS Bearer authentication
- API keys are only sent to the server URL you specify

## Data Retention

- **The plugin does not store any data**
- All parsing results are retrieved directly from your MinerU Tianshu API server
- Data retention is controlled by your MinerU Tianshu server configuration

## Third-Party Services

This plugin does **NOT** use any third-party services, analytics, or tracking tools. All functionality is self-contained and operates within your infrastructure.

## User Control

You have complete control over:
- Which MinerU Tianshu API server to use
- What documents to process
- API credentials and authentication
- Data retention policies (managed by your API server)

## Infrastructure Requirements

To use this plugin, you must:
1. Deploy and maintain your own MinerU Tianshu API server
2. Configure the plugin with your server's URL
3. Optionally configure API authentication

## Security Best Practices

We recommend:
- ✅ Use HTTPS for your MinerU Tianshu API server
- ✅ Enable API key authentication
- ✅ Configure appropriate network security rules
- ✅ Regularly update your MinerU Tianshu server
- ✅ Monitor API access logs

## Changes to This Privacy Policy

We may update this privacy policy from time to time. The "Last Updated" date at the top of this policy indicates when it was last revised.

## Contact

If you have questions about this privacy policy or the plugin's data handling practices, please contact:

- **GitHub Issues:** [Your Repository URL]
- **Email:** [Your Email]

## Compliance

This plugin is designed to:
- Respect user privacy
- Comply with data protection regulations (GDPR, CCPA, etc.)
- Give users full control over their data
- Operate within user-controlled infrastructure

## Disclaimer

The plugin author is not responsible for:
- Data handling practices of your MinerU Tianshu API server
- Security of your infrastructure
- Compliance obligations related to your use of the plugin

You are responsible for ensuring your deployment complies with applicable laws and regulations in your jurisdiction.
