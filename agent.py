import os, requests, json

GEMINI_KEY = os.environ["GEMINI_API_KEY"]
PROMPT = os.environ.get("SITE_PROMPT", "Build a 3D rotating cube website")

SYSTEM = """You are a 3D web developer. Output ONLY a single complete
HTML file. Use Three.js from CDN. The site must be visually
stunning and interactive. No markdown, no explanation —
just raw HTML starting with <!DOCTYPE html>."""

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

payload = {
    "contents": [{"parts": [{"text": f"{SYSTEM}\n\nUSER REQUEST: {PROMPT}"}]}],
    "generationConfig": {"maxOutputTokens": 8192, "temperature": 0.7}
}

res = requests.post(
    f"{url}?key={GEMINI_KEY}",
    json=payload,
    headers={"Content-Type": "application/json"}
)

# Print full response so we can debug
print("STATUS CODE:", res.status_code)
print("RESPONSE:", json.dumps(res.json(), indent=2))

response_json = res.json()

if "candidates" not in response_json:
    print("❌ API ERROR - Key might be wrong or quota exceeded")
    exit(1)

html = response_json["candidates"][0]["content"]["parts"][0]["text"]

if html.startswith("```"):
    html = html.split("\n", 1)[1].rsplit("```", 1)[0]

with open("index.html", "w") as f:
    f.write(html)

print("✅ Done! index.html generated.")