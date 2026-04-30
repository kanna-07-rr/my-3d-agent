import os, requests, json, re

ANTHROPIC_KEY = os.environ["OPENROUTER_API_KEY"]
USER_PROMPT = os.environ.get("SITE_PROMPT", "Build a 3D rotating cube website")

def call_claude(system, user, max_tokens=8096):
    """Call Claude API and return response text"""
    res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        },
        json={
            "model": "claude-opus-4-5",
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}]
        },
        timeout=300
    )
    data = res.json()
    if "content" not in data:
        print("API ERROR:", json.dumps(data, indent=2))
        exit(1)
    return data["content"][0]["text"]

print("=" * 60)
print("3D SITE AGENT STARTING")
print("=" * 60)

# ─── STEP 1: PLAN THE SITE ────────────────────────────────
print("\n[1/4] Planning site architecture...")

PLANNER_SYSTEM = """You are a senior web architect. 
Given a website description, output a JSON plan ONLY.
No explanation. Just raw JSON starting with {"""

PLANNER_PROMPT = f"""
Plan this website: {USER_PROMPT}

Output JSON in this exact format:
{{
  "site_name": "name of the site",
  "theme": "color palette description",
  "sections": [
    {{
      "id": "hero",
      "name": "Hero Section",
      "description": "what this section contains and does",
      "has_3d": true,
      "three_js_features": ["feature1", "feature2"]
    }}
  ],
  "fonts": ["Font1", "Font2"],
  "color_primary": "#hexcode",
  "color_secondary": "#hexcode",
  "color_bg": "#hexcode"
}}
"""

plan_raw = call_claude(PLANNER_SYSTEM, PLANNER_PROMPT, max_tokens=2000)

# Clean JSON
plan_raw = plan_raw.strip()
if "```json" in plan_raw:
    plan_raw = plan_raw.split("```json")[1].split("```")[0].strip()
elif "```" in plan_raw:
    plan_raw = plan_raw.split("```")[1].split("```")[0].strip()

try:
    plan = json.loads(plan_raw)
    print(f"  Site: {plan['site_name']}")
    print(f"  Sections: {len(plan['sections'])}")
    for s in plan['sections']:
        print(f"    - {s['name']}")
except Exception as e:
    print(f"Plan parse error: {e}")
    print("Using simple mode...")
    plan = {
        "site_name": "3D Website",
        "sections": [{"id": "main", "name": "Main", "description": USER_PROMPT}],
        "color_primary": "#gold",
        "color_bg": "#0a0a0a"
    }

# ─── STEP 2: BUILD CSS + BASE ─────────────────────────────
print("\n[2/4] Building base styles and structure...")

BASE_SYSTEM = """You are an expert CSS developer.
Output ONLY raw CSS code. No explanation. No markdown."""

BASE_PROMPT = f"""
Create complete premium CSS for this website:
Site: {plan['site_name']}
Theme: {plan.get('theme', 'dark luxury')}
Primary color: {plan.get('color_primary', '#FFD700')}
Background: {plan.get('color_bg', '#0a0a0a')}
Fonts: {', '.join(plan.get('fonts', ['Playfair Display', 'Inter']))}

Include:
- CSS variables for all colors
- Google Fonts import for: {', '.join(plan.get('fonts', ['Playfair Display', 'Inter']))}
- Full reset and base styles
- Premium typography system
- Glassmorphism utility classes (.glass, .glass-dark)
- Smooth scroll behavior
- Custom scrollbar styling
- Button styles (.btn-primary, .btn-magnetic)
- Section base styles
- Cursor glow effect styles
- Animation keyframes (fadeIn, slideUp, scaleIn, float, steam)
- Mobile responsive breakpoints
- All section layouts for: {', '.join([s['name'] for s in plan['sections']])}
"""

css_code = call_claude(BASE_SYSTEM, BASE_PROMPT, max_tokens=4096)
css_code = re.sub(r'```css|```', '', css_code).strip()

# ─── STEP 3: BUILD EACH SECTION ───────────────────────────
print("\n[3/4] Building sections...")

SECTION_SYSTEM = """You are an expert HTML + Three.js developer.
Output ONLY the HTML for the requested section.
No DOCTYPE, no <html>, no <head>, no <body> tags.
Just the section HTML content with inline JS if needed."""

sections_html = []

for i, section in enumerate(plan['sections']):
    print(f"  Building: {section['name']}...")
    
    has_3d = section.get('has_3d', False)
    three_features = section.get('three_js_features', [])
    
    SECTION_PROMPT = f"""
Build the "{section['name']}" section for {plan['site_name']}.

Section description: {section['description']}
{'3D Features needed: ' + ', '.join(three_features) if has_3d else 'No 3D needed for this section'}
Primary color: {plan.get('color_primary', '#FFD700')}
Background color: {plan.get('color_bg', '#0a0a0a')}

Original site brief: {USER_PROMPT[:300]}

Rules:
- Output only the HTML for this section
- Section must have id="{section['id']}"
- {'Use Three.js (already loaded in page) for 3D elements' if has_3d else 'Use CSS animations only'}
- Use GSAP (already loaded) for scroll animations
- All JS must be in <script> tags within this section
- Make it premium, stunning, production quality
- Use CSS classes from the design system already defined
"""
    
    section_html = call_claude(SECTION_SYSTEM, SECTION_PROMPT, max_tokens=4096)
    section_html = re.sub(r'```html|```', '', section_html).strip()
    sections_html.append(section_html)
    print(f"    Done ({len(section_html)} chars)")

# ─── STEP 4: BUILD JAVASCRIPT ─────────────────────────────
print("\n[4/4] Building Three.js and animations...")

JS_SYSTEM = """You are an expert Three.js and GSAP developer.
Output ONLY raw JavaScript code. No explanation. No markdown."""

JS_PROMPT = f"""
Write the main JavaScript for {plan['site_name']}.

The site has these sections: {', '.join([s['name'] for s in plan['sections']])}
3D sections: {', '.join([s['name'] for s in plan['sections'] if s.get('has_3d')])}

Original brief: {USER_PROMPT[:500]}

Write:
1. Three.js scene initialization for all 3D canvases
2. All 3D objects, geometries, materials, lighting
3. Animation loops (requestAnimationFrame)
4. GSAP ScrollTrigger animations for all sections
5. Smooth scroll with Lenis if needed
6. Magnetic button effects
7. Cursor glow effect
8. Particle systems if needed
9. All event listeners
10. Mobile detection and simplified 3D for mobile

Use these CDNs already loaded:
- Three.js r128
- GSAP 3.12.2 with ScrollTrigger
"""

js_code = call_claude(JS_SYSTEM, JS_PROMPT, max_tokens=8096)
js_code = re.sub(r'```javascript|```js|```', '', js_code).strip()

# ─── COMBINE EVERYTHING ───────────────────────────────────
print("\nCombining all parts...")

fonts_list = plan.get('fonts', ['Playfair Display', 'Inter'])
fonts_url = '+'.join([f.replace(' ', '+') for f in fonts_list])

final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan['site_name']}</title>

    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family={fonts_url}:wght@300;400;600;700;900&display=swap" rel="stylesheet">

    <!-- Three.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

    <!-- GSAP -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>

    <style>
{css_code}
    </style>
</head>
<body>

    <!-- SECTIONS -->
{''.join(sections_html)}

    <!-- MAIN JAVASCRIPT -->
    <script>
{js_code}
    </script>

</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

total = len(final_html)
print(f"\n{'='*60}")
print(f"SUCCESS! index.html generated")
print(f"Total size: {total:,} characters ({total//1024} KB)")
print(f"Sections built: {len(sections_html)}")
print(f"{'='*60}")