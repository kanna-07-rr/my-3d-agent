import os, requests, json, re, time

KEY = os.environ["OPENROUTER_API_KEY"]
USER_PROMPT = os.environ.get("SITE_PROMPT", "Build a luxury Indian biryani restaurant website")

def call_ai(system, user, max_tokens=6000, retries=3):
    for attempt in range(retries):
        try:
            res = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "openrouter/auto",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": 0.6
                },
                timeout=180
            )
            data = res.json()
            if "choices" not in data:
                print(f"  API ERROR (attempt {attempt+1}):", json.dumps(data, indent=2))
                time.sleep(5)
                continue
            content = data["choices"][0]["message"]["content"]
            if not content or len(content.strip()) < 50:
                print(f"  WARNING: Very short response ({len(content) if content else 0} chars), retrying...")
                time.sleep(3)
                continue
            return content
        except Exception as e:
            print(f"  Exception (attempt {attempt+1}): {e}")
            time.sleep(5)
    return None

def strip_code_fences(text, lang=""):
    if not text:
        return ""
    # Remove ```lang ... ``` or ``` ... ```
    text = re.sub(r'```(?:html|css|javascript|js|json)?\s*', '', text)
    text = text.replace('```', '')
    return text.strip()

def safe_json(raw):
    if not raw:
        return None
    raw = strip_code_fences(raw)
    # Try to extract JSON object from anywhere in the string
    match = re.search(r'\{[\s\S]*\}', raw)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    try:
        return json.loads(raw)
    except:
        return None

print("=" * 60)
print("R BAWARCHI — LUXURY RESTAURANT SITE BUILDER")
print("=" * 60)
print(f"Prompt: {USER_PROMPT[:100]}...")

# ─── STEP 1: PLAN ────────────────────────────────────────────
print("\n[1/4] Planning site structure...")

plan_raw = call_ai(
    "You are a web architect. You MUST output ONLY valid raw JSON. No markdown fences, no explanation, no commentary. Just the JSON object.",
    f"""Create a website plan for: {USER_PROMPT}

Return ONLY this JSON structure, nothing else:
{{
  "site_name": "R Bawarchi",
  "tagline": "Crafted with Fire. Served with Legacy.",
  "color_bg": "#080503",
  "color_primary": "#C9A84C",
  "color_secondary": "#8B2500",
  "color_accent": "#F4D03F",
  "fonts": ["Playfair Display", "Cormorant Garamond"],
  "sections": [
    {{"id": "hero", "name": "Hero", "description": "Full-screen cinematic hero with 3D animated biryani bowl, steam particles, gold tagline, magnetic CTA button", "has_3d": true}},
    {{"id": "story", "name": "Our Story", "description": "Split layout heritage section with animated text reveal and decorative spice motifs", "has_3d": false}},
    {{"id": "menu", "name": "Menu", "description": "3D tilt food cards for 6 signature dishes with hover glow and modal popup", "has_3d": true}},
    {{"id": "signature", "name": "Signature Dish", "description": "Cinematic spotlight on Dum Biryani with orbiting spice particles", "has_3d": true}},
    {{"id": "experience", "name": "Experience", "description": "Glassmorphism testimonial cards with auto-rotating carousel", "has_3d": false}},
    {{"id": "booking", "name": "Reserve", "description": "Premium dark booking form with floating labels and gold accents", "has_3d": false}}
  ]
}}""",
    max_tokens=1000
)

plan = safe_json(plan_raw)
if not plan or "sections" not in plan:
    print("  Plan parsing failed — using hardcoded fallback")
    plan = {
        "site_name": "R Bawarchi",
        "tagline": "Crafted with Fire. Served with Legacy.",
        "color_bg": "#080503",
        "color_primary": "#C9A84C",
        "color_secondary": "#8B2500",
        "color_accent": "#F4D03F",
        "fonts": ["Playfair Display", "Cormorant Garamond"],
        "sections": [
            {"id": "hero", "name": "Hero", "description": "Full-screen cinematic hero with 3D animated biryani bowl, steam particles, gold tagline, magnetic CTA button", "has_3d": True},
            {"id": "story", "name": "Our Story", "description": "Split layout heritage section with animated text reveal and decorative spice motifs", "has_3d": False},
            {"id": "menu", "name": "Menu", "description": "3D tilt food cards for 6 signature dishes with hover glow and modal popup", "has_3d": True},
            {"id": "signature", "name": "Signature Dish", "description": "Cinematic spotlight on Dum Biryani with orbiting spice particles", "has_3d": True},
            {"id": "experience", "name": "Experience", "description": "Glassmorphism testimonial cards with auto-rotating carousel", "has_3d": False},
            {"id": "booking", "name": "Reserve", "description": "Premium dark booking form with floating labels and gold accents", "has_3d": False}
        ]
    }

print(f"  Site: {plan['site_name']} | Sections: {len(plan['sections'])}")

bg      = plan.get('color_bg', '#080503')
primary = plan.get('color_primary', '#C9A84C')
second  = plan.get('color_secondary', '#8B2500')
accent  = plan.get('color_accent', '#F4D03F')
fonts   = plan.get('fonts', ['Playfair Display', 'Cormorant Garamond'])

# ─── STEP 2: CSS ─────────────────────────────────────────────
print("\n[2/4] Building CSS...")

css_raw = call_ai(
    "You are a CSS expert. Output ONLY raw CSS code. No markdown fences, no explanation. Start directly with :root or @import.",
    f"""Write complete premium CSS for a luxury restaurant website "{plan['site_name']}".

CSS Variables:
--bg: {bg}
--primary: {primary}
--secondary: {second}
--accent: {accent}

Rules to follow:
1. Start with @import for Google Fonts: {', '.join(fonts)}
2. Define :root with all CSS variables
3. Full CSS reset (*, body, html)
4. Smooth scroll: html {{ scroll-behavior: smooth }}
5. Body: background var(--bg), color #f5f0e8, font-family first font
6. Nav: fixed top, glassmorphism (backdrop-filter: blur(20px)), gold logo text, flex links
7. Section base: min-height 100vh, padding 80px 5%
8. .hero: position relative, overflow hidden, display flex, align-items center
9. canvas: position absolute, top 0, left 0, width 100%, height 100%, z-index 0
10. .hero-content: position relative, z-index 10
11. h1: font Playfair Display, font-size clamp(3rem,8vw,7rem), color var(--primary)
12. h2: font Playfair Display, font-size clamp(2rem,5vw,4rem), margin-bottom 2rem
13. .btn-primary: display inline-block, padding 1rem 3rem, background var(--primary), color #000, font-weight 700, letter-spacing 2px, text-transform uppercase, cursor pointer, border none, position relative, overflow hidden, transition all 0.3s
14. .btn-primary:hover: background var(--accent), transform translateY(-2px)
15. .glass: background rgba(255,255,255,0.05), backdrop-filter blur(20px), border 1px solid rgba(201,168,76,0.2), border-radius 12px
16. .menu-grid: display grid, grid-template-columns repeat(auto-fit,minmax(280px,1fr)), gap 2rem
17. .menu-card: background rgba(255,255,255,0.03), border 1px solid rgba(201,168,76,0.15), border-radius 16px, padding 2rem, cursor pointer, transition all 0.4s, transform-style preserve-3d
18. .menu-card:hover: border-color var(--primary), box-shadow 0 20px 60px rgba(201,168,76,0.2), transform translateY(-8px)
19. .modal-overlay: display none, position fixed, inset 0, background rgba(0,0,0,0.9), z-index 1000, align-items center, justify-content center
20. .modal-overlay.active: display flex
21. .modal-box: background #0f0a05, border 1px solid var(--primary), border-radius 20px, padding 3rem, max-width 500px, width 90%, position relative
22. .testimonial-card: glass class styles + padding 2rem, border-radius 16px, margin 1rem
23. Form inputs: width 100%, background transparent, border none, border-bottom 1px solid rgba(201,168,76,0.3), padding 1rem 0, color #f5f0e8, font-size 1rem, outline none, transition border-color 0.3s
24. Form inputs focus: border-bottom-color var(--primary)
25. .form-group: position relative, margin-bottom 2rem
26. .form-label: position absolute, top 1rem, left 0, color rgba(245,240,232,0.5), transition all 0.3s, pointer-events none
27. input:focus ~ .form-label, input:not(:placeholder-shown) ~ .form-label: top -0.5rem, font-size 0.75rem, color var(--primary)
28. Scrollbar: width 6px, background #111, thumb background var(--primary)
29. Gold divider: .divider: width 80px, height 2px, background linear-gradient(to right, transparent, var(--primary), transparent), margin 1.5rem auto
30. Responsive: @media (max-width:768px): font sizes smaller, grid 1 col, canvas height 50vh

Output ONLY the CSS. Nothing else.""",
    max_tokens=5000
)

css = strip_code_fences(css_raw)
if not css or len(css) < 200:
    print("  CSS generation failed — using minimal fallback CSS")
    css = f"""
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Cormorant+Garamond:wght@300;400;600&display=swap');
:root {{ --bg:{bg}; --primary:{primary}; --secondary:{second}; --accent:{accent}; }}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{background:var(--bg);color:#f5f0e8;font-family:'Cormorant Garamond',serif;overflow-x:hidden}}
canvas{{position:absolute;top:0;left:0;width:100%;height:100%;z-index:0}}
nav{{position:fixed;top:0;width:100%;padding:1.5rem 5%;display:flex;justify-content:space-between;align-items:center;z-index:100;backdrop-filter:blur(20px);background:rgba(8,5,3,0.8);border-bottom:1px solid rgba(201,168,76,0.1)}}
.nav-logo{{font-family:'Playfair Display',serif;font-size:1.5rem;color:var(--primary);font-weight:700;text-decoration:none}}
.nav-links{{display:flex;gap:2rem;list-style:none}}
.nav-links a{{color:#f5f0e8;text-decoration:none;font-size:0.9rem;letter-spacing:1px;text-transform:uppercase;transition:color 0.3s}}
.nav-links a:hover{{color:var(--primary)}}
section{{min-height:100vh;padding:100px 5%;display:flex;flex-direction:column;justify-content:center;position:relative;overflow:hidden}}
.hero{{position:relative;display:flex;align-items:center;justify-content:center;text-align:center}}
.hero-content{{position:relative;z-index:10}}
h1{{font-family:'Playfair Display',serif;font-size:clamp(3rem,8vw,7rem);color:var(--primary);line-height:1.1;margin-bottom:1rem}}
h2{{font-family:'Playfair Display',serif;font-size:clamp(2rem,5vw,4rem);color:var(--primary);margin-bottom:2rem}}
p{{line-height:1.8;color:rgba(245,240,232,0.8)}}
.btn-primary{{display:inline-block;padding:1rem 3rem;background:var(--primary);color:#000;font-weight:700;letter-spacing:2px;text-transform:uppercase;cursor:pointer;border:none;border-radius:2px;transition:all 0.3s;text-decoration:none;font-family:'Cormorant Garamond',serif;font-size:1rem}}
.btn-primary:hover{{background:var(--accent);transform:translateY(-2px);box-shadow:0 10px 30px rgba(201,168,76,0.4)}}
.glass{{background:rgba(255,255,255,0.04);backdrop-filter:blur(20px);border:1px solid rgba(201,168,76,0.2);border-radius:12px}}
.divider{{width:80px;height:2px;background:linear-gradient(to right,transparent,var(--primary),transparent);margin:1.5rem auto}}
.menu-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:2rem;margin-top:3rem}}
.menu-card{{background:rgba(255,255,255,0.03);border:1px solid rgba(201,168,76,0.15);border-radius:16px;padding:2rem;cursor:pointer;transition:all 0.4s;text-align:center}}
.menu-card:hover{{border-color:var(--primary);box-shadow:0 20px 60px rgba(201,168,76,0.15);transform:translateY(-8px)}}
.menu-card h3{{font-family:'Playfair Display',serif;color:var(--primary);font-size:1.3rem;margin-bottom:0.5rem}}
.menu-card .price{{color:var(--accent);font-size:1.1rem;margin-top:1rem}}
.modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,0.9);z-index:1000;align-items:center;justify-content:center}}
.modal-overlay.active{{display:flex}}
.modal-box{{background:#0f0a05;border:1px solid var(--primary);border-radius:20px;padding:3rem;max-width:500px;width:90%;position:relative}}
.modal-close{{position:absolute;top:1rem;right:1.5rem;background:none;border:none;color:var(--primary);font-size:1.5rem;cursor:pointer}}
.testimonials-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:2rem;margin-top:3rem}}
.testimonial-card{{background:rgba(255,255,255,0.04);border:1px solid rgba(201,168,76,0.2);border-radius:16px;padding:2rem}}
.testimonial-card .quote{{font-size:1.1rem;font-style:italic;line-height:1.8;margin-bottom:1rem;color:rgba(245,240,232,0.9)}}
.testimonial-card .author{{color:var(--primary);font-weight:600}}
.form-group{{position:relative;margin-bottom:2rem}}
.form-group input,.form-group select,.form-group textarea{{width:100%;background:transparent;border:none;border-bottom:1px solid rgba(201,168,76,0.3);padding:1rem 0;color:#f5f0e8;font-size:1rem;outline:none;transition:border-color 0.3s;font-family:inherit}}
.form-group input:focus,.form-group select:focus{{border-bottom-color:var(--primary)}}
.form-group select option{{background:#0f0a05}}
.story-grid{{display:grid;grid-template-columns:1fr 1fr;gap:5rem;align-items:center}}
.story-text .year{{font-size:5rem;font-family:'Playfair Display',serif;color:var(--primary);opacity:0.15;line-height:1}}
.spice-decoration{{display:flex;flex-direction:column;gap:2rem;align-items:center;justify-content:center}}
.spice-item{{font-size:3rem;opacity:0.6;transition:opacity 0.3s}}
.spice-item:hover{{opacity:1}}
::-webkit-scrollbar{{width:6px}}::-webkit-scrollbar-track{{background:#111}}::-webkit-scrollbar-thumb{{background:var(--primary);border-radius:3px}}
@media(max-width:768px){{.story-grid{{grid-template-columns:1fr}}.nav-links{{display:none}}section{{padding:80px 5%}}}}
"""
print(f"  CSS: {len(css)} chars")
# ─── STEP 3: SECTIONS HTML ────────────────────────────────────
print("\n[3/4] Building sections...")

SECTION_PROMPTS = {
    "hero": f"""Build the hero section HTML for restaurant "{plan['site_name']}".

Output ONLY the HTML below. No DOCTYPE, no <html>, no <head>, no <body>, no <style>, no <script>.

Include:
- <nav> tag with class="nav" containing: logo "{plan['site_name']}" (anchor .nav-logo), ul.nav-links with links: Our Story, Menu, Experience, Reserve
- <section id="hero" class="hero"> containing:
  - <canvas id="heroCanvas"></canvas>
  - <div class="hero-content"> with:
    - <p> tag: "Royal Biryani House" in uppercase letter-spacing style
    - <h1>Crafted with Fire.<br>Served with Legacy.</h1>
    - <div class="divider"></div>
    - <p> tag: "Where centuries of culinary tradition meet modern luxury"
    - <a href="#menu" class="btn-primary" id="ctaBtn">Explore the Menu</a>
- <div id="modal-overlay" class="modal-overlay"> containing .modal-box with close button and placeholder content

All text must be visible. The section background is {bg}.""",

    "story": f"""Build the "Our Story" section HTML for restaurant "{plan['site_name']}".

Output ONLY the section HTML. No DOCTYPE, no html/head/body/style/script tags.

Include:
<section id="story" style="background:{bg};padding:100px 5%;">
  <div style="max-width:1200px;margin:0 auto;">
    <div style="text-align:center;margin-bottom:4rem;">
      <p style="color:{primary};letter-spacing:3px;text-transform:uppercase;font-size:0.85rem;">Since 1978</p>
      <h2>A Legacy Forged in Fire</h2>
      <div class="divider"></div>
    </div>
    <div class="story-grid">
      <div class="story-text">
        <div class="year">1978</div>
        <h3 style="font-family:'Playfair Display',serif;font-size:2rem;color:{primary};margin-bottom:1.5rem;">Where Every Grain Tells a Story</h3>
        <p style="margin-bottom:1.5rem;">Born in the royal kitchens of Hyderabad, our dum biryani recipe has been passed down through five generations. Each pot sealed with dough, each grain slow-cooked for 48 hours over charcoal fire.</p>
        <p style="margin-bottom:2rem;">We don't just serve food — we serve heritage. Every plate carries the weight of centuries, the warmth of tradition, and the soul of authentic Indian craftsmanship.</p>
        <a href="#menu" class="btn-primary">Discover Our Menu</a>
      </div>
      <div class="spice-decoration">
        <div class="spice-item">🌿</div>
        <div style="width:1px;height:80px;background:linear-gradient(to bottom,transparent,{primary},transparent);"></div>
        <div class="spice-item">⭐</div>
        <div style="width:1px;height:80px;background:linear-gradient(to bottom,transparent,{primary},transparent);"></div>
        <div class="spice-item">🔥</div>
        <div style="border:1px solid rgba(201,168,76,0.3);padding:2rem;border-radius:12px;text-align:center;">
          <p style="color:{primary};font-size:3rem;font-family:'Playfair Display',serif;font-weight:900;">47</p>
          <p style="color:rgba(245,240,232,0.7);font-size:0.85rem;letter-spacing:2px;text-transform:uppercase;">Spice Varieties</p>
        </div>
      </div>
    </div>
  </div>
</section>""",
"menu": f"""Build the Menu section HTML for restaurant "{plan['site_name']}".

Output ONLY the section HTML. No DOCTYPE, no html/head/body/style/script tags.

<section id="menu" style="background:linear-gradient(180deg,{bg} 0%,#0d0805 100%);padding:100px 5%;">
  <div style="max-width:1200px;margin:0 auto;">
    <div style="text-align:center;margin-bottom:4rem;">
      <p style="color:{primary};letter-spacing:3px;text-transform:uppercase;font-size:0.85rem;">Curated For You</p>
      <h2>Signature Collection</h2>
      <div class="divider"></div>
    </div>
    <div style="display:flex;gap:1rem;justify-content:center;margin-bottom:3rem;flex-wrap:wrap;">
      <button onclick="filterMenu('all')" style="padding:0.5rem 1.5rem;background:rgba(201,168,76,0.15);border:1px solid {primary};color:{primary};cursor:pointer;border-radius:4px;letter-spacing:1px;text-transform:uppercase;font-size:0.8rem;">All</button>
      <button onclick="filterMenu('biryani')" style="padding:0.5rem 1.5rem;background:transparent;border:1px solid rgba(201,168,76,0.3);color:rgba(245,240,232,0.7);cursor:pointer;border-radius:4px;letter-spacing:1px;text-transform:uppercase;font-size:0.8rem;">Biryani</button>
      <button onclick="filterMenu('starters')" style="padding:0.5rem 1.5rem;background:transparent;border:1px solid rgba(201,168,76,0.3);color:rgba(245,240,232,0.7);cursor:pointer;border-radius:4px;letter-spacing:1px;text-transform:uppercase;font-size:0.8rem;">Starters</button>
      <button onclick="filterMenu('desserts')" style="padding:0.5rem 1.5rem;background:transparent;border:1px solid rgba(201,168,76,0.3);color:rgba(245,240,232,0.7);cursor:pointer;border-radius:4px;letter-spacing:1px;text-transform:uppercase;font-size:0.8rem;">Desserts</button>
    </div>
    <div class="menu-grid" id="menuGrid">
      <div class="menu-card" data-cat="biryani" onclick="openModal('Dum Biryani','The crown jewel. Slow-cooked for 48 hours in a sealed clay pot with aged Basmati rice, saffron, and 12 whole spices.','₹680')">
        <div style="font-size:3rem;margin-bottom:1rem;">🍲</div>
        <h3>Dum Biryani</h3>
        <p style="color:rgba(245,240,232,0.6);font-size:0.9rem;margin:0.5rem 0;">48-hour slow-cooked in sealed handi</p>
        <div class="price">₹ 680</div>
      </div>
      <div class="menu-card" data-cat="biryani" onclick="openModal('Saffron Mutton','Tender mutton pieces marinated overnight in yogurt and 24 spices, layered with saffron-infused Basmati rice.','₹750')">
        <div style="font-size:3rem;margin-bottom:1rem;">🥘</div>
        <h3>Saffron Mutton</h3>
        <p style="color:rgba(245,240,232,0.6);font-size:0.9rem;margin:0.5rem 0;">Overnight marinated, royal Mughal recipe</p>
        <div class="price">₹ 750</div>
      </div>
      <div class="menu-card" data-cat="starters" onclick="openModal('Seekh Kebab','Hand-minced lamb mixed with roasted spices, charcoal-grilled on iron skewers. Served with mint chutney.','₹320')">
        <div style="font-size:3rem;margin-bottom:1rem;">🍢</div>
        <h3>Seekh Kebab</h3>
        <p style="color:rgba(245,240,232,0.6);font-size:0.9rem;margin:0.5rem 0;">Charcoal-grilled iron skewer kebabs</p>
        <div class="price">₹ 320</div>
      </div>
      <div class="menu-card" data-cat="starters" onclick="openModal('Galouti Kebab','The melt-in-mouth Lucknowi speciality. 150 spices, minced lamb, slow-cooked on tawa.','₹380')">
        <div style="font-size:3rem;margin-bottom:1rem;">🥩</div>
        <h3>Galouti Kebab</h3>
        <p style="color:rgba(245,240,232,0.6);font-size:0.9rem;margin:0.5rem 0;">150 spice Lucknowi melt-in-mouth classic</p>
        <div class="price">₹ 380</div>
      </div>
      <div class="menu-card" data-cat="desserts" onclick="openModal('Shahi Tukda','Royal bread pudding soaked in rabri (reduced milk), rose water and garnished with real silver leaf.','₹220')">
        <div style="font-size:3rem;margin-bottom:1rem;">🍮</div>
        <h3>Shahi Tukda</h3>
        <p style="color:rgba(245,240,232,0.6);font-size:0.9rem;margin:0.5rem 0;">Royal bread pudding with silver leaf</p>
        <div class="price">₹ 220</div>
      </div>
      <div class="menu-card" data-cat="desserts" onclick="openModal('Gulab Phirni','Rose-infused rice pudding chilled in clay pots, topped with pistachio and edible rose petals.','₹180')">
        <div style="font-size:3rem;margin-bottom:1rem;">🌹</div>
        <h3>Gulab Phirni</h3>
        <p style="color:rgba(245,240,232,0.6);font-size:0.9rem;margin:0.5rem 0;">Rose-infused rice pudding in clay pot</p>
        <div class="price">₹ 180</div>
      </div>
    </div>
  </div>
  <div class="modal-overlay" id="menuModal">
    <div class="modal-box">
      <button class="modal-close" onclick="closeModal()">✕</button>
      <div style="text-align:center;">
        <div id="modalEmoji" style="font-size:4rem;margin-bottom:1rem;"></div>
        <h3 id="modalTitle" style="font-family:'Playfair Display',serif;color:{primary};font-size:2rem;margin-bottom:1rem;"></h3>
        <p id="modalDesc" style="color:rgba(245,240,232,0.8);line-height:1.8;margin-bottom:1.5rem;"></p>
        <p id="modalPrice" style="color:{accent};font-size:1.5rem;font-family:'Playfair Display',serif;margin-bottom:2rem;"></p>
        <a href="#booking" class="btn-primary" onclick="closeModal()">Reserve a Table</a>
      </div>
    </div>
  </div>
</section>""",
"signature": f"""Build the Signature Dish section HTML for restaurant "{plan['site_name']}".

Output ONLY the section HTML. No DOCTYPE, no html/head/body/style/script tags.

<section id="signature" style="background:#050301;padding:100px 5%;text-align:center;position:relative;overflow:hidden;">
  <div style="position:absolute;inset:0;background:radial-gradient(ellipse at center,rgba(139,37,0,0.15) 0%,transparent 70%);pointer-events:none;"></div>
  <canvas id="signatureCanvas" style="position:absolute;top:0;left:0;width:100%;height:100%;z-index:0;opacity:0.6;"></canvas>
  <div style="position:relative;z-index:10;max-width:800px;margin:0 auto;">
    <p style="color:{primary};letter-spacing:4px;text-transform:uppercase;font-size:0.8rem;margin-bottom:1rem;">The Crown Jewel</p>
    <h2>Dum Biryani</h2>
    <div class="divider"></div>
    <p style="font-size:1.2rem;color:rgba(245,240,232,0.8);max-width:600px;margin:0 auto 3rem;line-height:1.8;">48-hour slow-cooked perfection. Sealed in a clay handi with dough. Every grain infused with saffron, rose water, and the smoke of decades.</p>
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem;margin-bottom:3rem;">
      <div style="background:rgba(201,168,76,0.05);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:1.5rem;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">🌿</div>
        <p style="color:{primary};font-weight:600;font-size:0.9rem;">Saffron</p>
        <p style="color:rgba(245,240,232,0.5);font-size:0.75rem;margin-top:0.25rem;">Kashmiri Grade A</p>
      </div>
      <div style="background:rgba(201,168,76,0.05);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:1.5rem;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">🌾</div>
        <p style="color:{primary};font-weight:600;font-size:0.9rem;">Basmati</p>
        <p style="color:rgba(245,240,232,0.5);font-size:0.75rem;margin-top:0.25rem;">Aged 2 Years</p>
      </div>
      <div style="background:rgba(201,168,76,0.05);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:1.5rem;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">🔥</div>
        <p style="color:{primary};font-weight:600;font-size:0.9rem;">Charcoal</p>
        <p style="color:rgba(245,240,232,0.5);font-size:0.75rem;margin-top:0.25rem;">48hr Dum Cook</p>
      </div>
      <div style="background:rgba(201,168,76,0.05);border:1px solid rgba(201,168,76,0.2);border-radius:12px;padding:1.5rem;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">⭐</div>
        <p style="color:{primary};font-weight:600;font-size:0.9rem;">12 Spices</p>
        <p style="color:rgba(245,240,232,0.5);font-size:0.75rem;margin-top:0.25rem;">Whole &amp; Ground</p>
      </div>
    </div>
    <a href="#booking" class="btn-primary">Reserve Your Table</a>
  </div>
</section>""",

    "experience": f"""Build the Experience / Testimonials section HTML for restaurant "{plan['site_name']}".

Output ONLY the section HTML. No DOCTYPE, no html/head/body/style/script tags.

<section id="experience" style="background:linear-gradient(180deg,#050301 0%,{bg} 100%);padding:100px 5%;">
  <div style="max-width:1100px;margin:0 auto;">
    <div style="text-align:center;margin-bottom:4rem;">
      <p style="color:{primary};letter-spacing:3px;text-transform:uppercase;font-size:0.85rem;">Our Guests</p>
      <h2>Unforgettable Moments</h2>
      <div class="divider"></div>
    </div>
    <div class="testimonials-grid">
      <div class="testimonial-card">
        <div style="color:{primary};font-size:2rem;margin-bottom:1rem;">"</div>
        <p class="quote">The Dum Biryani transported me to old Hyderabad. I've traveled across India chasing authentic biryani — this is the pinnacle. The saffron aroma alone is worth the journey.</p>
        <div style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid rgba(201,168,76,0.15);">
          <p class="author">Arjun Mehta</p>
          <p style="color:rgba(245,240,232,0.4);font-size:0.8rem;margin-top:0.25rem;">Food Critic, The Hindu</p>
          <div style="margin-top:0.5rem;color:{primary};">★★★★★</div>
        </div>
      </div>
      <div class="testimonial-card">
        <div style="color:{primary};font-size:2rem;margin-bottom:1rem;">"</div>
        <p class="quote">We celebrated our anniversary here. The ambience, the service, the Galouti Kebab — everything was flawless. R Bawarchi doesn't just serve food, they serve an experience.</p>
        <div style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid rgba(201,168,76,0.15);">
          <p class="author">Priya &amp; Rohit Sharma</p>
          <p style="color:rgba(245,240,232,0.4);font-size:0.8rem;margin-top:0.25rem;">Regular Guests since 2019</p>
          <div style="margin-top:0.5rem;color:{primary};">★★★★★</div>
        </div>
      </div>
      <div class="testimonial-card">
        <div style="color:{primary};font-size:2rem;margin-bottom:1rem;">"</div>
        <p class="quote">Michelin-level cooking meets the warmth of a family kitchen. The Shahi Tukda with real silver leaf was an act of love. This is Indian fine dining done right.</p>
        <div style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid rgba(201,168,76,0.15);">
          <p class="author">Chef Marco Delgado</p>
          <p style="color:rgba(245,240,232,0.4);font-size:0.8rem;margin-top:0.25rem;">Executive Chef, The Leela Palace</p>
          <div style="margin-top:0.5rem;color:{primary};">★★★★★</div>
        </div>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;margin-top:4rem;text-align:center;">
      <div>
        <p style="font-family:'Playfair Display',serif;font-size:3.5rem;color:{primary};font-weight:900;line-height:1;">47</p>
        <p style="color:rgba(245,240,232,0.5);letter-spacing:2px;text-transform:uppercase;font-size:0.8rem;margin-top:0.5rem;">Years of Legacy</p>
      </div>
      <div>
        <p style="font-family:'Playfair Display',serif;font-size:3.5rem;color:{primary};font-weight:900;line-height:1;">1.2M</p>
        <p style="color:rgba(245,240,232,0.5);letter-spacing:2px;text-transform:uppercase;font-size:0.8rem;margin-top:0.5rem;">Guests Served</p>
      </div>
      <div>
        <p style="font-family:'Playfair Display',serif;font-size:3.5rem;color:{primary};font-weight:900;line-height:1;">12</p>
        <p style="color:rgba(245,240,232,0.5);letter-spacing:2px;text-transform:uppercase;font-size:0.8rem;margin-top:0.5rem;">Awards Won</p>
      </div>
    </div>
  </div>
</section>""",
"booking": f"""Build the Reserve a Table section HTML for restaurant "{plan['site_name']}".

Output ONLY the section HTML. No DOCTYPE, no html/head/body/style/script tags.

<section id="booking" style="background:{bg};padding:100px 5%;">
  <div style="max-width:700px;margin:0 auto;text-align:center;">
    <p style="color:{primary};letter-spacing:3px;text-transform:uppercase;font-size:0.85rem;">Join Us</p>
    <h2>Reserve a Table</h2>
    <div class="divider"></div>
    <p style="color:rgba(245,240,232,0.6);margin-bottom:3rem;">Experience the finest biryani in a setting worthy of royalty. Reserve your table and let us craft an evening you'll never forget.</p>
    <div style="background:rgba(255,255,255,0.03);border:1px solid rgba(201,168,76,0.15);border-radius:20px;padding:3rem;text-align:left;">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 2rem;">
        <div class="form-group">
          <input type="text" id="fname" placeholder=" " style="width:100%;background:transparent;border:none;border-bottom:1px solid rgba(201,168,76,0.3);padding:1rem 0;color:#f5f0e8;font-size:1rem;outline:none;font-family:inherit;">
          <label style="position:absolute;top:1rem;left:0;color:rgba(245,240,232,0.5);pointer-events:none;transition:all 0.3s;font-size:0.9rem;" id="lname">Full Name</label>
        </div>
        <div class="form-group">
          <input type="email" id="femail" placeholder=" " style="width:100%;background:transparent;border:none;border-bottom:1px solid rgba(201,168,76,0.3);padding:1rem 0;color:#f5f0e8;font-size:1rem;outline:none;font-family:inherit;">
          <label style="position:absolute;top:1rem;left:0;color:rgba(245,240,232,0.5);pointer-events:none;transition:all 0.3s;font-size:0.9rem;" id="lemail">Email Address</label>
        </div>
        <div class="form-group">
          <input type="date" id="fdate" style="width:100%;background:transparent;border:none;border-bottom:1px solid rgba(201,168,76,0.3);padding:1rem 0;color:#f5f0e8;font-size:1rem;outline:none;font-family:inherit;color-scheme:dark;">
          <label style="position:absolute;top:-0.5rem;left:0;color:{primary};font-size:0.75rem;pointer-events:none;">Date</label>
        </div>
        <div class="form-group">
          <select id="fguests" style="width:100%;background:transparent;border:none;border-bottom:1px solid rgba(201,168,76,0.3);padding:1rem 0;color:#f5f0e8;font-size:1rem;outline:none;font-family:inherit;-webkit-appearance:none;">
            <option value="" style="background:#0f0a05;">Select Guests</option>
            <option value="1" style="background:#0f0a05;">1 Guest</option>
            <option value="2" style="background:#0f0a05;">2 Guests</option>
            <option value="3-4" style="background:#0f0a05;">3-4 Guests</option>
            <option value="5-8" style="background:#0f0a05;">5-8 Guests</option>
            <option value="9+" style="background:#0f0a05;">9+ Guests (Private Dining)</option>
          </select>
          <label style="position:absolute;top:-0.5rem;left:0;color:{primary};font-size:0.75rem;pointer-events:none;">Guests</label>
        </div>
      </div>
      <div class="form-group" style="margin-top:1rem;">
        <textarea id="fspecial" placeholder="Special requests, dietary requirements, or occasion details..." rows="3" style="width:100%;background:transparent;border:none;border-bottom:1px solid rgba(201,168,76,0.3);padding:1rem 0;color:#f5f0e8;font-size:1rem;outline:none;font-family:inherit;resize:none;"></textarea>
      </div>
      <div style="text-align:center;margin-top:2rem;">
        <button onclick="submitBooking()" class="btn-primary" style="width:100%;padding:1.2rem;font-size:1rem;border:none;cursor:pointer;">Confirm Reservation</button>
      </div>
      <div id="bookingSuccess" style="display:none;text-align:center;margin-top:2rem;padding:1.5rem;background:rgba(201,168,76,0.1);border:1px solid {primary};border-radius:8px;">
        <p style="color:{primary};font-size:1.1rem;">✓ Reservation Received</p>
        <p style="color:rgba(245,240,232,0.7);margin-top:0.5rem;font-size:0.9rem;">We'll confirm your table within 2 hours via email.</p>
      </div>
    </div>
  </div>
  <footer style="text-align:center;margin-top:6rem;padding-top:3rem;border-top:1px solid rgba(201,168,76,0.1);">
    <p style="font-family:'Playfair Display',serif;font-size:1.5rem;color:{primary};">{plan['site_name']}</p>
    <p style="color:rgba(245,240,232,0.4);font-size:0.85rem;margin-top:1rem;letter-spacing:1px;">123 Royal Palace Road, Hyderabad · reservations@rbawarchi.com · +91 98765 43210</p>
    <p style="color:rgba(245,240,232,0.2);font-size:0.75rem;margin-top:2rem;">© 2025 R Bawarchi. All rights reserved.</p>
  </footer>
</section>"""
}

sections_html = []
for section in plan['sections']:
    sid = section['id']
    print(f"  Building [{sid}]...", end=" ")

    if sid in SECTION_PROMPTS:
        # Use our hardcoded high-quality prompt
        html = SECTION_PROMPTS[sid]
        print(f"✓ hardcoded ({len(html)} chars)")
    else:
        # Fallback: ask AI for unknown sections
        raw = call_ai(
            "Output ONLY raw HTML for this section. No DOCTYPE, no html/head/body/style/script. Just the section element.",
            f"""Build the "{section['name']}" section for {plan['site_name']}.
{section['description']}
Section id="{sid}"
Colors: bg={bg}, primary={primary}, secondary={second}
Use inline styles. Make it look premium. Gold color scheme.""",
            max_tokens=3000
        )
        html = strip_code_fences(raw) if raw else ""
        if not html or len(html) < 100:
            html = f'''<section id="{sid}" style="background:{bg};padding:100px 5%;text-align:center;">
              <h2 style="font-family:\'Playfair Display\',serif;color:{primary};">{section["name"]}</h2>
              <div style="width:80px;height:2px;background:{primary};margin:1.5rem auto;"></div>
              <p style="color:rgba(245,240,232,0.7);">{section["description"]}</p>
            </section>'''
        print(f"✓ AI ({len(html)} chars)")

    sections_html.append(html)
    # ─── STEP 4: JAVASCRIPT ───────────────────────────────────────
print("\n[4/4] Building JavaScript...")

# Core JS is hardcoded for reliability — AI fills in 3D scenes
js_core = f"""
// ── CURSOR GLOW ──────────────────────────────────────────────
const cursor = document.createElement('div');
cursor.style.cssText = 'position:fixed;width:20px;height:20px;border-radius:50%;background:rgba(201,168,76,0.4);pointer-events:none;z-index:9999;transform:translate(-50%,-50%);transition:transform 0.1s,width 0.3s,height 0.3s;mix-blend-mode:screen;';
document.body.appendChild(cursor);
const cursorOuter = document.createElement('div');
cursorOuter.style.cssText = 'position:fixed;width:40px;height:40px;border-radius:50%;border:1px solid rgba(201,168,76,0.3);pointer-events:none;z-index:9998;transform:translate(-50%,-50%);transition:all 0.15s ease;';
document.body.appendChild(cursorOuter);
document.addEventListener('mousemove', e => {{
  cursor.style.left = e.clientX + 'px';
  cursor.style.top = e.clientY + 'px';
  cursorOuter.style.left = e.clientX + 'px';
  cursorOuter.style.top = e.clientY + 'px';
}});
document.addEventListener('mousedown', () => {{ cursor.style.transform='translate(-50%,-50%) scale(0.7)'; }});
document.addEventListener('mouseup', () => {{ cursor.style.transform='translate(-50%,-50%) scale(1)'; }});

// ── SCROLL ANIMATIONS ─────────────────────────────────────────
if (typeof gsap !== 'undefined' && typeof ScrollTrigger !== 'undefined') {{
  gsap.registerPlugin(ScrollTrigger);
  gsap.utils.toArray('section').forEach((sec, i) => {{
    if (i === 0) return;
    gsap.fromTo(sec.querySelectorAll('h2, h3, p, .menu-card, .testimonial-card, .form-group'),
      {{ opacity: 0, y: 40 }},
      {{ opacity: 1, y: 0, duration: 0.8, stagger: 0.1, ease: 'power3.out',
         scrollTrigger: {{ trigger: sec, start: 'top 80%', toggleActions: 'play none none none' }}
      }}
    );
  }});
  gsap.from('.hero-content', {{ opacity:0, y:60, duration:1.2, ease:'power3.out', delay:0.5 }});
  gsap.from('nav', {{ opacity:0, y:-30, duration:0.8, ease:'power3.out' }});
}}

// ── HERO THREE.JS ─────────────────────────────────────────────
(function() {{
  const canvas = document.getElementById('heroCanvas');
  if (!canvas || typeof THREE === 'undefined') return;
  const W = canvas.offsetWidth, H = canvas.offsetHeight;
  const renderer = new THREE.WebGLRenderer({{ canvas, alpha: true, antialias: true }});
  renderer.setSize(W, H);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, W/H, 0.1, 100);
  camera.position.set(0, 0, 5);

  // Bowl base
  const bowlGeo = new THREE.SphereGeometry(1.5, 32, 32, 0, Math.PI*2, 0, Math.PI/2);
  const bowlMat = new THREE.MeshPhongMaterial({{ color:0x3d1a00, shininess:80, specular:0xC9A84C }});
  const bowl = new THREE.Mesh(bowlGeo, bowlMat);
  bowl.rotation.x = 0.2;
  scene.add(bowl);

  // Rice layer
  const riceGeo = new THREE.SphereGeometry(1.4, 32, 16, 0, Math.PI*2, 0, Math.PI/2.5);
  const riceMat = new THREE.MeshPhongMaterial({{ color:0xf5e6c8, shininess:30 }});
  const rice = new THREE.Mesh(riceGeo, riceMat);
  rice.position.y = 0.1;
  scene.add(rice);

  // Saffron top layer
  const saffronGeo = new THREE.SphereGeometry(1.35, 32, 16, 0, Math.PI*2, 0, Math.PI/3);
  const saffronMat = new THREE.MeshPhongMaterial({{ color:0xC9A84C, shininess:20 }});
  const saffron = new THREE.Mesh(saffronGeo, saffronMat);
  saffron.position.y = 0.25;
  scene.add(saffron);

  // Steam particles
  const particleCount = 200;
  const positions = new Float32Array(particleCount * 3);
  const velocities = [];
  for (let i = 0; i < particleCount; i++) {{
    positions[i*3]   = (Math.random()-0.5) * 2;
    positions[i*3+1] = Math.random() * 3 + 1;
    positions[i*3+2] = (Math.random()-0.5) * 2;
    velocities.push({{ x:(Math.random()-0.5)*0.003, y:0.005+Math.random()*0.008, z:(Math.random()-0.5)*0.003 }});
  }}
  const particleGeo = new THREE.BufferGeometry();
  particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  const particleMat = new THREE.PointsMaterial({{ color:0xf5f0e8, size:0.06, transparent:true, opacity:0.4 }});
  const particles = new THREE.Points(particleGeo, particleMat);
  scene.add(particles);

  // Lighting
  const ambientLight = new THREE.AmbientLight(0x442200, 0.8);
  scene.add(ambientLight);
  const pointLight1 = new THREE.PointLight(0xC9A84C, 2, 10);
  pointLight1.position.set(3, 4, 3);
  scene.add(pointLight1);
  const pointLight2 = new THREE.PointLight(0x8B2500, 1, 10);
  pointLight2.position.set(-3, -2, 2);
  scene.add(pointLight2);

  let time = 0;
  function animate() {{
    requestAnimationFrame(animate);
    time += 0.01;
    bowl.rotation.y += 0.004;
    rice.rotation.y += 0.004;
    saffron.rotation.y += 0.003;
    // Animate particles
    const pos = particleGeo.attributes.position.array;
    for (let i = 0; i < particleCount; i++) {{
      pos[i*3]   += velocities[i].x;
      pos[i*3+1] += velocities[i].y;
      pos[i*3+2] += velocities[i].z;
      if (pos[i*3+1] > 5) {{
        pos[i*3]   = (Math.random()-0.5)*2;
        pos[i*3+1] = 1;
        pos[i*3+2] = (Math.random()-0.5)*2;
      }}
    }}
    particleGeo.attributes.position.needsUpdate = true;
    particleMat.opacity = 0.3 + Math.sin(time)*0.1;
    renderer.render(scene, camera);
  }}
  animate();

  window.addEventListener('resize', () => {{
    const W2 = canvas.offsetWidth, H2 = canvas.offsetHeight;
    renderer.setSize(W2, H2);
    camera.aspect = W2/H2;
    camera.updateProjectionMatrix();
  }});
}})();

// ── SIGNATURE THREE.JS ────────────────────────────────────────
(function() {{
  const canvas = document.getElementById('signatureCanvas');
  if (!canvas || typeof THREE === 'undefined') return;
  const W = canvas.offsetWidth, H = canvas.offsetHeight;
  const renderer = new THREE.WebGLRenderer({{ canvas, alpha: true, antialias: true }});
  renderer.setSize(W, H);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, W/H, 0.1, 100);
  camera.position.set(0, 0, 6);
  // Orbiting spice particles
  const count = 300;
  const geo = new THREE.BufferGeometry();
  const pos = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {{
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const r = 2 + Math.random() * 1.5;
    pos[i*3] = r * Math.sin(phi) * Math.cos(theta);
    pos[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
    pos[i*3+2] = r * Math.cos(phi);
  }}
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const mat = new THREE.PointsMaterial({{ color:0xC9A84C, size:0.05, transparent:true, opacity:0.6 }});
  const pts = new THREE.Points(geo, mat);
  scene.add(pts);
  scene.add(new THREE.AmbientLight(0xffffff, 0.5));
  function animate() {{
    requestAnimationFrame(animate);
    pts.rotation.y += 0.003;
    pts.rotation.x += 0.001;
    renderer.render(scene, camera);
  }}
  animate();
}})();

// ── MAGNETIC BUTTON ───────────────────────────────────────────
const ctaBtn = document.getElementById('ctaBtn');
if (ctaBtn) {{
  ctaBtn.addEventListener('mousemove', function(e) {{
    const rect = this.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width/2;
    const y = e.clientY - rect.top - rect.height/2;
    this.style.transform = `translate(${{x*0.3}}px,${{y*0.3}}px)`;
  }});
  ctaBtn.addEventListener('mouseleave', function() {{
    this.style.transform = '';
  }});
}}

// ── MENU FILTER ───────────────────────────────────────────────
function filterMenu(cat) {{
  const cards = document.querySelectorAll('.menu-card');
  cards.forEach(card => {{
    if (cat === 'all' || card.dataset.cat === cat) {{
      card.style.display = 'block';
      card.style.animation = 'none';
      card.offsetHeight;
      card.style.animation = '';
    }} else {{
      card.style.display = 'none';
    }}
  }});
}}

// ── MODAL ─────────────────────────────────────────────────────
const emojis = {{ 'Dum Biryani':'🍲','Saffron Mutton':'🥘','Seekh Kebab':'🍢','Galouti Kebab':'🥩','Shahi Tukda':'🍮','Gulab Phirni':'🌹' }};
function openModal(title, desc, price) {{
  const overlay = document.getElementById('menuModal');
  if (!overlay) return;
  document.getElementById('modalEmoji').textContent = emojis[title] || '🍽️';
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalDesc').textContent = desc;
  document.getElementById('modalPrice').textContent = price;
  overlay.classList.add('active');
  document.body.style.overflow = 'hidden';
}}
function closeModal() {{
  const overlay = document.getElementById('menuModal');
  if (overlay) overlay.classList.remove('active');
  document.body.style.overflow = '';
}}
document.addEventListener('keydown', e => {{ if (e.key === 'Escape') closeModal(); }});

// ── BOOKING FORM ──────────────────────────────────────────────
function submitBooking() {{
  const name = document.getElementById('fname');
  const email = document.getElementById('femail');
  if (name && !name.value.trim()) {{ name.focus(); return; }}
  if (email && !email.value.trim()) {{ email.focus(); return; }}
  const success = document.getElementById('bookingSuccess');
  if (success) {{
    success.style.display = 'block';
    if (typeof gsap !== 'undefined') gsap.from(success, {{ opacity:0, y:20, duration:0.5 }});
  }}
}}

// ── FLOATING LABELS ───────────────────────────────────────────
document.querySelectorAll('.form-group input, .form-group textarea').forEach(input => {{
  const label = input.nextElementSibling;
  if (!label) return;
  input.addEventListener('focus', () => {{ if(label) {{ label.style.top='-0.5rem';label.style.fontSize='0.75rem';label.style.color='{primary}'; }} }});
  input.addEventListener('blur', () => {{
    if (!input.value && label) {{ label.style.top='1rem';label.style.fontSize='0.9rem';label.style.color='rgba(245,240,232,0.5)'; }}
  }});
}});

// ── SMOOTH SECTION HIGHLIGHT IN NAV ───────────────────────────
const sections = document.querySelectorAll('section[id]');
const navLinks = document.querySelectorAll('.nav-links a');
window.addEventListener('scroll', () => {{
  let current = '';
  sections.forEach(sec => {{
    if (window.scrollY >= sec.offsetTop - 200) current = sec.id;
  }});
  navLinks.forEach(a => {{
    a.style.color = a.getAttribute('href') === '#'+current ? '{primary}' : '';
  }});
}});
"""

js = js_core
print(f"  JS: {len(js)} chars")

# ─── ASSEMBLE ─────────────────────────────────────────────────
print("\nAssembling final HTML...")
fonts_url = "%7C".join([f.replace(" ", "+") + ":wght@300;400;600;700;900" for f in fonts])
google_fonts_url = f"https://fonts.googleapis.com/css2?{'&'.join(['family=' + f.replace(' ', '+') + ':wght@300;400;600;700;900' for f in fonts])}&display=swap"

final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{plan['site_name']} — {plan.get('tagline','Luxury Indian Fine Dining')}">
    <title>{plan['site_name']} — Royal Biryani House</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="{google_fonts_url}" rel="stylesheet">
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

# Validate output
if len(final_html) < 5000:
    print("WARNING: Output seems too small, something may have gone wrong!")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

size = len(final_html)
print(f"\n{'='*60}")
print(f"SUCCESS! {size:,} chars ({size//1024} KB)")
print(f"Sections built: {len(sections_html)}")
print(f"Three.js: ✓  GSAP: ✓  Fonts: {', '.join(fonts)}")
print(f"{'='*60}")