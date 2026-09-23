#!/usr/bin/env python3
"""
I-XI Labs site generator.

One content source, two emitters:
  emit_static()   -> five standalone .html files for GitHub Pages (real URLs)
  emit_artifact() -> one page with hash-routed tabs, for the hosted artifact

Why a generator for a five-page static site: the nav, masthead and colophon
appear on every page. Hand-duplicating them means a nav change is a five-file
edit and they drift. This keeps one source of truth and still emits plain HTML
with no runtime dependency -- the output needs no build step to SERVE, only to
regenerate. Edit the emitted HTML directly if you prefer; nothing depends on
re-running this.

    python3 build.py            # writes ./site/ and ./artifact/index.html
"""
import os, html

SITE = "site"
ART = "artifact"

# ---------------------------------------------------------------- navigation
# (slug, label, filename). Order is the nav order.
NAV = [
    ("index",    "Overview",  "index.html"),
    ("research", "Research",  "research.html"),
    ("notes",    "Notes",     "notes.html"),
    ("tools",    "Tools",     "tools.html"),
    ("log",      "Lab Log",   "log.html"),
]

# Secondary / off-site links. Deliberately separated from NAV so they render
# de-weighted and right-aligned rather than as peers of the research surfaces.
SOCIAL = [
    ("GitHub",    "https://github.com/Invariant-Xi-Labs", False),
]

# ------------------------------------------------------------------- styling
CSS = r"""
:root{
  color-scheme:light;
  --paper:#FAFAF9; --paper-2:#F2F1EE;
  --ink:#16181C; --ink-2:#4A4F57; --ink-3:#767B83;
  --rule:#E0DFDB; --rule-2:#C9C7C1;
  --accent:#1C3F6E; --accent-soft:#E8EDF4;
  --enforced:#2D6A4F; --declared:#8A5D14; --open:#6B7079;
  --measure:68ch;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;
  --paper:#0F1115; --paper-2:#171A20;
  --ink:#E8E9EB; --ink-2:#A4AAB3; --ink-3:#787E87;
  --rule:#262A31; --rule-2:#393F48;
  --accent:#8FB3E0; --accent-soft:#16202E;
  --enforced:#6BBF95; --declared:#D2A552; --open:#8B919A;
}}
:root[data-theme="dark"]{
  color-scheme:dark;
  --paper:#0F1115; --paper-2:#171A20;
  --ink:#E8E9EB; --ink-2:#A4AAB3; --ink-3:#787E87;
  --rule:#262A31; --rule-2:#393F48;
  --accent:#8FB3E0; --accent-soft:#16202E;
  --enforced:#6BBF95; --declared:#D2A552; --open:#8B919A;
}
*{box-sizing:border-box}
body{
  background:var(--paper); color:var(--ink);
  font-family:"IBM Plex Serif",Charter,Georgia,serif;
  font-size:1.125rem; line-height:1.62;
  -webkit-font-smoothing:antialiased;
  padding-inline:20px; padding-block:0;
}
.sheet{max-width:calc(var(--measure) + 13rem);margin-inline:auto}
.mono{font-family:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace}

/* ---------------- nav ---------------- */
.topbar{
  position:sticky; top:env(safe-area-inset-top,0px); z-index:20;
  background:var(--paper); border-bottom:1px solid var(--rule);
  margin-inline:-20px; padding-inline:20px;
}
.topbar-in{
  max-width:calc(var(--measure) + 13rem); margin-inline:auto;
  display:flex; align-items:center; gap:1.5rem;
  min-height:3.25rem; overflow-x:auto; scrollbar-width:none;
}
.topbar-in::-webkit-scrollbar{display:none}
.navgroup{display:flex;align-items:center;gap:1.35rem}
.navgroup.secondary{margin-left:auto;padding-left:1.35rem;border-left:1px solid var(--rule);gap:1rem}
.navlink{
  font-family:"IBM Plex Mono",monospace; font-size:.76rem;
  letter-spacing:.11em; text-transform:uppercase;
  color:var(--ink-2); text-decoration:none; white-space:nowrap;
  padding-block:.3rem; border-bottom:2px solid transparent;
}
.navlink:hover{color:var(--ink)}
.navlink[aria-current="page"]{color:var(--ink);border-bottom-color:var(--accent);font-weight:500}
.navgroup.secondary .navlink{font-size:.7rem;color:var(--ink-3);letter-spacing:.09em}
.navgroup.secondary .navlink:hover{color:var(--accent)}
.navlink:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:2px}

/* ---------------- masthead ---------------- */
.masthead{padding-block:3.5rem 0}
.wordmark{
  font-family:"IBM Plex Mono",monospace; font-weight:600;
  font-size:clamp(2.1rem,6vw,3.1rem); letter-spacing:.14em;
  line-height:1.05; margin:0; color:var(--ink);
}
.wordmark .hyphen{color:var(--accent)}
.subtitle{
  font-family:"IBM Plex Mono",monospace; font-size:.8rem;
  letter-spacing:.16em; text-transform:uppercase;
  color:var(--ink-3); margin:.85rem 0 0;
}
.pagetitle{
  font-family:"IBM Plex Mono",monospace; font-size:.74rem;
  letter-spacing:.16em; text-transform:uppercase; color:var(--accent);
  margin:0 0 .5rem;
}
.statusblock{
  margin-top:2.5rem; border-top:2px solid var(--ink);
  border-bottom:1px solid var(--rule);
  display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
}
.statusblock div{padding:.9rem 1.1rem .95rem 0;border-right:1px solid var(--rule)}
.statusblock div:last-child{border-right:0}
.statusblock dt{
  font-family:"IBM Plex Mono",monospace; font-size:.66rem;
  letter-spacing:.14em; text-transform:uppercase;
  color:var(--ink-3); margin:0 0 .3rem;
}
.statusblock dd{font-family:"IBM Plex Mono",monospace;font-size:.82rem;margin:0;color:var(--ink)}

/* ---------------- sections ---------------- */
section{padding-block:3.2rem;border-bottom:1px solid var(--rule)}
section:last-of-type{border-bottom:0}
.secnum{
  font-family:"IBM Plex Mono",monospace; font-size:.72rem;
  letter-spacing:.16em; color:var(--accent); display:block; margin-bottom:.55rem;
}
h2{font-size:1.42rem;font-weight:600;margin:0 0 1.3rem;text-wrap:balance;line-height:1.25}
h3{font-size:1.03rem;font-weight:600;margin:0 0 .35rem;line-height:1.35}
p{margin:0 0 1.15rem;max-width:var(--measure)}
p:last-child{margin-bottom:0}
.lede{font-size:1.28rem;line-height:1.55}
.lede em{font-style:italic;color:var(--accent)}
a{color:var(--accent);text-decoration-thickness:1px;text-underline-offset:.18em}
a:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:2px}

/* ---------------- entries (programs, disclosures, notes, tools) ------------- */
.entry{
  padding-block:1.6rem; border-top:1px solid var(--rule);
  display:grid; grid-template-columns:11rem 1fr; gap:0 2rem; align-items:start;
}
.entry:first-of-type{border-top:1px solid var(--rule-2)}
/* Close the group with a rule, the way a table closes. Without it a section
   trails off into its own bottom padding and reads as dead space. */
.entry:last-of-type{border-bottom:1px solid var(--rule-2)}
.desig{
  font-family:"IBM Plex Mono",monospace; font-size:.74rem;
  letter-spacing:.1em; color:var(--ink-3); padding-top:.28rem; line-height:1.5;
}
.desig .st{display:block;margin-top:.45rem}
.entry p{font-size:1rem;color:var(--ink-2);margin-bottom:.7rem}
.stack{font-family:"IBM Plex Mono",monospace;font-size:.74rem;color:var(--ink-3);margin:0}
.proglink{font-family:"IBM Plex Mono",monospace;font-size:.76rem;display:inline-block;margin-top:.55rem}

.chip{
  font-family:"IBM Plex Mono",monospace; font-size:.64rem;
  letter-spacing:.12em; text-transform:uppercase;
  padding:.15rem .45rem; border:1px solid currentColor;
  border-radius:2px; white-space:nowrap; font-weight:500;
}
.c-enforced{color:var(--enforced)}
.c-declared{color:var(--declared)}
.c-open{color:var(--open)}

/* disclosure timeline */
.timeline{
  margin:.9rem 0 0; padding:0; list-style:none;
  border-left:2px solid var(--rule-2); padding-left:1rem;
}
.timeline li{
  font-family:"IBM Plex Mono",monospace; font-size:.76rem;
  color:var(--ink-2); padding-block:.22rem;
  display:grid; grid-template-columns:7.5rem 1fr; gap:0 .75rem;
}
.timeline li span:first-child{color:var(--ink-3)}

/* ---------------- state model list ---------------- */
.states{margin:0;padding:0;list-style:none;border-top:1px solid var(--rule-2)}
.states li{
  display:grid; grid-template-columns:8.5rem 1fr; gap:0 2rem;
  padding-block:1.1rem; border-bottom:1px solid var(--rule); align-items:start;
}
.states .def{font-size:1rem;color:var(--ink-2);max-width:var(--measure)}
.states .def b{color:var(--ink);font-weight:600}

/* ---------------- empty + editor states ---------------- */
.empty{
  border:1px solid var(--rule-2); background:var(--paper-2);
  padding:1.6rem 1.4rem; text-align:left;
}
.empty .tag{
  font-family:"IBM Plex Mono",monospace; font-size:.66rem;
  letter-spacing:.13em; text-transform:uppercase;
  color:var(--ink-3); display:block; margin-bottom:.5rem;
}
.empty p{font-size:.98rem;color:var(--ink-2);margin:0;max-width:var(--measure)}
.ednote{border:1px dashed var(--declared);background:var(--paper-2);padding:1.15rem 1.25rem;margin-top:1.2rem}
.ednote .tag{
  font-family:"IBM Plex Mono",monospace; font-size:.66rem;
  letter-spacing:.13em; text-transform:uppercase; color:var(--declared);
  display:block; margin-bottom:.5rem; font-weight:600;
}
.ednote p{font-size:.95rem;color:var(--ink-2);margin-bottom:0;max-width:none}
.ednote code{font-size:.85em;background:var(--accent-soft);padding:.08em .35em;border-radius:2px}

/* ---------------- contact + colophon ---------------- */
.contact{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:1.5rem 2rem}
.contact dt{
  font-family:"IBM Plex Mono",monospace; font-size:.66rem;
  letter-spacing:.14em; text-transform:uppercase; color:var(--ink-3); margin-bottom:.35rem;
}
.contact dd{margin:0;font-size:.95rem;font-family:"IBM Plex Mono",monospace;word-break:break-word}
.colophon{
  padding-block:2.6rem 4rem; border-top:2px solid var(--ink); margin-top:1rem;
  font-family:"IBM Plex Mono",monospace; font-size:.72rem;
  color:var(--ink-3); line-height:1.85;
}
.colophon .mark{display:inline-block;vertical-align:-.18em;width:1.55rem;margin-right:.45rem;color:var(--ink-2)}

@media (max-width:640px){
  .entry,.states li,.timeline li{grid-template-columns:1fr;gap:.55rem 0}
  .desig{padding-top:0}
  .desig .st{display:inline-block;margin-top:0;margin-left:.6rem}
  .statusblock div{border-right:0;border-bottom:1px solid var(--rule);padding-right:0}
  .statusblock div:last-child{border-bottom:0}
  .masthead{padding-block:2.4rem 0}
  .navgroup.secondary{border-left:0;padding-left:0}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

MARK_SVG = ('<svg class="mark" viewBox="0 0 1574 860" fill="currentColor" role="img" '
            'aria-label="AERGUIIS mark"><path d="M0 0H180V700H0Z M0 109H560V264H0Z '
            'M0 436H560V591H0Z M750 18H1414V682H750Z M876 144V556H1288V144H876Z" '
            'transform="translate(80,80)"/></svg>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Serif:ital,wght@0,400;0,500;0,600;1,400'
         '&display=swap">')

MASTHEAD = '''<header class="masthead">
  <h1 class="wordmark">I<span class="hyphen">&#8211;</span>XI&nbsp;LABS</h1>
  <p class="subtitle">Independent Security Research &middot; Formal Assurance</p>
  <dl class="statusblock">
    <div><dt>Principal</dt><dd>Alec Sanchez</dd></div>
    <div><dt>Discipline</dt><dd>Detection Eng. / Platform Security</dd></div>
    <div><dt>Location</dt><dd>Houston, TX</dd></div>
    <div><dt>Status</dt><dd>Active</dd></div>
  </dl>
</header>'''

COLOPHON = f'''<footer class="colophon">
  {MARK_SVG}
  I-XI LABS &middot; Independent security research<br>
  Set in IBM Plex Serif and IBM Plex Mono. No trackers, no analytics, no cookies.<br>
  Assurance markers follow the state model on the Overview page.
</footer>'''


def empty(tag, text):
    return f'<div class="empty"><span class="tag">{tag}</span><p>{text}</p></div>'


def ednote(text):
    return (f'<div class="ednote"><span class="tag">Editor&rsquo;s note &mdash; remove before '
            f'publication</span><p>{text}</p></div>')


# ------------------------------------------------------------------- content
PAGES = {}

PAGES["index"] = ("Overview", f'''
<section>
  <span class="secnum">&sect; 1 &nbsp; SCOPE</span>
  <h2>What this lab does</h2>
  <p class="lede">I-XI Labs is a single-operator research practice working on the problem of
  <em>stating a security property precisely enough that a machine can check it</em> &mdash;
  and then building the machinery that checks it.</p>
  <p>The work spans three areas that share that spine: detection engineering validated
  against adversarial input rather than against a rule count; platform security research on
  macOS and Apple Silicon; and formal assurance methodology &mdash; the vocabulary and
  structure for saying what a system has actually been shown to do, as distinct from what its
  documentation claims.</p>
  <p>The practice is architectural and defensive. Adversarial technique is used to validate
  controls and to define vulnerability classes formally, not as an offering.</p>
</section>

<section>
  <span class="secnum">&sect; 2 &nbsp; METHOD</span>
  <h2>Assurance states</h2>
  <p>Most security documentation conflates three different things: a control that runs, a
  control that is written down, and a control that someone intends to build. The lab keeps
  them separate, and every claim it publishes carries one of these markers.</p>
  <ul class="states">
    <li><span class="chip c-enforced">Enforced</span><span class="def"><b>A running mechanical
    check verifies this.</b> The check is named, it executes, and its failure is observable.
    This is the only state that constitutes evidence.</span></li>
    <li><span class="chip c-declared">Declared</span><span class="def"><b>Asserted, not
    verified.</b> The property is specified and may well hold, but nothing mechanically
    confirms it. A policy document produces this state, never the one above.</span></li>
    <li><span class="chip c-open">Open</span><span class="def"><b>Unresolved.</b> The question
    is stated and the evidence that would settle it is named. Naming a risk is not mitigating
    it, and this marker says so explicitly.</span></li>
  </ul>
</section>

<section>
  <span class="secnum">&sect; 3 &nbsp; CONTACT</span>
  <h2>Correspondence</h2>
  <p>Research correspondence, collaboration, and vulnerability reports concerning this
  lab&rsquo;s own published work are welcome.</p>
  <dl class="contact">
    <div><dt>Code</dt><dd><a href="https://github.com/Invariant-Xi-Labs">github.com/Invariant-Xi-Labs</a></dd></div>
    <div><dt>Professional</dt><dd><a href="https://linkedin.com/in/alecasanchez">linkedin.com/in/alecasanchez</a></dd></div>
  </dl>
</section>
''')

PAGES["research"] = ("Research", f'''
<section>
  <span class="secnum">&sect; 1 &nbsp; PROGRAMS</span>
  <h2>Research programs</h2>

  <div class="entry">
    <div class="desig">OSIM<span class="st"><span class="chip c-enforced">Published</span></span></div>
    <div>
      <h3>Orthogonal Systems Invariance Method</h3>
      <p>A systems-based security architecture framework. OSIM treats detection coverage as a
      set of invariants over system state rather than a catalogue of signatures, and validates
      those invariants adversarially against a running environment.</p>
      <p class="stack">Zero Trust architecture &middot; invariant-based detection &middot; adversarial validation</p>
      <a class="proglink" href="https://github.com/osim-framework/osim-framework">github.com/osim-framework/osim-framework &#8599;</a>
    </div>
  </div>

  <div class="entry">
    <div class="desig">OSIM&#8209;CORE<span class="st"><span class="chip c-enforced">Published</span></span></div>
    <div>
      <h3>Validation environment</h3>
      <p>The production homelab OSIM is validated against &mdash; a multi-zone network with an
      Active Directory domain and separated blue and red node architecture. Detections are
      written, then attacked, then kept or discarded on the evidence.</p>
      <p class="stack">OPNsense &middot; Proxmox &middot; Wazuh SIEM &middot; TheHive &middot; MISP</p>
      <a class="proglink" href="https://github.com/osim-framework/osim-core">github.com/osim-framework/osim-core &#8599;</a>
    </div>
  </div>

  <div class="entry">
    <div class="desig">AEROS / AERGUIIS<span class="st"><span class="chip c-declared">In development</span></span></div>
    <div>
      <h3>Assurance architecture</h3>
      <p>The successor lineage to OSIM: a formal definition of vulnerability, an assurance
      vocabulary with machine-checkable states, and the domain tracks that carry them.
      Specifications are numbered and versioned; none are published yet.</p>
      <p class="stack">Formal vulnerability definition &middot; assurance state model &middot; kernel runtime integrity</p>
    </div>
  </div>
</section>

<section>
  <span class="secnum">&sect; 2 &nbsp; DISCLOSURE</span>
  <h2>Coordinated disclosure</h2>
  <p>Findings affecting third-party software are reported to the vendor and held until the
  vendor ships a fix or the disclosure window closes. Each published finding is listed here
  with its full timeline &mdash; report, acknowledgement, fix, and public advisory.</p>

  {empty("No entries", "No findings have been published. This section is maintained; an empty "
         "state here means nothing is disclosed, not that nothing is listed.")}
</section>
''')

PAGES["notes"] = ("Notes", f'''
<section>
  <span class="secnum">&sect; 1 &nbsp; NOTES</span>
  <h2>Working notes</h2>
  <p>Short technical writing: things established while working, recorded at the point they
  were established. Notes are dated and carry an assurance marker like anything else here
  &mdash; a note that records a measurement is not the same as a note that records a hunch.</p>

  {empty("No entries", "No notes published yet. Each entry is a dated heading, two to six "
         "paragraphs, and a marker stating whether the claim was verified or merely observed.")}
</section>
''')

PAGES["tools"] = ("Tools", f'''
<section>
  <span class="secnum">&sect; 1 &nbsp; TOOLS</span>
  <h2>Released tooling</h2>
  <p>Software released from lab work. Each entry states what the tool checks, what it does
  not check, and the platforms it has actually been run on &mdash; not the platforms it
  theoretically supports.</p>

  <div class="entry">
    <div class="desig">OSIM&#8209;CORE<span class="st"><span class="chip c-enforced">Published</span></span></div>
    <div>
      <h3>Lab topology and detection stack</h3>
      <p>The deployment definitions for the validation environment: multi-zone network, AD
      domain, and the blue/red node split. Usable as a reference build for anyone standing up
      a detection-engineering lab.</p>
      <p class="stack">OPNsense &middot; Proxmox &middot; Wazuh &middot; TheHive &middot; MISP</p>
      <a class="proglink" href="https://github.com/osim-framework/osim-core">github.com/osim-framework/osim-core &#8599;</a>
    </div>
  </div>
</section>
''')

PAGES["log"] = ("Lab Log", f'''
<section>
  <span class="secnum">&sect; 1 &nbsp; LAB LOG</span>
  <h2>Build log</h2>
  <p>The physical and operational side of the lab: rack and network builds, hardware, topology
  changes, and the occasional record of something going wrong in an instructive way. Less
  formal than Notes, and it does not carry assurance markers &mdash; nothing here is a claim.</p>

  {empty("No entries", "No log entries yet. Photographs of the rack build, the network "
         "topology, and the blue/red node separation belong here.")}
</section>
''')


# ------------------------------------------------------------------ emitters
def nav_html(current, hashmode=False):
    items = []
    for slug, label, fname in NAV:
        href = f"#{slug}" if hashmode else fname
        cur = ' aria-current="page"' if slug == current else ""
        extra = f' data-tab="{slug}"' if hashmode else ""
        items.append(f'<a class="navlink" href="{href}"{cur}{extra}>{label}</a>')
    soc = []
    for label, href, _ in SOCIAL:
        soc.append(f'<a class="navlink" href="{href}">{label} &#8599;</a>')
    return (f'<nav class="topbar" aria-label="Primary"><div class="topbar-in">'
            f'<div class="navgroup">{"".join(items)}</div>'
            f'<div class="navgroup secondary">{"".join(soc)}</div>'
            f'</div></nav>')


def emit_static():
    os.makedirs(SITE, exist_ok=True)
    os.makedirs(os.path.join(SITE, "img"), exist_ok=True)
    for slug, label, fname in NAV:
        title, body = PAGES[slug]
        pt = "" if slug == "index" else f'<p class="pagetitle">{title}</p>'
        doc = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{"I-XI Labs" if slug=="index" else f"{title} &middot; I-XI Labs"}</title>
<meta name="description" content="I-XI Labs — independent security research and formal assurance.">
<meta property="og:title" content="I-XI Labs">
<meta property="og:type" content="website">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns=&apos;http://www.w3.org/2000/svg&apos; viewBox=&apos;0 0 1000 1000&apos;%3E%3Cpath fill=&apos;%2316181C&apos; d=&apos;M220 150h180v700h-180z M220 259h560v155h-560z M220 586h560v155h-560z&apos;/%3E%3C/svg%3E">
{FONTS}
<style>html{{-webkit-text-size-adjust:100%}}body{{margin:0}}img{{max-width:100%}}
:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
{CSS}</style>
</head>
<body>
{nav_html(slug)}
<div class="sheet">
{MASTHEAD if slug=="index" else f'<header class="masthead">{pt}<h1 class="wordmark">I<span class="hyphen">&#8211;</span>XI&nbsp;LABS</h1></header>'}
{body}
{COLOPHON}
</div>
</body>
</html>
'''
        with open(os.path.join(SITE, fname), "w") as f:
            f.write(doc)
        print(f"  {SITE}/{fname}  ({len(doc)} bytes)")


def emit_artifact():
    os.makedirs(ART, exist_ok=True)
    panels = []
    for slug, label, _ in NAV:
        title, body = PAGES[slug]
        pt = "" if slug == "index" else f'<p class="pagetitle">{title}</p>'
        head = MASTHEAD if slug == "index" else (
            f'<header class="masthead">{pt}<h1 class="wordmark">'
            f'I<span class="hyphen">&#8211;</span>XI&nbsp;LABS</h1></header>')
        panels.append(f'<div class="panel" id="p-{slug}"{"" if slug=="index" else " hidden"}>'
                      f'{head}{body}</div>')

    doc = f'''<title>I-XI Labs</title>
{FONTS}
<style>{CSS}</style>
{nav_html("index", hashmode=True)}
<div class="sheet">
{"".join(panels)}
{COLOPHON}
</div>
<script>
(function(){{
  var slugs = {[s for s, _, _ in NAV]!r};
  function show(slug){{
    if (slugs.indexOf(slug) === -1) slug = slugs[0];
    slugs.forEach(function(s){{
      var p = document.getElementById('p-' + s);
      if (p) p.hidden = (s !== slug);
    }});
    document.querySelectorAll('.navlink[data-tab]').forEach(function(a){{
      if (a.dataset.tab === slug) a.setAttribute('aria-current','page');
      else a.removeAttribute('aria-current');
    }});
    window.scrollTo(0,0);
  }}
  window.addEventListener('hashchange', function(){{ show(location.hash.slice(1)); }});
  show(location.hash.slice(1) || 'index');
}})();
</script>
'''
    with open(os.path.join(ART, "index.html"), "w") as f:
        f.write(doc)
    print(f"  {ART}/index.html  ({len(doc)} bytes)")


if __name__ == "__main__":
    print("static site:")
    emit_static()
    print("artifact:")
    emit_artifact()
