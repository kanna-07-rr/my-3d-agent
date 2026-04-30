import os, requests, json, re, time

# Config from GitHub Actions
KEY = os.environ.get("OPENROUTER_API_KEY")
USER_PROMPT = os.environ.get("SITE_PROMPT", "A luxury watch brand with floating gold gears")

def call_ai(system, user, max_tokens=6000):
    """Universal AI caller that cleans markdown and handles retries."""
    for attempt in range(3):
        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"},
                json={
                    "model": "openrouter/auto",
                    "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
                    "max_tokens": max_tokens, "temperature": 0.7
                },
                timeout=180
            )
            content = res.json()["choices"][0]["message"]["content"]
            # Clean all markdown fences
            content = re.sub(r'
           return content
        except Exception as e:
            print(f"Retrying due to error: {e}")
            time.sleep(5)
    return ""

print(f"🚀 Initializing 3D Agent for: {USER_PROMPT}")

# 1. PLAN - Define the 3D Architecture
plan_sys = "You are a Creative Director. Output ONLY raw JSON."
plan_usr = f"Plan a premium 3D website for: {USER_PROMPT}. Return ONLY valid JSON: {{'name':'','colors':{{'bg':'','accent':''}},'sections':[{{'id':'hero','title':'','3d_obj_desc':''}}]}}"
plan_raw = call_ai(plan_sys, plan_usr)
plan = json.loads(plan_raw)

# 2. DESIGN - Premium CSS
css_sys = "You are an Elite UI Designer. Output ONLY raw CSS."
css_usr = f"Write premium CSS for {plan['name']}. Use colors {plan['colors']}. Include luxury typography, glassmorphism, and smooth layout. No markdown."
css = call_ai(css_sys, css_usr)

# 3. ANIMATION - Three.js and GSAP logic
js_sys = "You are a Three.js and GSAP Master. Output ONLY raw JavaScript."
js_usr = f"""Write JS to create 3D scenes for these IDs: {[s['id'] for s in plan['sections']]}. 
Descriptions: {[s['3d_obj_desc'] for s in plan['sections']]}. 
Requirements: 
- Initialize Three.js on each section's canvas. 
- Use MeshPhysicalMaterial for a luxury look. 
- Use GSAP ScrollTrigger to rotate/animate objects on scroll."""
js = call_ai(js_sys, js_usr)

# 4. ASSEMBLY
sections_html = ""
for s in plan['sections']:
    sections_html += f"""
    <section id="{s['id']}" style="height: 100vh; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;">
        <canvas id="canvas_{s['id']}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;"></canvas>
        <div style="position: relative; z-index: 10; text-align: center; background: rgba(0,0,0,0.3); padding: 3rem; backdrop-filter: blur(20px); border-radius: 40px; border: 1px solid rgba(255,255,255,0.1);">
            <h1 style="font-size: 3.5rem; margin-bottom: 1rem; color: white;">{s['title']}</h1>
            <p style="color: white; opacity: 0.8;">{s['3d_obj_desc']}</p>
        </div>
    </section>"""

final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{plan['name']}</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
    <style>
        body {{ margin: 0; background: {plan['colors']['bg']}; color: white; font-family: sans-serif; overflow-x: hidden; }}
        {css}
    </style>
</head>
<body>
    <nav style="position: fixed; top: 0; width: 100%; padding: 2rem; z-index: 100; text-align: center; font-weight: bold; color: white;">{plan['name']}</nav>
    {sections_html}
    <script>
        gsap.registerPlugin(ScrollTrigger);
        {js}
    </script>
</body>
</html>"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)