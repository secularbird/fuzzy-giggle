import axios, { type AxiosInstance } from 'axios';

// Types
export interface Document {
  doc_id: string;
  title: string;
  content: string;
  url?: string;
  entities?: Entity[];
}

export interface Entity {
  entity_id: string;
  name: string;
  entity_type: string;
  description?: string;
}

export interface EntityLink {
  source_id: string;
  target_id: string;
  relation_type: string;
}

export interface SearchResult {
  id: number;
  score: number;
  content?: string;
  entities?: Entity[];
  original_score?: number;
  reranked?: boolean;
}

export interface SearchResponse {
  results: SearchResult[];
  graph_results?: Record<string, unknown>;
}

export interface ScrapeRequest {
  urls: string[];
  add_to_knowledge_base: boolean;
}

export interface ScrapeResult {
  url: string;
  title?: string;
  content?: string;
  error?: string;
}

// API Client
class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  setBaseURL(url: string) {
    this.client.defaults.baseURL = url;
  }

  // Health check
  async healthCheck(): Promise<{ status: string }> {
    const response = await this.client.get('/health');
    return response.data;
  }

  // Document operations
  async addDocument(document: Omit<Document, 'entities'> & { entities?: Array<{ id: string; name: string; type: string }> }): Promise<{ status: string; doc_id: string }> {
    const response = await this.client.post('/documents', document);
    return response.data;
  }

  async getDocument(docId: string): Promise<Document> {
    const response = await this.client.get(`/documents/${docId}`);
    return response.data;
  }

  // Entity operations
  async addEntity(entity: Entity): Promise<{ status: string; entity_id: string }> {
    const response = await this.client.post('/entities', entity);
    return response.data;
  }

  async getEntity(entityId: string): Promise<Entity> {
    const response = await this.client.get(`/entities/${entityId}`);
    return response.data;
  }

  async linkEntities(link: EntityLink): Promise<{ status: string }> {
    const response = await this.client.post('/entities/link', link);
    return response.data;
  }

  async getRelatedEntities(entityId: string, relationType?: string): Promise<Entity[]> {
    const params = relationType ? { relation_type: relationType } : {};
    const response = await this.client.get(`/entities/${entityId}/related`, { params });
    return response.data;
  }

  // Search operations
  async search(
    query: string, 
    topK: number = 5, 
    includeGraph: boolean = true,
    entityName?: string,
    useReranker?: boolean
  ): Promise<SearchResponse> {
    const response = await this.client.post('/search', {
      query,
      top_k: topK,
      include_graph: includeGraph,
      entity_name: entityName,
      use_reranker: useReranker,
    });
    return response.data;
  }

  // Context for generation
  async getContext(query: string, topK: number = 3, maxTokens: number = 2000): Promise<{ context: string }> {
    const response = await this.client.post('/context', null, {
      params: { query, top_k: topK, max_tokens: maxTokens },
    });
    return response.data;
  }

  // Scraping operations
  async scrapeUrls(request: ScrapeRequest): Promise<{ scraped: ScrapeResult[] }> {
    const response = await this.client.post('/scrape', request);
    return response.data;
  }

  // Reranker info
  async listRerankers(): Promise<{
    available_models: Record<string, unknown>;
    current_model: Record<string, unknown> | null;
    reranking_enabled: boolean;
  }> {
    const response = await this.client.get('/rerankers');
    return response.data;
  }
}

// Export singleton instance
export const api = new ApiClient();
export default api;
