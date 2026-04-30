import os, requests, json, re, time

# --- CONFIGURATION ---
KEY = os.environ.get("OPENROUTER_API_KEY", "")
USER_PROMPT = os.environ.get("SITE_PROMPT", "A premium futuristic cyberpunk portfolio")

def call_ai(system, user, max_tokens=6000, model="openrouter/auto"):
    """Calls OpenRouter API with retry logic and exponential backoff."""
    for attempt in range(4):
        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {KEY}", 
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
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
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            else:
                print(f"API Error: {data}")
        except Exception as e:
            wait = 3 ** attempt
            print(f"Network error, retrying in {wait}s... ({e})")
            time.sleep(wait)
    return ""

def clean_code(text):
    """Removes markdown fences (e.g., ```html, ```javascript) from AI output."""
    if not text: return ""
    text = re.sub(r'```[a-zA-Z]*\n', '', text)
    text = text.replace('```', '')
    return text.strip()

def safe_json(raw):
    """Extracts JSON from text if the AI includes conversational padding."""
    raw = clean_code(raw)
    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        try: return json.loads(match.group())
        except: pass
    try: return json.loads(raw)
    except: return None

print("=" * 60)
print("🚀 UNIVERSAL 3D PREMIUM SITE AGENT")
print("=" * 60)
print(f"Prompt: {USER_PROMPT}\n")

# --- STEP 1: ARCHITECTURE (JSON PLAN) ---
print("[1/4] Generating Architecture & 3D Blueprint...")
plan_sys = "You are a World-Class UX & 3D Web Architect. Output ONLY valid JSON. No markdown."
plan_usr = f"""Create a premium 3D website plan for this prompt: "{USER_PROMPT}".
Return ONLY this JSON structure:
{{
  "site_name": "Brand Name",
  "tagline": "Catchy Tagline",
  "colors": {{"bg": "#000000", "primary": "#hex", "accent": "#hex", "text": "#ffffff"}},
  "fonts": ["Primary Font", "Secondary Font"],
  "sections": [
    {{
      "id": "hero", 
      "name": "Hero Section", 
      "content": "Headline and subheadline text", 
      "three_scene_desc": "Describe a complex 3D object to render here (e.g., rotating abstract torus knot with neon glowing wireframes)"
    }},
    {{
      "id": "about", 
      "name": "About", 
      "content": "About section text", 
      "three_scene_desc": "Describe a floating particle system or 3D geometry"
    }}
  ]
}}
Ensure exactly 3 to 4 highly creative sections."""

plan_raw = call_ai(plan_sys, plan_usr, 1500)
plan = safe_json(plan_raw)

if not plan:
    print("Failed to generate plan. Exiting.")
    exit(1)

# --- STEP 2: STYLING (CSS) ---
print("[2/4] Writing Premium CSS...")
css_sys = "You are an Elite CSS Developer. Output ONLY raw CSS code. No markdown fences."
css_usr = f"""Write premium CSS for '{plan['site_name']}'.
Use this palette: Background: {plan['colors']['bg']}, Primary: {plan['colors']['primary']}, Accent: {plan['colors']['accent']}, Text: {plan['colors']['text']}.
Requirements:
1. Reset margin/padding.
2. Smooth scrolling (`html {{ scroll-behavior: smooth; }}`).
3. Include Glassmorphism effects (backdrop-filter: blur).
4. Modern, clean layouts using Flexbox or CSS Grid.
5. Absolute positioning for `.canvas-container` so Three.js renders behind or beside section text.
6. Make `.section-container` min-height: 100vh, relative positioning, overflow hidden."""

css = clean_code(call_ai(css_sys, css_usr, 3000))

# --- STEP 3: STRUCTURE (HTML) ---
print("[3/4] Building HTML Layouts...")
html_sys = "You are a Senior Web Developer. Output ONLY raw HTML snippets. No markdown, no html/head/body tags."
html_usr = f"""Generate the semantic HTML sections for '{plan['site_name']}'.
Data: {json.dumps(plan['sections'])}
Requirements:
1. Wrap each section in a `<section id="[id]" class="section-container">`.
2. Inside EACH section, include `<canvas id="canvas_[id]" class="three-canvas" style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:-1;"></canvas>`.
3. Add a wrapper `<div class="content-wrapper" style="position:relative; z-index:10; padding:5rem;">` for the text/content.
4. Add premium typography hierarchy (h1/h2, p, glossy buttons)."""

sections_html = clean_code(call_ai(html_sys, html_usr, 4000))

# --- STEP 4: ANIMATION (THREE.JS & GSAP) ---
print("[4/4] Programming 3D Engines & Animations...")
js_sys = "You are an expert Three.js and GSAP Creative Developer. Output ONLY raw JavaScript code. No markdown fences."
js_usr = f"""Write the JavaScript to initialize Three.js scenes and GSAP animations for '{plan['site_name']}'.
Scenes to build: {json.dumps([{'id': s['id'], 'desc': s['three_scene_desc']} for s in plan['sections']])}

Requirements:
1. Initialize a `THREE.WebGLRenderer`, `THREE.PerspectiveCamera`, and `THREE.Scene` for EACH canvas ID (e.g., document.getElementById('canvas_hero')).
2. Build the specific 3D geometries, materials, and lighting described in the data above. Make them look highly premium (use MeshStandardMaterial, envMaps, or glowing PointsMaterial).
3. Create a single `requestAnimationFrame` render loop that updates/rotates all 3D objects smoothly.
4. Handle `window.addEventListener('resize')` for all cameras and renderers.
5. Use `gsap.registerPlugin(ScrollTrigger)` to animate the HTML content (fade up, stagger) as the user scrolls into each section.
6. Tie some 3D object rotations or camera positions to GSAP ScrollTrigger so they react to scrolling!"""

js = clean_code(call_ai(js_sys, js_usr, 6000))

# --- ASSEMBLE FINAL FILE ---
print("\nAssembling final site...")
font_string = "&family=".join([f.replace(" ", "+") for f in plan.get("fonts", ["Inter", "Playfair Display"])])
google_fonts_url = f"https://fonts.googleapis.com/css2?family={font_string}&display=swap"

final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{plan['site_name']} | {plan.get('tagline', 'Premium Experience')}</title>
    
    <!-- Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="{google_fonts_url}" rel="stylesheet">
    
    <!-- Libraries -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
    
    <style>
        :root {{
            --bg: {plan['colors'].get('bg', '#000')};
            --primary: {plan['colors'].get('primary', '#fff')};
            --accent: {plan['colors'].get('accent', '#555')};
            --text: {plan['colors'].get('text', '#eee')};
        }}
        body {{
            background-color: var(--bg);
            color: var(--text);
            font-family: '{plan['fonts'][0]}', sans-serif;
            overflow-x: hidden;
            margin: 0;
            padding: 0;
        }}
        /* AI Generated CSS */
        {css}
    </style>
</head>
<body>

    <!-- Fixed Glass Navbar -->
    <nav style="position: fixed; top: 0; width: 100%; padding: 1.5rem 5%; z-index: 999; background: rgba(0,0,0,0.2); backdrop-filter: blur(15px); border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center;">
        <div style="font-family: '{plan.get('fonts', [''])[1] if len(plan.get('fonts', []))>1 else plan['fonts'][0]}', serif; font-size: 1.5rem; font-weight: bold; color: var(--primary);">
            {plan['site_name']}
        </div>
        <div>
            <a href="#hero" style="color: var(--text); text-decoration: none; margin-left: 2rem; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px;">Home</a>
        </div>
    </nav>

    <!-- AI Generated Sections -->
    {sections_html}

    <!-- AI Generated 3D & Animations -->
    <script>
        {js}
    </script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"✅ Success! Generated customized 3D premium site ({len(final_html)} bytes).")