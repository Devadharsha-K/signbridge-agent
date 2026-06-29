import sys
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server for SignBridge Accessibility tools
mcp = FastMCP("SignBridge-MCP-Tools")

# Mock database of ASL Gloss terms and handshapes
ASL_DICTIONARY = {
    "hello": {"gloss": "HELLO", "handshape": "B-hand near temple", "movement": "Salute move outward", "location": "Head/Temple"},
    "thank you": {"gloss": "THANK-YOU", "handshape": "Flat hand on chin", "movement": "Move outward toward person", "location": "Chin"},
    "help": {"gloss": "HELP", "handshape": "A-hand on flat palm", "movement": "Lift upward together", "location": "Neutral space"},
    "learn": {"gloss": "LEARN", "handshape": "Flat hand grabbing from palm to forehead", "movement": "Pull up to forehead", "location": "Palm to Head"},
    "sign": {"gloss": "SIGN-LANGUAGE", "handshape": "1-hands (index fingers)", "movement": "Alternating backward circles", "location": "Chest level"},
    "doctor": {"gloss": "DOCTOR", "handshape": "M-hand or D-hand tapping wrist", "movement": "Tap pulse point twice", "location": "Wrist"},
    "emergency": {"gloss": "EMERGENCY", "handshape": "E-hand shaking", "movement": "Shake side to side fast", "location": "Neutral space"},
}

@mcp.tool()
def dictionary_lookup(term: str) -> str:
    """Look up sign language gloss, handshape, movement, and physical location for a specific English word or phrase."""
    clean_term = term.lower().strip()
    if clean_term in ASL_DICTIONARY:
        data = ASL_DICTIONARY[clean_term]
        return (
            f"Term: '{term}'\n"
            f"ASL Gloss: {data['gloss']}\n"
            f"Handshape: {data['handshape']}\n"
            f"Movement: {data['movement']}\n"
            f"Location: {data['location']}"
        )
    
    # Fallback/Fingerspelling recommendation
    letters = "-".join(list(clean_term.upper()))
    return f"Term: '{term}' not found in core lexicon. Recommended fallback: Fingerspell ({letters})."

@mcp.tool()
def grammar_checker(gloss_text: str) -> str:
    """Validate ASL syntax structure (Topic-Comment order, Time indicators, facial expression markers)."""
    text = gloss_text.upper()
    feedback = []
    
    # Check Time-Topic-Comment structure
    time_words = ["YESTERDAY", "TODAY", "TOMORROW", "FUTURE", "PAST", "NOW", "MORNING", "NIGHT"]
    has_time = any(tw in text for tw in time_words)
    
    if has_time and not any(text.startswith(tw) for tw in time_words):
        feedback.append("Suggestion: Move time indicators (e.g. YESTERDAY/TODAY) to the beginning of the ASL sentence.")
    
    if "?" in gloss_text or "WH" in text or "WHO" in text or "WHAT" in text or "WHERE" in text:
        feedback.append("Facial Marker required: Furrowed brows (wh-question) or raised brows (yes/no question). Put WH-words at the end of the sentence.")
    
    if not feedback:
        feedback.append("ASL Gloss structure conforms well to Topic-Comment standards.")
        
    return f"ASL Syntax Verification for [{gloss_text}]:\n" + "\n".join(f"- {f}" for f in feedback)

@mcp.tool()
def accessibility_formatter(text: str, mode: str = "visual_caption") -> str:
    """Format translation output for accessible display devices (e.g., visual_caption, high_contrast, tactical_haptic)."""
    mode = mode.lower()
    if mode == "high_contrast":
        return f"[HIGH CONTRAST BOLD YELLOW-ON-BLACK]\n>>> {text.upper()} <<<"
    elif mode == "tactical_haptic":
        # Simulating tactile braille / haptic pulses
        return f"[HAPTIC PULSE PATTERN ENCODED]\n{text}"
    else:
        # Default visual caption
        return f"📺 [ACCESSIBLE CAPTION]: {text}"

@mcp.tool()
def sign_phrase_builder(english_phrase: str) -> str:
    """Convert an English spoken sentence into candidate ASL Gloss tokens with syntax annotations."""
    words = english_phrase.lower().replace(".", "").replace("?", "").replace(",", "").split()
    gloss_list = []
    for w in words:
        if w in ["a", "an", "the", "is", "are", "am", "to", "of"]:
            continue  # Omit English articles and auxiliary verbs not present in ASL
        if w in ASL_DICTIONARY:
            gloss_list.append(ASL_DICTIONARY[w]["gloss"])
        else:
            gloss_list.append(w.upper())
    
    candidate_gloss = " ".join(gloss_list)
    return f"Input English: '{english_phrase}'\nCandidate ASL Gloss Sequence: {candidate_gloss} (Note: Adjust for Topic-Comment structure)."

if __name__ == "__main__":
    mcp.run()
