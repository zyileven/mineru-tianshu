# MinerU 天枢 Dify 插件

> MinerU 驱动的企业级多GPU文档解析服务

[![Version](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/zyileven/mineru-tianshu)
[![License](https://img.shields.io/badge/license-Apache%202.0-green.svg)](https://github.com/zyileven/mineru-tianshu/blob/main/LICENSE)
[![Dify Plugin](https://img.shields.io/badge/Dify-插件-orange.svg)](https://dify.ai)
[![GitHub](https://img.shields.io/badge/GitHub-zyileven%2Fmineru--tianshu-181717?logo=github)](https://github.com/zyileven/mineru-tianshu)

## 目录

- [概述](#概述)
- [功能特性](#功能特性)
- [安装](#安装)
- [使用示例](#使用示例)
- [配置](#配置)
- [API 服务器部署](#api-服务器部署)
- [故障排除](#故障排除)
- [性能优化建议](#性能优化建议)
- [开发](#开发)
- [贡献](#贡献)
- [支持](#支持)

## 概述

MinerU 天枢是一个强大的 Dify 插件,通过 MinerU 的企业级基础设施提供高质量的文档解析能力。将 PDF、图片和 Office 文档转换为结构化的 Markdown 格式,支持:

- 📄 **多格式支持**: PDF、图片(PNG、JPG)、Office 文件(Word、Excel、PowerPoint)
- 🔢 **公式识别**: 提取 LaTeX 格式的数学公式
- 📊 **表格提取**: 保留表格结构和格式
- 🌍 **多语言**: 中文、英语、韩语、日语等
- ⚡ **多GPU加速**: 利用 GPU 基础设施实现快速处理
- 🎯 **多种后端**: 可选 pipeline、VLM-transformers 或 VLM-vLLM 引擎

## 功能特性

本插件提供 **3 个工具**,支持灵活的文档处理工作流:

### 1. 解析文档(同步)
**`parse_document`** - 一键文档解析,自动等待

- 提交文档并等待完成
- 直接返回解析后的 Markdown 内容
- 适合交互式工作流
- 持续等待直到处理完成(无超时限制)

### 2. 解析文档(异步)
**`parse_document_async`** - 提交后继续工作流

- 提交文档进行后台处理
- 立即返回任务 ID
- 适合大文档或批量处理
- 支持优先级队列

### 3. 获取解析结果
**`get_parse_result`** - 稍后检索结果

- 检查任务状态(等待中/处理中/已完成/失败)
- 任务完成后获取解析的 Markdown
- 配合异步提交的任务 ID 使用

## 安装

### 前置要求

- Dify 实例(自托管或云版本)
- MinerU 天枢 API 服务器(必需)
- Python 3.11+(插件运行时)

### ⚠️ 重要:Dify 服务器配置

**对于自托管的 Dify 实例**,您必须在 Dify 服务器的 `.env` 文件中配置 `FILES_URL` 环境变量:

```bash
# 在 Dify 服务器的 .env 文件中添加
FILES_URL=http://你的dify服务器:端口
# 示例: FILES_URL=http://localhost:3000
# 示例: FILES_URL=https://your-dify-domain.com
```

这样插件才能从您的 Dify 实例下载文件。如果没有配置,您会看到如下错误:
```
Error: Invalid file URL '/files/...': Request URL is missing an 'http://' or 'https://' protocol
```

**注意**: Dify Cloud 用户不需要此配置,因为已经预先设置好了。

### 快速开始

#### 方式一:从 Dify 插件市场安装(推荐)

1. **安装插件** 到您的 Dify 实例:
   - 导航到 **工具与插件** → **插件市场**
   - 搜索 **"MinerU Tianshu"** 或 **"MinerU 天枢"**
   - 点击 **安装**

2. **配置 API 服务器**:
   - 进入插件设置
   - 输入您的 MinerU 天枢 API 服务器 URL
   - 示例: `http://localhost:8100`
   - (可选)如果服务器需要认证,添加 API 密钥

3. **开始使用** 在工作流或 Agent 中!

#### 方式二:手动安装

1. **下载插件包** 从 [GitHub Releases](https://github.com/zyileven/mineru-tianshu/releases)

2. **上传到 Dify**:
   - 进入 **工具与插件** → **自定义插件**
   - 点击 **上传插件**
   - 选择下载的插件包

3. **配置并使用** 如方式一所述

## 使用示例

### 示例 1: 工作流中的同步解析

```yaml
工具: parse_document
输入:
  - file: {{上传的文档}}
  - backend: pipeline
  - lang: ch
  - formula_enable: true
  - table_enable: true

输出:
  {{markdown_content}}
```

### 示例 2: 异步处理

**步骤 1: 提交文档**
```yaml
工具: parse_document_async
输入:
  - file: {{文档}}
  - priority: 5

输出:
  {{parse_document_async.text}}  # 直接返回 task_id 字符串
```

**步骤 2: 稍后获取结果**
```yaml
工具: get_parse_result
输入:
  - task_id: {{parse_document_async.text}}  # 使用上一步的 task_id

输出:
  {{markdown_content}}
```

### 示例 3: 文档分析 Agent

创建一个 Agent:
1. 使用 `parse_document` 将 PDF 转换为 Markdown
2. 用 LLM 分析内容
3. 提取关键信息

## 配置

### MinerU-tianshu API 服务器 URL
- **必填**: 是
- **格式**: `http://你的服务器:端口`
- **示例**: `http://localhost:8100`

### 工具参数

#### 后端选项
- `pipeline` (推荐): 平衡性能和准确度
- `vlm-transformers`: 基于 Transformers 的视觉语言模型
- `vlm-vllm-engine`: 优化的 VLM 引擎,适合大规模处理

#### 语言支持
- `ch`: 中文(简体)
- `en`: 英语
- `korean`: 韩语
- `japan`: 日语

#### 处理选项
- **公式识别**: 提取数学公式
- **表格识别**: 保留表格结构
- **优先级**: 队列优先级(0-100,数值越大越优先)

## API 服务器部署

如果您还没有 MinerU 天枢服务器,可以这样部署:

### 使用 Docker

```bash
docker run -d \
  --name mineru-tianshu \
  --gpus all \
  -p 8100:8000 \
  -e API_PORT=8000 \
  your-registry/mineru-tianshu:latest
```

### 从源码部署

```bash
cd MinerU/projects/mineru_tianshu
pip install -r requirements.txt
python api_server.py
```

查看 [MinerU 天枢文档](https://github.com/opendatalab/MinerU) 了解更多详情。

## 故障排除

### 连接错误

**错误**: "API Server URL is not configured"
- **解决方案**: 在插件设置中配置 API 服务器 URL

**错误**: "Network error: Connection refused"
- **解决方案**: 检查 MinerU 天枢服务器是否正在运行且可访问

### 处理时间过长

**现象**: 文档处理时间很长
- **原因**: 大文件、复杂布局或服务器资源有限
- **解决方案**:
  - 如果不想等待,使用 `parse_document_async` + `get_parse_result`
  - 检查服务器 GPU 可用性和资源使用情况
  - 对于紧急任务可以设置更高的优先级值

### 找不到结果

**警告**: "Task completed but no content found"
- **原因**: 结果文件已被清理(超过保留期限)
- **解决方案**: 在服务器上配置更长的保留期限

## 性能优化建议

1. **选择合适的后端**:
   - `pipeline`: 适合一般文档
   - `vlm-vllm-engine`: 适合大规模批量处理

2. **大文档使用异步模式**:
   - 文件 > 50 页 → 使用 `parse_document_async`
   - 用 `get_parse_result` 监控任务状态

3. **优化参数**:
   - 如不需要可禁用公式/表格识别
   - 为紧急任务调整优先级

## 开发

### 本地测试

1. **克隆仓库**
   ```bash
   git clone https://github.com/zyileven/mineru-tianshu.git
   cd mineru-tianshu
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境**
   - 复制 `.env.example` 为 `.env`
   - 填入 Dify 调试凭证
   - 配置 MinerU 天枢 API 服务器 URL

4. **运行插件**
   ```bash
   python -m main
   ```

### 项目结构

```
mineru-tianshu/
├── manifest.yaml              # 插件元数据
├── provider/
│   ├── mineru-tianshu.yaml   # 提供者配置
│   └── mineru-tianshu.py     # 提供者实现
├── tools/
│   ├── parse_document.yaml   # 同步工具定义
│   ├── parse_document.py     # 同步工具实现
│   ├── parse_document_async.yaml
│   ├── parse_document_async.py
│   ├── get_parse_result.yaml
│   └── get_parse_result.py
├── requirements.txt
├── LICENSE
└── README.md
```

### 运行测试

```bash
# 运行单元测试
pytest tests/

```

## 贡献

欢迎贡献!请:

1. Fork 仓库 [github.com/zyileven/mineru-tianshu](https://github.com/zyileven/mineru-tianshu)
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

查看 [CONTRIBUTING.md](https://github.com/zyileven/mineru-tianshu/blob/main/CONTRIBUTING.md) 了解更多详情。

## 许可证

Apache License 2.0 - 详见 [LICENSE](LICENSE)

## 支持

如果您遇到任何问题或有疑问:

- **GitHub Issues**: [报告问题或请求功能](https://github.com/zyileven/mineru-tianshu/issues)
- **邮件支持**: zyileven@gmail.com
- **文档**: 查看我们的[详细文档](https://github.com/zyileven/mineru-tianshu#readme)

我们力求在 48 小时内回复所有支持请求。


## 致谢

- [MinerU](https://github.com/opendatalab/MinerU) - 强大的文档提取工具包
- [Dify](https://dify.ai) - LLM 应用开发平台

---

**由 [zyileven](https://github.com/zyileven) 用 ❤️ 制作**

⭐ 如果这个插件对您有帮助,请考虑在 [GitHub](https://github.com/zyileven/mineru-tianshu) 上给我们一个 Star!
