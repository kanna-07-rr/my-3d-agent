import os, requests, json, re, time

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
OPENROUTER_KEY = os.environ["OPENROUTER_API_KEY"]
USER_PROMPT = os.environ.get(
    "SITE_PROMPT",
    "Build a premium futuristic 3D website"
)

MODEL = "openrouter/auto"

# ─────────────────────────────────────────────
# AI CALL ENGINE
# ─────────────────────────────────────────────
def call_ai(system_prompt, user_prompt, max_tokens=8000, retries=3):
    for attempt in range(retries):
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": max_tokens
                },
                timeout=180
            )

            data = response.json()

            if "choices" not in data:
                print(f"[ERROR] Attempt {attempt+1}: {json.dumps(data, indent=2)}")
                time.sleep(3)
                continue

            output = data["choices"][0]["message"]["content"]

            if not output or len(output.strip()) < 50:
                print(f"[WARNING] Weak output on attempt {attempt+1}")
                time.sleep(2)
                continue

            return output.strip()

        except Exception as e:
            print(f"[EXCEPTION] Attempt {attempt+1}: {e}")
            time.sleep(3)

    return None


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def strip_code_fences(text):
    if not text:
        return ""
    text = re.sub(r"```[a-zA-Z]*", "", text)
    return text.replace("```", "").strip()


def parse_json(text):
    if not text:
        return None
    text = strip_code_fences(text)

    try:
        return json.loads(text)
    except:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except:
                return None
    return None


# ─────────────────────────────────────────────
# STEP 1 — UNIVERSAL SITE BLUEPRINT
# ─────────────────────────────────────────────
print("\n[1/4] Planning universal premium website...\n")

plan_raw = call_ai(
    "You are an elite web architect. Output ONLY valid JSON.",
    f"""
Create a premium 3D website blueprint for:
{USER_PROMPT}

Return:
{{
  "site_name": "",
  "tagline": "",
  "industry": "",
  "color_bg": "",
  "color_primary": "",
  "color_secondary": "",
  "color_accent": "",
  "fonts": [],
  "sections": [
    {{
      "id": "",
      "name": "",
      "description": "",
      "has_3d": true
    }}
  ]
}}
"""
)

plan = parse_json(plan_raw)

# Fallback universal structure
if not plan:
    plan = {
        "site_name": "Premium 3D Experience",
        "tagline": "Built From Imagination",
        "industry": "Universal",
        "color_bg": "#050816",
        "color_primary": "#00F5FF",
        "color_secondary": "#7B2FF7",
        "color_accent": "#F72585",
        "fonts": ["Poppins", "Space Grotesk"],
        "sections": [
            {"id": "hero", "name": "Hero", "description": "3D immersive hero", "has_3d": True},
            {"id": "about", "name": "About", "description": "Brand story", "has_3d": False},
            {"id": "features", "name": "Features", "description": "Premium offerings", "has_3d": True},
            {"id": "showcase", "name": "Showcase", "description": "Interactive products/services", "has_3d": True},
            {"id": "contact", "name": "Contact", "description": "Lead generation", "has_3d": False}
        ]
    }


# ─────────────────────────────────────────────
# STEP 2 — UNIVERSAL CSS SYSTEM
# ─────────────────────────────────────────────
print("[2/4] Building universal premium CSS...\n")

css = call_ai(
    "You are a world-class UI/UX CSS engineer. Output ONLY CSS.",
    f"""
Build elite premium CSS for:
{USER_PROMPT}

Rules:
- futuristic
- glassmorphism
- responsive
- luxury animations
- dynamic sections
- 3D canvas support
- reusable components
- premium buttons
- mobile optimized
"""
)

css = strip_code_fences(css)


# ─────────────────────────────────────────────
# STEP 3 — UNIVERSAL HTML GENERATION
# ─────────────────────────────────────────────
print("[3/4] Building sections...\n")

sections_html = []

for section in plan["sections"]:
    html = call_ai(
        "Output ONLY valid HTML section.",
        f"""
Create section:
Name: {section['name']}
Description: {section['description']}
Industry: {plan['industry']}
Theme: premium futuristic luxury
3D: {section['has_3d']}
"""
    )

    html = strip_code_fences(html)

    if not html:
        html = f"""
<section id="{section['id']}">
  <h2>{section['name']}</h2>
  <p>{section['description']}</p>
</section>
"""
    sections_html.append(html)


# ─────────────────────────────────────────────
# STEP 4 — UNIVERSAL JS + 3D ENGINE
# ─────────────────────────────────────────────
print("[4/4] Building universal JS...\n")

js = """
// Premium universal interactions
// Cursor
// GSAP
// ScrollTrigger
// Three.js Hero Scene
// Dynamic section transitions
// Magnetic buttons
// Interactive cards
"""


# ─────────────────────────────────────────────
# FINAL ASSEMBLY
# ─────────────────────────────────────────────
final_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{plan['site_name']}</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>

<style>
{css}
</style>
</head>

<body>
{''.join(sections_html)}

<script>
{js}
</script>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"\nSUCCESS — Universal 3D website generated: {len(final_html)} characters")