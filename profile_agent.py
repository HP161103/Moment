import json
import os
import textwrap
from datetime import datetime
from google import genai
from google.genai import types

from tools import (
    PROFILE_FILE,
    TOOL_LOG_FILE,
    _read_json_file,
    _write_json_file,
    _logged,
    get_user_interpretations,
    get_user_profile,
    save_user_profile,
    count_new_moments,
    extract_json,
    PROFILE_TOOLS,
)

# ── Config ────────────────────────────────────────────────────────────────────

_api_key = os.environ.get("GEMINI_API_KEY_MOMENT")
if not _api_key:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        _api_key = os.environ.get("GEMINI_API_KEY_MOMENT")
    except ImportError:
        pass

if not _api_key:
    raise EnvironmentError(
        "GEMINI_API_KEY_MOMENT is not set. Export it before importing this module."
    )

_gemini_client = genai.Client(api_key=_api_key)
_GEMINI_MODEL  = "gemini-2.5-flash"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_response_text(response) -> str | None:
    """
    Safely extract text from a Gemini response.
    Returns None if the model's final action was a tool call with no text,
    or if the response structure is unexpected.
    """
    try:
        return response.text
    except Exception:
        pass
    try:
        parts = response.candidates[0].content.parts
        texts = [p.text for p in parts if hasattr(p, "text") and p.text]
        return "\n".join(texts) if texts else None
    except Exception:
        return None

def _build_profile_prompt(user_id: str) -> tuple[str, str]:
    """
    Fetch the user's interpretations and fill in the system prompt template.
    Returns (filled_prompt, book_title) or raises ValueError if no moments found.
    """
    interpretations = get_user_interpretations(user_id)
    if not interpretations:
        raise ValueError(f"No interpretations found for user_id={user_id}")

    # pull metadata from the first moment — all moments share the same user/book
    first            = interpretations[0]
    character_name   = first.get("character_name", user_id)
    book_title       = first.get("book_title", first.get("book_id", "Unknown Book"))

    interpretations_text = "\n\n".join(
        f"[Passage {m.get('passage_number', '?')}]\n{m.get('cleaned_interpretation', '')}"
        for m in interpretations
    )

    filled = textwrap.dedent("""
        You are analysing how a reader engages with a book based on their written interpretations of passages.

        Reader: {character_name}
        Book: {book_title}

        Here are all their interpretations:
        {interpretations_text}

        Based ONLY on these interpretations, produce a reader portrait with exactly these 6 fields.
        Be specific and grounded — every claim must be evidenced by the actual text above.

        Return ONLY valid JSON, no explanation, no markdown, no backticks:

        {{
          "how_they_read": "one sentence: what level of text do they operate on — words/phrases, scene/atmosphere, character psychology, or theme/ideology",
          "interpretive_lens": "one sentence: what conceptual vocabulary do they use — psychological, philosophical, literary-critical, clinical, craft-focused, or personal-experiential",
          "central_preoccupation": "one sentence: the recurring question they ask of this book AND their position on it",
          "what_moves_them": "one sentence: the specific emotional content that produces their deepest responses",
          "emotional_mode": "one of: prosecutorial / empathetic-victim / empathetic-perpetrator / craft-observer — plus one sentence of evidence",
          "self_referential": "true or false — does this reader map the text to personal experience? Plus one sentence of evidence",
          "reflection_density": "low / medium / high — based on how many logical moves they make and whether they push past surface meaning"
        }}
    """).format(
        character_name=character_name,
        book_title=book_title,
        interpretations_text=interpretations_text,
    )

    return filled, book_title


# ── Profile Agent ─────────────────────────────────────────────────────────────

_PROFILE_REQUIRED_KEYS = {
    "how_they_read", "interpretive_lens", "central_preoccupation",
    "what_moves_them", "emotional_mode", "self_referential", "reflection_density"
}

def run_profile_agent(user_id: str) -> dict:
    """
    Build or incrementally update a reader portrait for user_id.
    Returns the portrait dict. On failure returns {"error": ..., "user_id": user_id}.
    """
    print(f"[ProfileAgent] running for user_id={user_id}")

    try:
        system_prompt, book_title = _build_profile_prompt(user_id)
    except ValueError as e:
        print(f"[ProfileAgent] {e}")
        return {"error": str(e), "user_id": user_id}

    chat = _gemini_client.chats.create(
        model=_GEMINI_MODEL,
        config=types.GenerateContentConfig(
            tools=PROFILE_TOOLS,
            temperature=0.2,
            system_instruction=system_prompt,
        )
    )

    response = chat.send_message(
        f"Build or update the portrait for user_id: {user_id}. "
        "Follow the workflow in your instructions exactly. "
        "Final output must be a raw JSON object."
    )

    portrait = extract_json(_get_response_text(response))

    if "error" in portrait:
        raw = _get_response_text(response) or ""
        print(f"[ProfileAgent] JSON extraction failed. raw={raw[:200]}")
        return {"error": "invalid JSON from Profile Agent",
                "raw": response.text, "user_id": user_id}

    missing = _PROFILE_REQUIRED_KEYS - portrait.keys()
    if missing:
        print(f"[ProfileAgent] incomplete portrait, missing keys: {missing}")
        return {"error": f"incomplete portrait, missing: {missing}",
                "raw": portrait, "user_id": user_id}

    portrait["user_id"]    = user_id
    portrait["book_title"] = book_title
    print(f"[ProfileAgent] portrait ready for user_id={user_id}")
    saved_message=save_user_profile(user_id,portrait)
    print(saved_message)
    return portrait


# ── Backwards compatibility aliases ──────────────────────────────────────────

run_profile_agent_v1 = run_profile_agent
run_profile_agent_v2 = run_profile_agent