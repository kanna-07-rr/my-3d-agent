import os, requests, json, re, time

KEY = os.environ.get("OPENROUTER_API_KEY")
USER_PROMPT = os.environ.get("SITE_PROMPT", "A premium luxury 3D automotive showcase")

def clean_code(content):
    # Remove markdown code blocks
    return re.sub(r"```.*?```", "", content, flags=re.DOTALL).strip()

def call_ai(system_prompt, user_message):
    for attempt in range(3):
        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openrouter/auto",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 4000,
                    "temperature": 0.7
                },
                timeout=120
            )

            data = res.json()
            content = data["choices"][0]["message"]["content"]
            return clean_code(content)

        except Exception as e:
            print(f"Retrying: {e}")
            time.sleep(5)

    return ""

print(f"🚀 Building site for: {USER_PROMPT}")

# STEP 1: PLAN
plan = json.loads(call_ai(
    "You are a Creative Director. Output ONLY JSON.",
    f"Plan a 3D website for: {USER_PROMPT}. Format: "
    "{'name':'','colors':{'bg':'','accent':''},"
    "'sections':[{'id':'hero','title':'','3d_obj_desc':''}]}"
))

# STEP 2: CSS
css = call_ai(
    "You are an elite UI designer. Output ONLY CSS.",
    f"Create premium CSS using {plan['colors']}"
)

# STEP 3: JS
js = call_ai(
    "You are a Three.js expert. Output ONLY JS.",
    f"Create 3D scenes for sections: {[s['id'] for s in plan['sections']]}"
)

# STEP 4: HTML BUILD
sections_html = ""
for s in plan['sections']:
    sections_html += f"""
    <section id="{s['id']}">
        <canvas id="canvas_{s['id']}"></canvas>
        <h1>{s['title']}</h1>
        <p>{s['3d_obj_desc']}</p>
    </section>
    """

html = f"""
<!DOCTYPE html>
<html>
<head>
<title>{plan['name']}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>

<style>
body {{ margin:0; background:{plan['colors']['bg']}; }}
{css}
</style>
</head>

<body>
{sections_html}

<script>
{js}
</script>
</body>
</html>
"""

with open("index.html", "w") as f:
    f.write(html)

print("✅ index.html generated!")