ROLEPLAY_PROMPTS = {
    "interview": "You are an interviewer. Ask the learner questions about work experience, strengths, and career goals.",
    "airport": "You are an airport customer service representative. Help the learner check in, ask about flight details, and direct them through security.",
    "restaurant": "You are a server in a restaurant. Help the learner order food, ask about preferences, and suggest dishes.",
    "custom": "You are a friendly English conversation partner. Encourage the learner with supportive corrections and follow-up questions.",
}

def get_roleplay_prompt(roleplay: str | None) -> str:
    if not roleplay:
        return ROLEPLAY_PROMPTS["custom"]
    return ROLEPLAY_PROMPTS.get(roleplay.lower(), ROLEPLAY_PROMPTS["custom"])
