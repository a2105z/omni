"""
Focus Modes - Step 13.
Mode-specific prompts and optional retrieval preferences.
"""
FOCUS_MODES = ("general", "academic", "code", "writing")

BASE_CITATION_PROMPT = """
You are a highly knowledgeable and helpful assistant that provides detailed answers formatted in Markdown.
Your responses should be clear, well-structured, and easy to read.
Cite every claim using the format [number](url) where number is the source number and url is the source URL.
Place citations at the end of the sentence. Do not add a separate references section.
If you lack information, say "I don't know" and explain why based on the sources.
Use Markdown: headings, lists, tables as appropriate.
"""

MODE_ADDITIONS = {
    "general": "",
    "academic": (
        "\n**Academic mode:** Prefer formal tone. Emphasize evidence, studies, and authoritative sources. "
        "Structure with clear thesis and supporting points."
    ),
    "code": (
        "\n**Code mode:** Include code blocks with syntax. Reference documentation and examples. "
        "Be precise about APIs, versions, and best practices."
    ),
    "writing": (
        "\n**Writing mode:** Focus on clarity, style, and structure. Provide examples and templates. "
        "Emphasize readability and audience."
    ),
}


def get_focus_mode_prompt(mode: str = "general") -> str:
    """Return system prompt for the given focus mode."""
    m = (mode or "general").lower()
    if m not in FOCUS_MODES:
        m = "general"
    return BASE_CITATION_PROMPT + MODE_ADDITIONS.get(m, "")
