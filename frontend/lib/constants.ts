/** Focus modes for search - aligned with backend */
export const FOCUS_MODES = [
  { id: "general", label: "General", icon: "🔍" },
  { id: "academic", label: "Academic", icon: "📚" },
  { id: "code", label: "Code", icon: "💻" },
  { id: "writing", label: "Writing", icon: "✍️" },
] as const;

/** Suggested prompts for empty state */
export const SUGGESTED_PROMPTS = [
  "What is quantum computing and how does it work?",
  "Explain React Server Components in simple terms",
  "Best practices for REST API design in 2024",
  "How does machine learning differ from deep learning?",
  "Compare Next.js vs Remix for full-stack apps",
  "What are the main causes of climate change?",
  "How to implement authentication with JWT?",
];
