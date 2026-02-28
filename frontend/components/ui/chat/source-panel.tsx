"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, ExternalLink, Shield } from "lucide-react";
import { cn } from "@/lib/utils";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";

export interface Source {
  id?: string;
  url: string;
  title: string;
  snippet?: string;
  domain?: string;
  favicon?: string;
  sourceNumber?: number;
}

interface SourcePanelProps {
  sources: Source[];
  imageSources?: { imgUrl: string; title: string; summary?: string; sourceNumber?: number }[];
  className?: string;
}

function extractDomain(url: string): string {
  try {
    const host = new URL(url).hostname;
    return host.replace(/^www\./, "");
  } catch {
    return "unknown";
  }
}

function TrustBadge({ domain }: { domain: string }) {
  const trusted = [".edu", ".gov", ".ac"].some((t) =>
    domain.toLowerCase().endsWith(t)
  );
  const known = [
    "wikipedia.org",
    "github.com",
    "stackoverflow.com",
    "mdn.io",
    "arxiv.org",
  ].some((k) => domain.toLowerCase().includes(k));
  if (!trusted && !known) return null;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded",
        trusted ? "bg-emerald-500/20 text-emerald-700 dark:text-emerald-400" : "bg-blue-500/20 text-blue-700 dark:text-blue-400"
      )}
    >
      <Shield className="h-2.5 w-2.5" />
      {trusted ? "Trusted" : "Verified"}
    </span>
  );
}

export function SourcePanel({
  sources,
  imageSources = [],
  className,
}: SourcePanelProps) {
  const [expanded, setExpanded] = useState<Set<number>>(new Set());

  const toggle = (n: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(n)) next.delete(n);
      else next.add(n);
      return next;
    });
  };

  if (sources.length === 0 && imageSources.length === 0) return null;

  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card/50 overflow-hidden",
        className
      )}
    >
      <div className="px-3 py-2 border-b border-border flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground">Sources</h3>
        <span className="text-xs text-muted-foreground">
          {sources.length + imageSources.length} total
        </span>
      </div>
      <div className="max-h-96 overflow-y-auto divide-y divide-border">
        {sources.map((s, idx) => {
          const num = s.sourceNumber ?? idx + 1;
          const domain = s.domain ?? extractDomain(s.url);
          const isExpanded = expanded.has(num);
          return (
            <div key={s.url} className="group">
              <div
                className="flex items-start gap-2 p-3 hover:bg-accent/50 transition-colors cursor-pointer"
                onClick={() => toggle(num)}
              >
                <button
                  type="button"
                  className="mt-0.5 text-muted-foreground hover:text-foreground"
                  aria-label={isExpanded ? "Collapse" : "Expand"}
                >
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </button>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-medium flex-shrink-0">
                      {num}
                    </span>
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm font-medium truncate hover:text-primary"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {s.title || s.url}
                    </a>
                    <TrustBadge domain={domain} />
                  </div>
                  <p className="text-xs text-muted-foreground mt-1 truncate">
                    {domain}
                  </p>
                  {isExpanded && s.snippet && (
                    <div className="mt-2 text-xs text-muted-foreground prose prose-sm dark:prose-invert max-w-none [&_p]:my-1">
                      <Markdown remarkPlugins={[remarkGfm]}>
                        {s.snippet}
                      </Markdown>
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 mt-2 text-primary hover:underline"
                        onClick={(e) => e.stopPropagation()}
                      >
                        Read more
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                  )}
                </div>
                <a
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex-shrink-0 p-1 rounded hover:bg-accent text-muted-foreground"
                  onClick={(e) => e.stopPropagation()}
                  aria-label="Open in new tab"
                >
                  <ExternalLink className="h-4 w-4" />
                </a>
              </div>
            </div>
          );
        })}
        {imageSources.map((img, idx) => (
          <div
            key={img.imgUrl}
            className="flex items-center gap-2 p-3 hover:bg-accent/50"
          >
            <span className="w-5 h-5 rounded-full bg-secondary text-secondary-foreground text-xs flex items-center justify-center font-medium">
              {img.sourceNumber ?? sources.length + idx + 1}
            </span>
            <a
              href={img.imgUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium truncate hover:text-primary flex-1"
            >
              {img.title}
            </a>
            <ExternalLink className="h-4 w-4 text-muted-foreground flex-shrink-0" />
          </div>
        ))}
      </div>
    </div>
  );
}
