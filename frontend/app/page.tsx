"use client";

import { Button } from "@/components/ui/button";
import { useChat } from "@/lib/chat/chat-context";
import {
  Send,
  X,
  Pencil,
  Menu,
  PenSquare,
  Check,
  Moon,
  Sun,
  Download,
} from "lucide-react";
import { useState, useRef, useEffect, useCallback } from "react";
import TextareaAutosize from "react-textarea-autosize";
import { AiResponseView } from "@/components/ui/chat/ai-response-view";
import { cn } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { FocusModeSelector } from "@/components/ui/focus-mode-selector";
import { useTheme } from "@/components/ui/theme-provider";
import { SUGGESTED_PROMPTS } from "@/lib/constants";

export default function Home() {
  const {
    currentMessages: messages,
    setCurrentMessages: setMessages,
    generateAssistantResponse,
    regenerateResponse,
    currentSessionTitle,
    sessions,
    setCurrentSessionId,
    currentSessionId,
    setCurrentSessionTitle,
    createNewSession,
    focusMode,
    setFocusMode,
    exportSession,
  } = useChat();

  const { theme, setTheme, resolvedTheme } = useTheme();

  const [isGenerating, setIsGenerating] = useState(false);
  const [input, setInput] = useState("");
  const abortControllerRef = useRef<AbortController | null>(null);
  const [editingMessageIndex, setEditingMessageIndex] = useState<number | null>(
    null
  );
  const [editingMessageContent, setEditingMessageContent] = useState("");
  const [activeMessageIndex, setActiveMessageIndex] = useState<number>(
    messages.length - 1
  );
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [editedTitle, setEditedTitle] = useState("");

  useEffect(() => {
    setInput("");
  }, [currentSessionId]);

  useEffect(() => {
    setActiveMessageIndex(messages.length - 1);
  }, [messages.length]);

  const cancelGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsGenerating(false);
    }
  };

  const handleSubmit = useCallback(
    async (query: string) => {
      cancelGeneration();
      abortControllerRef.current = new AbortController();
      const signal = abortControllerRef.current.signal;
      try {
        setIsGenerating(true);
        await generateAssistantResponse(query, signal, { focusMode });
      } catch {
        // Abort or error handled in context
      } finally {
        setIsGenerating(false);
        abortControllerRef.current = null;
      }
    },
    [focusMode, generateAssistantResponse]
  );

  const handleRegenerate = useCallback(
    async (idx: number) => {
      cancelGeneration();
      abortControllerRef.current = new AbortController();
      const signal = abortControllerRef.current.signal;
      try {
        setIsGenerating(true);
        await regenerateResponse(idx, signal);
      } catch {
        // Abort handled
      } finally {
        setIsGenerating(false);
        abortControllerRef.current = null;
      }
    },
    [regenerateResponse]
  );

  const handleEditMessage = (index: number, newContent: string) => {
    cancelGeneration();
    setMessages(messages.slice(0, index));
    setEditingMessageIndex(null);
    setEditingMessageContent("");
    handleSubmit(newContent);
  };

  const scrollToMessage = (index: number) => {
    const target = document.querySelector(`[data-message-index="${index}"]`);
    target?.scrollIntoView({ behavior: "smooth" });
    setActiveMessageIndex(index);
  };

  const handleKeyPress = (
    e: React.KeyboardEvent<HTMLTextAreaElement>,
    action: () => void,
    content: string
  ) => {
    if (e.key === "Enter" && !e.shiftKey && content.trim().length > 0) {
      e.preventDefault();
      action();
    }
  };

  const handleTitleEdit = () => {
    if (editedTitle.trim()) {
      setCurrentSessionTitle(editedTitle.trim());
      setIsEditingTitle(false);
    }
  };

  const handleExport = () => {
    const text = exportSession(currentSessionId);
    if (!text) return;
    const blob = new Blob([text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentSessionTitle.replace(/[^a-z0-9]/gi, "_")}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "k") {
        e.preventDefault();
        createNewSession(true);
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [createNewSession]);

  return (
    <div className="flex flex-row h-screen bg-background">
      {/* Overlay */}
      <div
        className={cn(
          "fixed inset-0 bg-background/80 backdrop-blur-sm z-40 md:hidden",
          isSidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={() => setIsSidebarOpen(false)}
      />

      {/* Sidebar */}
      <div
        className={cn(
          "fixed md:relative h-full bg-card overflow-y-auto z-50",
          "transition-all duration-300 ease-in-out border-r border-border",
          isSidebarOpen
            ? "w-80 translate-x-0 p-4"
            : "w-0 -translate-x-full md:translate-x-0 md:w-72 p-4"
        )}
      >
        <div className="h-12" />

        {/* Session title */}
        <div className="flex items-center gap-2 mb-4">
          {isEditingTitle ? (
            <div className="flex w-full gap-2">
              <Input
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleTitleEdit();
                  else if (e.key === "Escape") setIsEditingTitle(false);
                }}
                autoFocus
                className="h-8"
              />
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsEditingTitle(false)}>
                <X className="h-4 w-4" />
              </Button>
              <Button variant="ghost" size="icon" className="h-8 w-8" onClick={handleTitleEdit}>
                <Check className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div className="flex w-full items-center min-w-0">
              <h2
                className="font-semibold text-lg cursor-pointer hover:text-muted-foreground flex-1 truncate text-primary"
                onClick={() => {
                  setEditedTitle(currentSessionTitle);
                  setIsEditingTitle(true);
                }}
              >
                {currentSessionTitle}
              </h2>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 flex-shrink-0"
                onClick={() => {
                  setEditedTitle(currentSessionTitle);
                  setIsEditingTitle(true);
                }}
              >
                <Pencil className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        {/* Export */}
        {messages.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            className="w-full gap-2 mb-4"
            onClick={handleExport}
          >
            <Download className="h-4 w-4" />
            Export
          </Button>
        )}

        {/* Message history */}
        {messages.length === 0 ? (
          <p className="text-muted-foreground text-sm">No questions yet</p>
        ) : (
          <div className="space-y-2 mb-8">
            {messages.map((message, idx) => (
              <Button
                key={idx}
                variant="outline"
                onClick={() => scrollToMessage(idx)}
                className={cn(
                  "w-full justify-start font-normal truncate text-left py-2",
                  activeMessageIndex === idx && "bg-accent"
                )}
              >
                <span className="truncate">{message.userMessage.content}</span>
              </Button>
            ))}
          </div>
        )}

        <div className="h-px bg-border my-4" />
        <h3 className="font-semibold mb-4">Sessions</h3>
        <div className="space-y-2">
          {[...sessions].reverse().map((session) => (
            <Button
              key={session.id}
              variant="outline"
              onClick={() => setCurrentSessionId(session.id)}
              className={cn(
                "w-full justify-start font-normal truncate text-left py-2",
                session.id === currentSessionId && "bg-accent"
              )}
            >
              <span className="truncate">{session.title}</span>
            </Button>
          ))}
        </div>
      </div>

      {/* Main area */}
      <div className="flex flex-col h-screen flex-1 relative">
        {/* Top bar */}
        <div className="absolute top-4 left-4 right-4 flex justify-between items-center z-50 gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="md:hidden"
          >
            <Menu className="h-4 w-4" />
          </Button>
          <div className="flex-1 flex justify-center">
            <FocusModeSelector value={focusMode} onChange={setFocusMode} />
          </div>
          <div className="flex gap-1">
            <Button
              variant="outline"
              size="icon"
              onClick={() =>
                setTheme(
                  theme === "system"
                    ? resolvedTheme === "dark"
                      ? "light"
                      : "dark"
                    : theme === "dark"
                      ? "light"
                      : "dark"
                )
              }
            >
              {resolvedTheme === "dark" ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={() => createNewSession(true)}
              title="New chat (⌘K)"
            >
              <PenSquare className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {!messages || messages.length === 0 ? (
          /* Empty state */
          <div className="flex flex-col flex-1 items-center justify-center p-4 sm:p-8">
            <div className="flex flex-col gap-8 items-center w-full max-w-2xl">
              <h1 className="text-4xl sm:text-5xl font-bold tracking-tighter">
                Omni
              </h1>
              <p className="text-muted-foreground text-center">
                Search the web and get AI-powered answers with citations.
              </p>
              <div className="w-full flex flex-col gap-4">
                <div className="flex flex-row gap-2 border-2 border-border bg-card rounded-lg w-full p-2">
                  <TextareaAutosize
                    className="w-full resize-none bg-transparent placeholder:text-muted-foreground focus:outline-none p-2 min-h-[52px]"
                    placeholder="Ask a question..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    maxRows={4}
                    minRows={2}
                    onKeyDown={(e) =>
                      handleKeyPress(
                        e,
                        () => {
                          if (input.trim()) {
                            const q = input.trim();
                            setInput("");
                            handleSubmit(q);
                          }
                        },
                        input
                      )
                    }
                  />
                  <div className="flex flex-col justify-end">
                    <Button
                      variant={
                        isGenerating || !input.trim() ? "secondary" : "default"
                      }
                      size="icon"
                      className="h-10 w-10"
                      onClick={() => {
                        if (isGenerating) cancelGeneration();
                        else if (input.trim()) {
                          const q = input.trim();
                          setInput("");
                          handleSubmit(q);
                        }
                      }}
                    >
                      {isGenerating ? <X className="h-4 w-4" /> : <Send className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2 justify-center">
                  {SUGGESTED_PROMPTS.map((prompt, i) => (
                    <Button
                      key={i}
                      variant="outline"
                      size="sm"
                      className="text-left font-normal h-auto py-2 px-3"
                      onClick={() => {
                        setInput(prompt);
                        handleSubmit(prompt);
                      }}
                    >
                      {prompt.length > 60 ? `${prompt.slice(0, 60)}...` : prompt}
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Chat */
          <div className="flex flex-col flex-1 min-h-0">
            <div className="flex-1 overflow-y-auto">
              <div className="flex flex-col px-4 sm:px-16 py-4 sm:py-8 pt-20 pb-0 w-full">
                <div className="w-full max-w-5xl mx-auto">
                  {messages.map((message, idx) => (
                    <div
                      key={idx}
                      data-message-index={idx}
                      className="flex flex-col w-full gap-8"
                    >
                      {editingMessageIndex === idx ? (
                        <div className="flex flex-row gap-2 border-2 border-border bg-card rounded-lg p-2 mt-8">
                          <TextareaAutosize
                            className="w-full resize-none bg-transparent focus:outline-none p-2"
                            value={editingMessageContent}
                            onChange={(e) =>
                              setEditingMessageContent(e.target.value)
                            }
                            onKeyDown={(e) =>
                              handleKeyPress(
                                e,
                                () =>
                                  handleEditMessage(idx, editingMessageContent),
                                editingMessageContent
                              )
                            }
                            maxRows={4}
                            minRows={1}
                          />
                          <div className="flex gap-2 justify-end">
                            <Button
                              variant="default"
                              size="icon"
                              onClick={() =>
                                handleEditMessage(idx, editingMessageContent)
                              }
                            >
                              <Send className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="secondary"
                              size="icon"
                              onClick={() => {
                                setEditingMessageIndex(null);
                                setEditingMessageContent("");
                              }}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div
                          className="group relative w-full cursor-pointer mt-8"
                          onClick={() => {
                            setEditingMessageIndex(idx);
                            setEditingMessageContent(
                              message.userMessage.content
                            );
                          }}
                        >
                          <p className="w-full font-semibold tracking-tight text-2xl sm:text-3xl text-primary pr-10">
                            {message.userMessage.content}
                          </p>
                          <div className="absolute right-0 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <Pencil className="h-5 w-5 text-muted-foreground" />
                          </div>
                        </div>
                      )}
                      <AiResponseView
                        assistantMessage={message.assistantMessage}
                        submitFollowUpSearchQueryCallback={(q) =>
                          handleSubmit(q)
                        }
                        onRegenerate={() => handleRegenerate(idx)}
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Input */}
            <div className="w-full p-4 sm:p-8 pt-4 flex flex-row items-end">
              <div className="flex flex-row gap-2 border-2 border-border bg-card rounded-lg w-full max-w-5xl mx-auto p-2">
                <TextareaAutosize
                  className="w-full resize-none bg-transparent placeholder:text-muted-foreground focus:outline-none p-2 min-h-[44px]"
                  placeholder="Ask a follow-up..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) =>
                    handleKeyPress(
                      e,
                      () => {
                        if (isGenerating) cancelGeneration();
                        else if (input.trim()) {
                          const q = input.trim();
                          setInput("");
                          handleSubmit(q);
                        }
                      },
                      input
                    )
                  }
                  maxRows={4}
                  minRows={1}
                />
                <div className="flex flex-col justify-end">
                  <Button
                    variant={
                      isGenerating || !input.trim() ? "secondary" : "default"
                    }
                    size="icon"
                    className="h-10 w-10"
                    onClick={() => {
                      if (isGenerating) cancelGeneration();
                      else if (input.trim()) {
                        const q = input.trim();
                        setInput("");
                        handleSubmit(q);
                      }
                    }}
                  >
                    {isGenerating ? (
                      <X className="h-4 w-4" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
