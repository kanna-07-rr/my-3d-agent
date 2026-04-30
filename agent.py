import os, requests, json, re, time

# ==============================
# CONFIG
# ==============================
KEY = os.environ.get("OPENROUTER_API_KEY")
USER_PROMPT = os.environ.get("SITE_PROMPT", "A premium luxury 3D automotive showcase")

# ==============================
# CLEAN AI OUTPUT
# ==============================
def clean_code(content):
    if not content:
        return ""

    # Remove markdown blocks
    content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)

    # Extract JSON only
    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        return match.group(0)

    return content.strip()

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

            # DEBUG FULL RESPONSE
            print("🔎 API RAW RESPONSE:", data)

            if "choices" not in data:
                print("❌ API ERROR:", data)
                return ""

            content = data["choices"][0]["message"]["content"]
            return clean_code(content)

        except Exception as e:
            print(f"⚠️ Retry {attempt+1}: {e}")
            time.sleep(5)

    return ""

print(f"🚀 Building site for: {USER_PROMPT}")

# ==============================
# STEP 1: PLAN (STRICT JSON)
# ==============================
plan_sys = "You are a strict JSON generator. Output ONLY valid JSON."

plan_usr = f"""
Create a 3D website plan.

Return STRICT JSON ONLY like this:
{{
"name": "Luxury 3D Site",
"colors": {{"bg": "#000000", "accent": "#ffcc00"}},
"sections": [
{{"id": "hero", "title": "Hero Section", "3d_obj_desc": "Rotating futuristic car"}},
{{"id": "about", "title": "About", "3d_obj_desc": "Floating glass panels"}}
]
}}

Topic: {USER_PROMPT}
"""

plan_raw = call_ai(plan_sys, plan_usr)

print("🧠 PLAN RAW OUTPUT:\n", plan_raw)

if not plan_raw:
    raise Exception("❌ AI returned empty plan")

try:
    plan = json.loads(plan_raw)
except Exception as e:
    print("❌ INVALID JSON:\n", plan_raw)
    raise e

# ==============================
# STEP 2: CSS
# ==============================
css = call_ai(
    "You are an elite UI designer. Output ONLY CSS.",
    f"Create premium CSS using colors {plan['colors']} with glassmorphism and luxury fonts."
)

# ==============================
# STEP 3: JS (THREE + GSAP)
# ==============================
js = call_ai(
    "You are a Three.js expert. Output ONLY JavaScript.",
    f"""
Create 3D scenes for sections: {[s['id'] for s in plan['sections']]}.

Requirements:
- Use Three.js
- Each section has its own canvas: canvas_ID
- Use MeshPhysicalMaterial
- Add rotation animation
- Use GSAP ScrollTrigger
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

    <div style="
        position:relative;
        z-index:10;
        text-align:center;
        padding-top:20%;
        color:white;
    ">
        <h1>{s['title']}</h1>
        <p>{s['3d_obj_desc']}</p>
    </div>
</section>
"""

# ==============================
# FINAL HTML
# ==============================
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{plan['name']}</title>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>

<style>
body {{
    margin: 0;
    background: {plan['colors']['bg']};
    color: white;
    font-family: Arial, sans-serif;
    overflow-x: hidden;
}}

section {{
    display:flex;
    justify-content:center;
    align-items:center;
}}

{css}
</style>
</head>

<body>

<nav style="
position:fixed;
top:0;
width:100%;
padding:20px;
text-align:center;
z-index:100;
font-weight:bold;
">
{plan['name']}
</nav>

{sections_html}

<script>
gsap.registerPlugin(ScrollTrigger);
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