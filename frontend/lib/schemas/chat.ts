import type {
  BraveImageSearchResponse,
  BraveWebSearchResponse,
} from "./brave";
import type { ImageScrapeStatus } from "./image";
import type { WebScrapeStatus } from "./search";

export interface UserMessage {
  content: string;
}

/** Backend-style source (from /api/answer) */
export interface BackendSource {
  url: string;
  title: string;
  snippet?: string;
  domain?: string;
}

export interface AssistantMessage {
  searchQueries?: string[];
  isDoneGeneratingSearchQueries?: boolean;
  isDonePerformingSearch?: boolean;
  searchResults?: BraveWebSearchResponse;
  isDoneProcessingSearchResults?: boolean;
  processedSearchResults?: WebScrapeStatus[];
  /** Backend sources (from /api/answer) - used when backend is used */
  backendSources?: BackendSource[];
  backendImageSources?: { sourceNumber: number; imgUrl: string; title: string; summary?: string }[];
  imageSearchQueries?: string[];
  isDonePerformingImageSearch?: boolean;
  imageSearchResults?: BraveImageSearchResponse;
  isDoneProcessingImageSearchResults?: boolean;
  processedImageSearchResults?: ImageScrapeStatus[];
  finalAnswer?: string;
  isDoneGeneratingFinalAnswer?: boolean;
  followUpSearchQueries?: string[];
  /** Error message when generation fails */
  error?: string;
}

export interface AiWebSearchResponse {
  optimizedQueries: string[];
  processedSearchResults: WebScrapeStatus[];
}

export interface AiImageSearchResponse {
  optimizedQueries: string[];
  processedImageSearchResults: ImageScrapeStatus[];
}

export interface Message {
  userMessage: UserMessage;
  assistantMessage: AssistantMessage;
}

export interface Session {
  id: string;
  messages: Message[];
  title: string;
  hasTitleBeenSet: boolean;
}
