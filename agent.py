import os, requests, json, time

# ==============================
# CONFIG
# ==============================
KEY = os.environ.get("OPENROUTER_API_KEY")
USER_PROMPT = os.environ.get("SITE_PROMPT", "A premium luxury 3D automotive showcase")

if not KEY:
    raise Exception("❌ Missing OPENROUTER_API_KEY")

# ==============================
# CLEAN AI OUTPUT (FIXED)
# ==============================
def clean_code(content):
    if not content:
        return ""

    # Remove markdown wrappers but KEEP content
    content = content.replace("```json", "").replace("```", "").strip()
    return content

# ==============================
# AI CALL FUNCTION
# ==============================
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

            # DEBUG (important)
            print("🔎 API RESPONSE:", data)

            if "choices" not in data:
                print("❌ API ERROR:", data)
                time.sleep(3)
                continue

            content = data["choices"][0]["message"]["content"]
            return clean_code(content)

        except Exception as e:
            print(f"⚠️ Retry {attempt+1}: {e}")
            time.sleep(5)

    return ""

print(f"🚀 Building site for: {USER_PROMPT}")

# ==============================
# STEP 1: PLAN
# ==============================
plan_sys = "You are a strict JSON generator. Output ONLY valid JSON. No explanation."

plan_usr = f"""
Create a 3D website plan.

Return ONLY JSON:
{{
"name": "Luxury 3D Site",
"colors": {{"bg": "#0a0a0a", "accent": "#ffcc00"}},
"sections": [
{{"id": "hero", "title": "Hero Section", "3d_obj_desc": "Rotating futuristic object"}},
{{"id": "about", "title": "About", "3d_obj_desc": "Floating glass panels"}}
]
}}

Topic: {USER_PROMPT}
"""

plan_raw = call_ai(plan_sys, plan_usr)

print("🧠 PLAN RAW:\n", plan_raw)

# Fallback if AI fails
if not plan_raw:
    print("⚠️ Using fallback plan")
    plan = {
        "name": "Fallback 3D Site",
        "colors": {"bg": "#000000", "accent": "#00ffcc"},
        "sections": [
            {"id": "hero", "title": "Hero", "3d_obj_desc": "Rotating cube"},
            {"id": "about", "title": "About", "3d_obj_desc": "Floating shapes"}
        ]
    }
else:
    try:
        plan = json.loads(plan_raw)
    except Exception as e:
        print("❌ JSON ERROR, using fallback")
        plan = {
            "name": "Safe Mode Site",
            "colors": {"bg": "#000000", "accent": "#ff0000"},
            "sections": [
                {"id": "hero", "title": "Hero", "3d_obj_desc": "Basic 3D object"}
            ]
        }

# ==============================
# STEP 2: CSS
# ==============================
css = call_ai(
    "You are an elite UI designer. Output ONLY CSS.",
    f"Create premium dark theme CSS using colors {plan['colors']}."
)

# ==============================
# STEP 3: JS
# ==============================
js = call_ai(
    "You are a Three.js expert. Output ONLY JavaScript.",
    f"""
Create simple 3D scenes for sections: {[s['id'] for s in plan['sections']]}.

Requirements:
- Use Three.js
- Create rotating cube/sphere
- Each section uses canvas canvas_ID
"""
)

# ==============================
# STEP 4: HTML BUILD
# ==============================
sections_html = ""

for s in plan['sections']:
    sections_html += f"""
<section id="{s['id']}" style="height:100vh;position:relative;">
    <canvas id="canvas_{s['id']}" style="position:absolute;width:100%;height:100%;"></canvas>

    <div style="position:relative;z-index:10;text-align:center;color:white;padding-top:20%;">
        <h1>{s['title']}</h1>
        <p>{s['3d_obj_desc']}</p>
    </div>
</section>
"""

html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{plan['name']}</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<style>
body {{
    margin:0;
    background:{plan['colors']['bg']};
    color:white;
    font-family:Arial;
}}

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

# ==============================
# SAVE FILE
# ==============================
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("✅ SUCCESS: index.html generated!")