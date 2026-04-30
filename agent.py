import os, requests, json, re

KEY = os.environ["OPENROUTER_API_KEY"]
USER_PROMPT = os.environ.get("SITE_PROMPT", "Build a 3D rotating cube website")

def call_ai(system, user, max_tokens=8000):
    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.7
        },
        timeout=180
    )
    data = res.json()
    if "choices" not in data:
        print("API ERROR:", json.dumps(data, indent=2))
        exit(1)
    return data["choices"][0]["message"]["content"]

print("=" * 50)
print("3D SITE AGENT — MULTI STEP BUILD")
print("=" * 50)

plan_raw = call_ai(
    "You are a web architect. Output ONLY raw JSON. No markdown. No explanation.",
    f"""Plan this website: {USER_PROMPT}

Output this exact JSON:
{{
  "site_name": "site name",
  "color_bg": "#0a0a0a",
  "color_primary": "#FFD700",
  "color_secondary": "#ff6b35",
  "fonts": ["Playfair Display", "Inter"],
  "sections": [
    {{
      "id": "hero",
      "name": "Hero Section",
      "description": "description",
      "has_3d": true
    }}
  ]
}}""",
    max_tokens=1500
)

if "```" in plan_raw:
    plan_raw = plan_raw.split("```")[1].split("```")[0]
    plan_raw = plan_raw.replace("json", "", 1).strip()

try:
    plan = json.loads(plan_raw)
    print(f"Site: {plan['site_name']}")
    print(f"Sections: {len(plan['sections'])}")
except:
    print("Plan failed — using fallback")
    plan = {
        "site_name": "3D Website",
        "color_bg": "#0a0a0a",
        "color_primary": "#FFD700",
        "color_secondary": "#ff6b35",
        "fonts": ["Playfair Display", "Inter"],
        "sections": [
            {"id": "hero", "name": "Hero", "description": USER_PROMPT, "has_3d": True},
            {"id": "about", "name": "About", "description": "About section", "has_3d": False},
            {"id": "menu", "name": "Menu", "description": "Menu section", "has_3d": False},
            {"id": "booking", "name": "Booking", "description": "Booking form", "has_3d": False}
        ]
    }

print("\n[2/4] Building CSS...")
css = call_ai(
    "You are a CSS expert. Output ONLY raw CSS. No markdown. No explanation.",
    f"""Write complete premium CSS for {plan['site_name']}.
Colors: bg={plan['color_bg']}, primary={plan['color_primary']}, secondary={plan['color_secondary']}
Fonts: {', '.join(plan['fonts'])}
Sections: {', '.join([s['id'] for s in plan['sections']])}
Include: Google Fonts import, CSS variables, reset, typography, glassmorphism, buttons, layouts, animations, mobile responsive, scrollbar, cursor glow""",
    max_tokens=4000
)
css = re.sub(r'```css|```', '', css).strip()
print(f"CSS: {len(css)} chars")

print("\n[3/4] Building sections...")
sections_html = []
for section in plan['sections']:
    print(f"  Building {section['name']}...")
    html = call_ai(
        "Output ONLY the HTML for this section. No DOCTYPE, no html, no head, no body tags. Just the section and its contents.",
        f"""Build "{section['name']}" section for {plan['site_name']}.
Description: {section['description']}
Section id="{section['id']}"
Colors: bg={plan['color_bg']}, primary={plan['color_primary']}
{'Three.js is already loaded — use it for 3D' if section.get('has_3d') else 'Use CSS animations only'}
GSAP already loaded. Make it premium and stunning.""",
        max_tokens=4000
    )
    html = re.sub(r'```html|```', '', html).strip()
    sections_html.append(html)
    print(f"    {len(html)} chars")

print("\n[4/4] Building JavaScript...")
js = call_ai(
    "Output ONLY raw JavaScript. No markdown. No explanation.",
    f"""Write main JavaScript for {plan['site_name']}.
Sections: {', '.join([s['name'] for s in plan['sections']])}
3D sections: {', '.join([s['name'] for s in plan['sections'] if s.get('has_3d')])}
Colors: primary={plan['color_primary']}, bg={plan['color_bg']}
Brief: {USER_PROMPT[:300]}
Libraries loaded: Three.js r128, GSAP 3.12.2, ScrollTrigger
Write: Three.js scenes, GSAP animations, magnetic buttons, cursor glow, smooth scroll, mobile fallback""",
    max_tokens=8000
)
js = re.sub(r'```javascript|```js|```', '', js).strip()
print(f"JS: {len(js)} chars")

print("\nCombining...")
fonts_url = "+".join([f.replace(" ", "+") for f in plan['fonts']])

final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan['site_name']}</title>
    <link href="https://fonts.googleapis.com/css2?family={fonts_url}:wght@300;400;600;700;900&display=swap" rel="stylesheet">
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
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

size = len(final_html)
print(f"\n{'='*50}")
print(f"SUCCESS! {size:,} chars ({size//1024} KB)")
print(f"Sections: {len(sections_html)}")
print(f"{'='*50}")