/**
 * Shared types for frontend and backend (mirror in Python as needed).
 */

export interface SearchResult {
  id: string;
  url: string;
  title: string;
  snippet: string;
  score: number;
  metadata?: Record<string, unknown>;
}

export interface ParsedDocument {
  url: string;
  title: string;
  description: string;
  content: string;
  contentHtml?: string;
  links?: string[];
  meta?: Record<string, unknown>;
}

export interface CrawlResult {
  url: string;
  html: string;
  statusCode: number;
  finalUrl?: string;
  meta?: Record<string, unknown>;
}
