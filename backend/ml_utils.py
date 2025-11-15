import requests, os, json
from backend.utils.env_helpers import gemini_url

def call_llm_extract(article_text, title, url, published_at):
    url_api = gemini_url()  # returns None if not configured
    LLM_PROMPT_FROM_ABOVE = """You are an assistant that extracts crime incidents from a news article. \nInput: the article text and metadata (title, url, published_at).\nReturn a JSON object (only JSON; no extra commentary) with the key 'incidents': an array of objects. Each object must have:\n- description: short 1-2 sentence description of the event.\n- incident_date: ISO date (YYYY-MM-DD) or null.\n- incident_time: human time or null.\n- location_mentions: array of place names exactly as in text (strings).\n- approximate_coordinates: array of objects { 'lat': <float|null>, 'lng': <float|null>, 'confidence': 0-1, 'source': 'llm' } - model should attempt coordinates only if text explicitly mentions coordinates; otherwise leave nulls.\n- inferred_location: a single place name string (best inferred point) or null.\n- tags: array of short tags like ['assault','theft','robbery'].\n- severity: 'low'|'medium'|'high' based on described harm or keywords, or null.\nRules:\n- If multiple incidents are described, return them separately.\n- Only output valid JSON.\n- Be conservative: if you are not sure about coordinates, return null for lat/lng but provide location_mentions."""
    prompt = f"ARTICLE_TITLE: {title}\nARTICLE_URL: {url}\nPUBLISHED_AT: {published_at}\n\nARTICLE_TEXT:\n{article_text}\n\n---\n{LLM_PROMPT_FROM_ABOVE}"
    if not url_api:
        return None
    payload = {
        "contents":[{"parts":[{"text":prompt}]}],
        "generationConfig": {"maxOutputTokens": 1500, "temperature":0}
    }
    resp = requests.post(url_api, json=payload, headers={"Content-Type":"application/json"}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    # navigate to text output depending on provider:
    raw_text = data.get("candidates", [{}])[0].get("content", {}).get("parts",[{}])[0].get("text","")
    try:
        parsed = json.loads(raw_text)
    except Exception:
        # LLM sometimes adds code fences; try to extract JSON substring
        import re
        m = re.search(r'(\{[\s\S]*\})', raw_text)
        parsed = json.loads(m.group(1)) if m else None
    return {"raw_text": raw_text, "parsed": parsed, "raw_response": data}