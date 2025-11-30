# Knowledge Server 用户手册

## 目录

1. [简介](#简介)
2. [系统要求](#系统要求)
3. [安装指南](#安装指南)
4. [快速入门](#快速入门)
5. [命令行界面](#命令行界面)
6. [REST API 参考](#rest-api-参考)
7. [配置说明](#配置说明)
8. [常见问题](#常见问题)

---

## 简介

Knowledge Server 是一个基于 RAG（检索增强生成）的知识服务器，结合了向量数据库、图数据库和网页抓取功能，为构建智能知识管理系统提供完整的后端服务。

### 核心功能

- **向量搜索**: 基于 usearch 的高效相似度搜索
- **知识图谱**: 基于 Kùzu DB 的实体关系存储
- **网页抓取**: 基于 Scrapy 的自动内容提取
- **REST API**: 基于 FastAPI 的完整 HTTP 接口

---

## 系统要求

### 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核心 | 4+ 核心 |
| 内存 | 4 GB | 8+ GB |
| 存储 | 1 GB | 10+ GB |

### 软件要求

- Python 3.9 或更高版本
- pip 包管理器
- 操作系统: Linux, macOS, Windows

---

## 安装指南

### 方式一: 从源码安装

```bash
# 1. 克隆仓库
git clone https://github.com/secularbird/fuzzy-giggle.git
cd fuzzy-giggle

# 2. 创建虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt
```

### 方式二: 使用 pip 安装

```bash
pip install -e .
```

### 验证安装

```bash
python -m knowledge_server --help
```

---

## 快速入门

### 1. 启动服务器

```bash
# 默认配置启动
python -m knowledge_server serve

# 自定义端口启动
python -m knowledge_server serve --host 0.0.0.0 --port 8080
```

服务器启动后，访问 `http://localhost:8000/docs` 查看 API 文档。

### 2. 添加文档

```bash
# 使用 CLI
python -m knowledge_server add \
    --id doc1 \
    --title "人工智能简介" \
    --content "人工智能是计算机科学的一个分支..."

# 使用 API
curl -X POST http://localhost:8000/documents \
    -H "Content-Type: application/json" \
    -d '{
        "doc_id": "doc1",
        "title": "人工智能简介",
        "content": "人工智能是计算机科学的一个分支..."
    }'
```

### 3. 搜索知识库

```bash
# 使用 CLI
python -m knowledge_server search "人工智能"

# 使用 API
curl -X POST http://localhost:8000/search \
    -H "Content-Type: application/json" \
    -d '{"query": "人工智能", "top_k": 5}'
```

### 4. 抓取网页内容

```bash
# 使用 CLI
python -m knowledge_server scrape https://example.com -o output.json

# 使用 API
curl -X POST http://localhost:8000/scrape \
    -H "Content-Type: application/json" \
    -d '{
        "urls": ["https://example.com"],
        "add_to_knowledge_base": true
    }'
```

---

## 命令行界面

### 全局选项

```bash
python -m knowledge_server [命令] [选项]
```

### 可用命令

#### `serve` - 启动 API 服务器

```bash
python -m knowledge_server serve [选项]

选项:
    --host TEXT     服务器主机地址 (默认: 0.0.0.0)
    --port INTEGER  服务器端口 (默认: 8000)
```

#### `add` - 添加文档

```bash
python -m knowledge_server add [选项]

选项:
    --id TEXT       文档唯一标识 (必填)
    --title TEXT    文档标题 (必填)
    --content TEXT  文档内容 (必填)
    --url TEXT      来源 URL (可选)
```

#### `search` - 搜索知识库

```bash
python -m knowledge_server search [查询] [选项]

参数:
    查询            搜索查询文本

选项:
    --top-k INTEGER 返回结果数量 (默认: 5)
```

#### `scrape` - 抓取网页

```bash
python -m knowledge_server scrape [URLs] [选项]

参数:
    URLs            要抓取的 URL 列表

选项:
    -o, --output TEXT     输出文件路径
    --follow-links        是否跟踪页面中的链接
```

---

## REST API 参考

### 基础信息

- **基础 URL**: `http://localhost:8000`
- **内容类型**: `application/json`

### 端点详情

#### 健康检查

```http
GET /health
```

**响应示例:**
```json
{
    "status": "healthy"
}
```

#### 添加文档

```http
POST /documents
```

**请求体:**
```json
{
    "doc_id": "string",
    "title": "string",
    "content": "string",
    "url": "string (可选)",
    "entities": [
        {
            "id": "string",
            "name": "string",
            "type": "string"
        }
    ]
}
```

**响应示例:**
```json
{
    "status": "success",
    "doc_id": "doc1"
}
```

#### 获取文档

```http
GET /documents/{doc_id}
```

**响应示例:**
```json
{
    "d.id": "doc1",
    "d.title": "文档标题",
    "d.content": "文档内容",
    "d.url": "https://example.com"
}
```

#### 添加实体

```http
POST /entities
```

**请求体:**
```json
{
    "entity_id": "string",
    "name": "string",
    "entity_type": "string",
    "description": "string (可选)"
}
```

#### 获取实体

```http
GET /entities/{entity_id}
```

#### 链接实体

```http
POST /entities/link
```

**请求体:**
```json
{
    "source_id": "string",
    "target_id": "string",
    "relation_type": "string"
}
```

#### 获取相关实体

```http
GET /entities/{entity_id}/related?relation_type=string
```

#### 搜索

```http
POST /search
```

**请求体:**
```json
{
    "query": "string",
    "top_k": 5,
    "include_graph": true,
    "entity_name": "string (可选)"
}
```

**响应示例:**
```json
{
    "results": [
        {
            "id": 123456,
            "score": 0.95,
            "content": "相关文档内容...",
            "entities": []
        }
    ],
    "graph_results": {}
}
```

#### 获取上下文

```http
POST /context?query=string&top_k=3&max_tokens=2000
```

**响应示例:**
```json
{
    "context": "合并后的相关文档内容..."
}
```

#### 抓取网页

```http
POST /scrape
```

**请求体:**
```json
{
    "urls": ["https://example.com"],
    "add_to_knowledge_base": true
}
```

**响应示例:**
```json
{
    "scraped": [
        {
            "url": "https://example.com",
            "title": "页面标题",
            "content": "页面内容..."
        }
    ]
}
```

---

## 配置说明

### 环境变量

所有配置项都以 `KNOWLEDGE_` 为前缀:

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `KNOWLEDGE_DATA_DIR` | 数据存储目录 | `./data` |
| `KNOWLEDGE_VECTOR_DB_PATH` | 向量数据库路径 | `{DATA_DIR}/vector_store` |
| `KNOWLEDGE_GRAPH_DB_PATH` | 图数据库路径 | `{DATA_DIR}/graph_store` |
| `KNOWLEDGE_VECTOR_DIMENSION` | 向量维度 | `384` |
| `KNOWLEDGE_VECTOR_METRIC` | 距离度量方式 | `cos` |
| `KNOWLEDGE_EMBEDDING_MODEL` | 嵌入模型名称 | `all-MiniLM-L6-v2` |
| `KNOWLEDGE_HOST` | 服务器主机 | `0.0.0.0` |
| `KNOWLEDGE_PORT` | 服务器端口 | `8000` |
| `KNOWLEDGE_SCRAPE_DELAY` | 抓取请求间隔(秒) | `1.0` |
| `KNOWLEDGE_SCRAPE_CONCURRENT` | 并发抓取数 | `4` |

### 配置文件

创建 `.env` 文件:

```env
KNOWLEDGE_DATA_DIR=./data
KNOWLEDGE_EMBEDDING_MODEL=all-MiniLM-L6-v2
KNOWLEDGE_HOST=0.0.0.0
KNOWLEDGE_PORT=8000
```

---

## 常见问题

### Q: 如何更换嵌入模型?

A: 设置环境变量 `KNOWLEDGE_EMBEDDING_MODEL` 为 sentence-transformers 支持的任意模型名称:

```bash
export KNOWLEDGE_EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
```

### Q: 向量搜索结果不准确怎么办?

A: 检查以下几点:
1. 确保文档内容足够丰富
2. 尝试更换嵌入模型
3. 调整 `top_k` 参数获取更多结果

### Q: 如何备份数据?

A: 复制 `KNOWLEDGE_DATA_DIR` 目录下的所有文件:

```bash
cp -r ./data ./data_backup
```

### Q: 抓取网页失败怎么办?

A: 检查以下几点:
1. 确保目标 URL 可访问
2. 某些网站可能需要设置代理
3. 私有 IP 地址会被安全机制拦截

### Q: 如何处理大量文档?

A: 建议:
1. 使用批量导入而非单条添加
2. 增加系统内存
3. 定期清理不需要的数据

---

## 获取帮助

- 提交 Issue: https://github.com/secularbird/fuzzy-giggle/issues
- 查看 API 文档: http://localhost:8000/docs (服务器运行时)
