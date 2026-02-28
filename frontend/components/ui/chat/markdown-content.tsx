"use client";

import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/cjs/styles/prism";
import { HoverCard, HoverCardContent, HoverCardTrigger } from "../hover-card";
import { cn } from "@/lib/utils";
import "katex/dist/katex.min.css";

/** Source for citation hover - url -> { title, snippet, domain } */
export interface CitationSource {
  url: string;
  title: string;
  snippet?: string;
  domain?: string;
}

/** Parse [1](url) citations to map number -> source */
function parseCitationSources(sources: CitationSource[]): Map<number, CitationSource> {
  const m = new Map<number, CitationSource>();
  sources.forEach((s, i) => m.set(i + 1, s));
  return m;
}

interface MarkdownContentProps {
  content: string;
  sources?: CitationSource[];
  className?: string;
}

export function MarkdownContent({
  content,
  sources = [],
  className,
}: MarkdownContentProps) {
  const citationMap = parseCitationSources(sources);

  return (
    <div
      className={cn(
        "prose dark:prose-invert max-w-none",
        "[&>*]:my-5 [&_p]:leading-relaxed [&_p:not(:last-child)]:mb-2",
        "[&_a]:inline-flex [&_a]:items-center [&_a]:gap-1 [&_a]:rounded [&_a]:bg-secondary [&_a]:px-1 [&_a]:py-0.5 [&_a]:border [&_a]:border-border [&_a]:text-sm [&_a]:text-primary [&_a]:font-semibold [&_a]:no-underline [&_a]:transition-colors hover:[&_a]:bg-card/80 [&_a]:mx-0.5 [&_a]:cursor-pointer",
        " [&_pre]:!bg-muted [&_pre]:!rounded-lg [&_pre]:!p-4 [&_pre]:!overflow-x-auto",
        "[&_code]:!bg-muted [&_code]:!px-1 [&_code]:!py-0.5 [&_code]:!rounded [&_code]:!text-sm",
        " [&_pre_code]:!bg-transparent [&_pre_code]:!p-0",
        className
      )}
    >
      <Markdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          a: ({ href, children }) => {
            if (!href) return <a href="#">{children}</a>;
            const num = parseInt(String(children), 10);
            const isCitation = !Number.isNaN(num) && citationMap.has(num);
            const source = isCitation ? citationMap.get(num) : null;
            if (source) {
              return (
                <HoverCard openDelay={200}>
                  <HoverCardTrigger asChild>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 rounded bg-secondary px-1 py-0.5 border border-border text-sm text-primary font-semibold no-underline transition-colors hover:bg-card/80 mx-0.5 cursor-pointer"
                    >
                      [{children}]
                    </a>
                  </HoverCardTrigger>
                  <HoverCardContent className="w-80 max-h-64 overflow-y-auto">
                    <div className="space-y-2">
                      <p className="text-sm font-medium line-clamp-2">
                        {source.title}
                      </p>
                      {source.domain && (
                        <span className="text-xs text-muted-foreground">
                          {source.domain}
                        </span>
                      )}
                      {source.snippet && (
                        <p className="text-xs text-muted-foreground line-clamp-3">
                          {source.snippet}
                        </p>
                      )}
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline"
                      >
                        Read more →
                      </a>
                    </div>
                  </HoverCardContent>
                </HoverCard>
              );
            }
            return (
              <a href={href} target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            );
          },
          code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || "");
            if (match) {
              return (
                <SyntaxHighlighter
                  style={oneDark}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    margin: "1em 0",
                    borderRadius: "0.5rem",
                    fontSize: "0.875rem",
                  }}
                  codeTagProps={{ style: {} }}
                >
                  {String(children).replace(/\n$/, "")}
                </SyntaxHighlighter>
              );
            }
            return (
              <code className={cn("bg-muted px-1 py-0.5 rounded text-sm", className)} {...props}>
                {children}
              </code>
            );
          },
          p: ({ children }) => (
            <div className="my-4 leading-relaxed">{children}</div>
          ),
        }}
      >
        {content}
      </Markdown>
    </div>
  );
}
