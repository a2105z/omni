import type { Status } from "./base";

export interface ImageSource {
  title: string;
  imgUrl: string;
  thumbnailUrl: string;
  webUrl: string;
  summary: string;
  sourceNumber: number;
}

export interface ImageScrapeStatus {
  scrapeStatus: Status;
  source: ImageSource;
  error?: string;
}
