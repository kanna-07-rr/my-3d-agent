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
            except:
            time.sleep(5)
    return ""

print(f"🚀 Building Premium 3D Site: {USER_PROMPT}")

# 1. PLAN
plan = json.loads(call_ai("Director", f"Plan a 3D site for: {USER_PROMPT}. Return ONLY JSON: {{'name':'','colors':{{'bg':'','accent':''}},'sections':[{{'id':'','title':'','3d_desc':''}}]}}"))

# 2. ASSEMBLE COMPONENTS
css = call_ai("Designer", f"Write premium CSS for {plan['name']}. Use colors {plan['colors']}. Include glassmorphism and full-page layouts.")
js = call_ai("Three.js Expert", f"Write JS to create 3D scenes for these IDs: {[s['id'] for s in plan['sections']]}. Descriptions: {[s['3d_desc'] for s in plan['sections']]}. Use GSAP ScrollTrigger to animate objects on scroll.")

# 3. HTML GENERATION
sections_html = "".join([f"<section id='{s['id']}'><canvas id='canvas_{s['id']}'></canvas><div class='content'><h1>{s['title']}</h1></div></section>" for s in plan['sections']])

final_html = f"""<!DOCTYPE html><html><head><title>{plan['name']}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/ScrollTrigger.min.js"></script>
<style>
body {{ margin: 0; background: {plan['colors']['bg']}; color: white; font-family: sans-serif; overflow-x: hidden; }}
section {{ position: relative; height: 100vh; display: flex; align-items: center; justify-content: center; }}
canvas {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }}
.content {{ z-index: 10; text-align: center; background: rgba(0,0,0,0.3); padding: 2rem; backdrop-filter: blur(15px); border-radius: 20px; border: 1px solid rgba(255,255,255,0.1); }}
{css}</style></head><body>{sections_html}<script>gsap.registerPlugin(ScrollTrigger);{js}</script></body></html>"""

with open("index.html", "w", encoding="utf-8") as f: f.write(final_html)