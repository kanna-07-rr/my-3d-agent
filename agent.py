import os, requests, json

KEY = os.environ["OPENROUTER_API_KEY"]
PROMPT = os.environ.get("SITE_PROMPT", "Build a 3D rotating cube website")

SYSTEM = """You are a 3D web developer. Output ONLY a single complete
HTML file. Use Three.js from CDN. Make it visually stunning.
No markdown, no explanation — just raw HTML starting with <!DOCTYPE html>."""

res = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {KEY}",
        "Content-Type": "application/json"
    },
    json={
        "model": "meta-llama/llama-3.3-8b-instruct:free",
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": PROMPT}
        ]
    }
)

print("STATUS:", res.status_code)
response_json = res.json()
print("RESPONSE:", json.dumps(response_json, indent=2))

html = response_json["choices"][0]["message"]["content"]

if html.startswith("```"):
    html = html.split("\n", 1)[1].rsplit("```", 1)[0]

with open("index.html", "w") as f:
    f.write(html)

print("✅ Done!")