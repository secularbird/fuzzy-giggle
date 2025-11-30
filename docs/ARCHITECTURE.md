# Knowledge Server 架构设计文档

## 目录

1. [概述](#概述)
2. [系统架构](#系统架构)
3. [核心组件](#核心组件)
4. [数据流](#数据流)
5. [技术选型](#技术选型)
6. [安全设计](#安全设计)
7. [扩展性设计](#扩展性设计)
8. [部署架构](#部署架构)

---

## 概述

### 项目目标

Knowledge Server 旨在提供一个完整的知识管理后端服务，支持:

- 文档的向量化存储和相似度搜索
- 实体关系的图数据库存储
- 网页内容的自动抓取和入库
- 统一的 REST API 接口

### 设计原则

1. **模块化**: 各组件独立，易于维护和替换
2. **可扩展**: 支持水平和垂直扩展
3. **安全性**: 内置安全防护机制
4. **易用性**: 提供 CLI 和 API 两种交互方式

---

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            客户端层                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Web 应用   │  │  移动应用    │  │   CLI 工具   │  │  第三方系统  │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
└─────────┼────────────────┼────────────────┼────────────────┼───────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            API 层 (FastAPI)                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     REST API Endpoints                           │   │
│  │  /health  /documents  /entities  /search  /context  /scrape     │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   Pydantic 数据验证                              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            业务逻辑层                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                       RAG Engine                                 │   │
│  │  ┌──────────────────┐           ┌──────────────────┐           │   │
│  │  │   文档处理模块    │           │   检索合并模块    │           │   │
│  │  │  - 文本嵌入      │           │  - 向量搜索      │           │   │
│  │  │  - 分块处理      │           │  - 图谱查询      │           │   │
│  │  │  - 元数据提取    │           │  - 结果排序      │           │   │
│  │  └──────────────────┘           └──────────────────┘           │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Scrapy Server                                │   │
│  │  - URL 验证        - 内容提取        - 自动入库                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            数据存储层                                    │
│  ┌───────────────────────────┐    ┌───────────────────────────┐        │
│  │      Vector Store         │    │       Graph Store         │        │
│  │       (usearch)           │    │       (Kùzu DB)           │        │
│  │  ┌─────────────────────┐  │    │  ┌─────────────────────┐  │        │
│  │  │   向量索引          │  │    │  │    Document 节点    │  │        │
│  │  │   - 384 维向量      │  │    │  │    - id, title     │  │        │
│  │  │   - 余弦相似度      │  │    │  │    - content, url  │  │        │
│  │  └─────────────────────┘  │    │  └─────────────────────┘  │        │
│  │  ┌─────────────────────┐  │    │  ┌─────────────────────┐  │        │
│  │  │   文本映射表        │  │    │  │    Entity 节点      │  │        │
│  │  │   - ID -> 文本      │  │    │  │    - id, name      │  │        │
│  │  └─────────────────────┘  │    │  │    - type, desc    │  │        │
│  └───────────────────────────┘    │  └─────────────────────┘  │        │
│                                   │  ┌─────────────────────┐  │        │
│                                   │  │    关系边           │  │        │
│                                   │  │    - MENTIONS      │  │        │
│                                   │  │    - RELATED_TO    │  │        │
│                                   │  └─────────────────────┘  │        │
│                                   └───────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────────┘
```

### 组件交互图

```
                         ┌──────────────┐
                         │   Client     │
                         └──────┬───────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │    FastAPI Server     │
                    │   (api/server.py)     │
                    └───────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
    ┌─────────────────┐ ┌──────────────┐ ┌───────────────┐
    │   RAG Engine    │ │ Graph Store  │ │ Scrapy Runner │
    │(rag/rag_engine) │ │(graph_store) │ │   (runner)    │
    └────────┬────────┘ └──────┬───────┘ └───────┬───────┘
             │                 │                 │
             ▼                 ▼                 ▼
    ┌─────────────────┐ ┌──────────────┐ ┌───────────────┐
    │  Vector Store   │ │   Kùzu DB    │ │ URL Validator │
    │  (usearch)      │ │              │ │               │
    └─────────────────┘ └──────────────┘ └───────────────┘
```

---

## 核心组件

### 1. API 层 (api/server.py)

**职责:**
- 提供 RESTful API 接口
- 请求参数验证
- 响应格式化
- 错误处理

**技术栈:**
- FastAPI: 高性能异步 Web 框架
- Pydantic: 数据验证和序列化
- Uvicorn: ASGI 服务器

**关键类:**
```python
class DocumentRequest(BaseModel):
    doc_id: str
    title: str
    content: str
    url: Optional[str] = None
    entities: Optional[List[Dict[str, str]]] = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    include_graph: bool = True
    entity_name: Optional[str] = None
```

### 2. 向量存储 (vector_db/vector_store.py)

**职责:**
- 向量索引管理
- 相似度搜索
- 数据持久化

**技术栈:**
- usearch: 高性能向量搜索库
- NumPy: 向量运算

**核心接口:**
```python
class VectorStore:
    def add(vectors, texts, ids) -> List[int]
    def search(query_vector, top_k) -> List[Tuple[int, float, str]]
    def delete(ids) -> None
    def save(path) -> None
    def load(path) -> None
```

**存储结构:**
```
vector_store/
├── index.usearch      # 向量索引文件
└── index.texts.npy    # ID到文本的映射
```

### 3. 图存储 (graph_db/graph_store.py)

**职责:**
- 文档和实体节点管理
- 关系边管理
- 图查询

**技术栈:**
- Kùzu: 嵌入式图数据库

**数据模型:**
```
节点类型:
- Document(id, title, content, url)
- Entity(id, name, entity_type, description)

关系类型:
- MENTIONS: Document -> Entity
- RELATED_TO: Entity -> Entity (relation_type)
```

**核心接口:**
```python
class GraphStore:
    def add_document(doc_id, title, content, url) -> None
    def add_entity(entity_id, name, entity_type, description) -> None
    def link_document_entity(doc_id, entity_id) -> None
    def link_entities(source_id, target_id, relation_type) -> None
    def get_document(doc_id) -> Dict
    def get_entity(entity_id) -> Dict
    def get_related_entities(entity_id, relation_type) -> List[Dict]
    def search_entities(name_pattern, entity_type) -> List[Dict]
```

### 4. RAG 引擎 (rag/rag_engine.py)

**职责:**
- 文本嵌入生成
- 混合检索 (向量 + 图)
- 结果重排序
- 上下文构建

**技术栈:**
- sentence-transformers: 文本嵌入模型
- cross-encoder: 重排序模型
- NumPy: 向量运算

**核心接口:**
```python
class RAGEngine:
    def embed_text(text) -> np.ndarray
    def embed_texts(texts) -> np.ndarray
    def add_document(doc_id, title, content, url, entities) -> None
    def retrieve(query, top_k, include_graph_context, use_reranker) -> List[Dict]
    def retrieve_with_graph(query, entity_name, top_k) -> Dict
    def get_context(query, top_k, max_tokens) -> str
```

### 5. 重排序器 (rag/reranker.py)

**职责:**
- 使用交叉编码器对检索结果进行精排
- 提高检索质量

**技术栈:**
- sentence-transformers CrossEncoder: 交叉编码器模型

**支持的模型:**

| 模型 | 参数量 | 特点 |
|------|--------|------|
| cross-encoder/ms-marco-MiniLM-L-6-v2 | 22M | 快速高效，推荐通用场景 |
| cross-encoder/ms-marco-MiniLM-L-12-v2 | 33M | 更高准确度 |
| BAAI/bge-reranker-base | 278M | 性能与准确度平衡 |
| BAAI/bge-reranker-large | 560M | 最高准确度 |
| BAAI/bge-reranker-v2-m3 | - | 多语言支持 (含中文) |

**核心接口:**
```python
class Reranker:
    def rerank(query, documents, top_k) -> List[Tuple[int, float, str]]
    def rerank_results(query, results, content_key, top_k) -> List[Dict]
    @staticmethod
    def list_available_models() -> Dict[str, Dict[str, str]]
    def get_model_info() -> Dict[str, Any]
```

### 6. 网页抓取 (scrapy_server/)

**职责:**
- URL 验证 (防止 SSRF)
- 网页内容抓取
- 内容解析

**组件:**

```python
# spider.py - Scrapy 爬虫
class ContentSpider(CrawlSpider):
    # 支持链接跟踪的完整爬虫

class SimpleSpider(Spider):
    # 单页面抓取

# runner.py - 爬虫运行器
class ScrapyRunner:
    # 同步抓取运行器

class AsyncScrapyRunner:
    # 异步抓取运行器 (用于 FastAPI)

def validate_url(url, allowed_domains) -> str:
    # URL 安全验证
```

---

## 数据流

### 文档添加流程

```
1. 客户端请求
   POST /documents
   {doc_id, title, content, url, entities}
         │
         ▼
2. API 层验证
   DocumentRequest 验证
         │
         ▼
3. RAG Engine 处理
   ┌─────────────────────────────────────┐
   │ a. 生成文本嵌入向量 (384维)          │
   │ b. 添加到 VectorStore               │
   │ c. 添加到 GraphStore                │
   │ d. 如果有实体，创建实体和关系        │
   └─────────────────────────────────────┘
         │
         ▼
4. 返回成功响应
   {"status": "success", "doc_id": "..."}
```

### 搜索流程

```
1. 客户端请求
   POST /search
   {query, top_k, include_graph, entity_name}
         │
         ▼
2. RAG Engine 检索
   ┌─────────────────────────────────────┐
   │ a. 查询文本转换为嵌入向量            │
   │ b. VectorStore 相似度搜索           │
   │ c. (可选) GraphStore 实体搜索       │
   │ d. 结果合并和排序                   │
   └─────────────────────────────────────┘
         │
         ▼
3. 返回搜索结果
   {"results": [...], "graph_results": {...}}
```

### 网页抓取流程

```
1. 客户端请求
   POST /scrape
   {urls, add_to_knowledge_base}
         │
         ▼
2. URL 验证
   ┌─────────────────────────────────────┐
   │ - 检查 URL 格式                     │
   │ - 检查协议 (只允许 http/https)       │
   │ - 检查是否为私有 IP                  │
   └─────────────────────────────────────┘
         │
         ▼
3. 内容抓取
   ┌─────────────────────────────────────┐
   │ - HTTP 请求获取页面                  │
   │ - BeautifulSoup 解析 HTML           │
   │ - 提取标题和正文内容                 │
   └─────────────────────────────────────┘
         │
         ▼
4. (可选) 添加到知识库
   └── 调用 RAG Engine 添加文档
         │
         ▼
5. 返回抓取结果
   {"scraped": [...]}
```

---

## 技术选型

### 核心依赖

| 组件 | 技术 | 选型理由 |
|------|------|----------|
| Web 框架 | FastAPI | 高性能、自动文档、类型安全 |
| 向量数据库 | usearch | 轻量级、高性能、易部署 |
| 图数据库 | Kùzu DB | 嵌入式、支持 Cypher、高性能 |
| 嵌入模型 | sentence-transformers | 开源、多语言支持、易用 |
| 网页抓取 | Scrapy | 成熟稳定、功能丰富 |
| 配置管理 | pydantic-settings | 类型安全、环境变量支持 |

### 向量维度选择

默认使用 384 维向量 (all-MiniLM-L6-v2 模型):

| 维度 | 模型 | 特点 |
|------|------|------|
| 384 | all-MiniLM-L6-v2 | 平衡性能和效果，适合通用场景 |
| 768 | all-mpnet-base-v2 | 更高精度，需要更多资源 |
| 512 | paraphrase-multilingual-MiniLM-L12-v2 | 多语言支持 |

### 距离度量

支持三种距离度量:

- `cos` (余弦相似度): 默认，适合文本相似度
- `l2` (欧氏距离): 适合精确匹配场景
- `ip` (内积): 适合已归一化的向量

---

## 安全设计

### URL 验证 (防止 SSRF)

```python
def validate_url(url: str, allowed_domains: List[str] = None) -> str:
    """
    验证步骤:
    1. 检查 URL 格式是否有效
    2. 只允许 http/https 协议
    3. 阻止访问私有 IP 地址:
       - localhost, 127.0.0.1, ::1
       - 10.0.0.0/8
       - 192.168.0.0/16
       - 172.16.0.0/12
       - 169.254.0.0/16 (Link-local)
    4. (可选) 只允许白名单域名
    """
```

### 输入验证

所有 API 输入通过 Pydantic 模型验证:

```python
class DocumentRequest(BaseModel):
    doc_id: str = Field(..., description="唯一标识")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="内容")
    # Pydantic 自动验证类型和格式
```

### 依赖安全

- 使用 requirements.txt 固定依赖版本
- 定期使用安全工具扫描依赖漏洞

---

## 扩展性设计

### 水平扩展

```
                    ┌──────────────┐
                    │ Load Balancer│
                    └──────┬───────┘
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   Server 1   │ │   Server 2   │ │   Server N   │
    └──────────────┘ └──────────────┘ └──────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   Shared DB     │
                  │  (可选配置)      │
                  └─────────────────┘
```

### 模块替换

各模块通过接口抽象，支持替换:

```python
# 向量存储可替换为:
# - Milvus
# - Pinecone
# - Weaviate

# 图数据库可替换为:
# - Neo4j
# - ArangoDB

# 嵌入模型可替换为:
# - OpenAI Embeddings
# - Cohere Embeddings
# - Custom Models
```

### 插件机制 (未来规划)

```python
# 文档处理器插件
class DocumentProcessor(Protocol):
    def process(self, content: str) -> ProcessedDocument: ...

# 实体提取器插件
class EntityExtractor(Protocol):
    def extract(self, text: str) -> List[Entity]: ...
```

---

## 部署架构

### 单机部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
export KNOWLEDGE_DATA_DIR=/var/data/knowledge_server
export KNOWLEDGE_HOST=0.0.0.0
export KNOWLEDGE_PORT=8000

# 3. 启动服务
python -m knowledge_server serve
```

### Docker 部署 (推荐)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["python", "-m", "knowledge_server", "serve"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  knowledge-server:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    environment:
      - KNOWLEDGE_DATA_DIR=/app/data
      - KNOWLEDGE_HOST=0.0.0.0
```

### 生产部署建议

1. **使用进程管理器**
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker \
       knowledge_server.api.server:app
   ```

2. **配置反向代理 (Nginx)**
   ```nginx
   upstream knowledge_server {
       server 127.0.0.1:8000;
   }
   
   server {
       listen 80;
       location / {
           proxy_pass http://knowledge_server;
       }
   }
   ```

3. **数据备份策略**
   - 定期备份 data 目录
   - 配置增量备份

4. **监控告警**
   - 集成 Prometheus + Grafana
   - 配置健康检查告警

---

## 附录

### 目录结构

```
knowledge_server/
├── __init__.py              # 包初始化，版本信息
├── __main__.py              # CLI 入口点
├── config.py                # 配置管理 (pydantic-settings)
├── api/
│   ├── __init__.py
│   └── server.py            # FastAPI 应用和端点
├── vector_db/
│   ├── __init__.py
│   └── vector_store.py      # usearch 向量存储实现
├── graph_db/
│   ├── __init__.py
│   └── graph_store.py       # Kùzu 图存储实现
├── rag/
│   ├── __init__.py
│   └── rag_engine.py        # RAG 引擎实现
└── scrapy_server/
    ├── __init__.py
    ├── spider.py            # Scrapy 爬虫定义
    └── runner.py            # 爬虫运行器和 URL 验证
```

### API 错误码

| HTTP 状态码 | 含义 |
|-------------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 性能指标 (参考)

| 操作 | 预期延迟 |
|------|----------|
| 健康检查 | < 10ms |
| 添加文档 | < 100ms |
| 向量搜索 | < 50ms |
| 图查询 | < 30ms |
| 网页抓取 | 取决于目标网站 |
