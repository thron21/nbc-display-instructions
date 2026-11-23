"""Rebuild the NBC display booklet: recoloured model, sub-steps of up to 14 pieces, pictures rendered with
three.js (r3.Renderer) instead of LeoCAD. Keeps the page's head, scripts and features; regenerates
<main>, MOCKIT_HL, img/ and 3d/model.js + parts.js."""
import os, sys, re, json, html, shutil, io
import numpy as np
from PIL import Image
KIT = '/home/claude/thron21/moc-instruction-kit'
sys.path.insert(0, KIT); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mockit import ldraw, render, outlines, geometry
from mockit.plan import footprint, where_text, letters
from r3 import Renderer

REPO = '/home/claude/nbc-display-instructions'
MODEL = sys.argv[1] if len(sys.argv) > 1 else 'v4_recol.ldr'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'site'
MPS = 14
WORK = 'work'
cfg = json.load(open(f'{REPO}/source/config.json'))
frame = tuple(cfg['frame']); bg = tuple(int(cfg['background'][i:i + 2], 16) for i in (1, 3, 5)); pale = cfg['pale']
lib = ldraw.Library('lib')
title, P = ldraw.read_model(MODEL, lib)

# step titles: the last "0 // ..." comment before each STEP's pieces
titles = {}; step = 0; last = None; seen = False
for ln in open(MODEL).read().split('\n'):
    s = ln.strip()
    if s.startswith('0 // '): last = s[5:].strip()
    elif s.startswith('0 STEP'):
        step += 1; seen = False
    elif s.startswith('1 ') and not seen:
        titles[step] = last; seen = True
nsteps = max(p['step'] for p in P) + 1

los, his = zip(*[lib.bbox(p) for p in P]); lo = np.min(los, 0); hi = np.max(his, 0)
x0 = round(float(lo[0])); z0 = round(float(lo[2]))

def hexc(c):
    x = lib.colors.get(c); return x['rgb'] if x else '#888888'
def edgec(c):
    x = lib.colors.get(c)
    if not x: return '#333333'
    e = x['edge']; return e if e.startswith('#') else hexc(int(e))
def rec(p, col, edge):
    return [p['part'], *map(float, p['pos']), *map(float, np.asarray(p['M']).flatten()), col, edge]

sections = []
for s in cfg['sections']:
    a, b = s['steps']                      # 1-based STEP numbers, inclusive
    idx = [i for i, p in enumerate(P) if a - 1 <= p['step'] <= b - 1]
    bigs = {}
    for i in idx: bigs.setdefault(P[i]['step'], []).append(i)
    steps = []
    for n, (stp, ids) in enumerate(sorted(bigs.items()), start=1):
        chunks = [ids[k:k + MPS] for k in range(0, len(ids), MPS)]
        for ci, ch in enumerate(chunks):
            sid = f'{s["id"]}{n}' + (letters(ci) if len(chunks) > 1 else '')
            label = f'{n}' + (letters(ci) if len(chunks) > 1 else '')
            ticks = []
            for j, pi in enumerate(ch):
                p = P[pi]; c, r, _, _ = footprint(lib, p, x0, z0)
                col = lib.colors.get(p['color'], dict(name=f'Colour {p["color"]}', rgb='#888888'))
                ticks.append(dict(k=f'{sid}-{j}', piece=pi, part=p['part'], color=p['color'], name=lib.part_name(p['part']),
                                  colorname=col['name'], rgb=col['rgb'], wh=where_text(c, r)))
            steps.append(dict(id=sid, big=n, label=label, nsub=len(chunks), ticks=ticks, title=titles.get(stp) or f'Step {n}', gstep=stp))
    sections.append(dict(id=s['id'], name=s['name'], pieces=P, steps=steps, grid=[64, 48], last_step=b - 1))
print('sub-steps', sum(len(s['steps']) for s in sections), 'max per sub-step', max(len(st['ticks']) for s in sections for st in s['steps']))

cam = render.Camera(lib, P, cfg.get('camera', {}), frame[0])
print('camera', cam.W, cam.H, round(cam.pps))
img = os.path.join(OUT, 'img'); os.makedirs(img, exist_ok=True); os.makedirs(os.path.join(img, 'parts'), exist_ok=True)
R = Renderer()
base_job = dict(W=cam.W, H=cam.H, fov=cam.fov, pos=list(map(float, cam.pos)), target=list(map(float, cam.t)), near=10, far=float(cam.d * 4 + 5000))
hl = {}; done = {}
for sec in sections:
    rdir = os.path.join(WORK, sec['id']); os.makedirs(rdir, exist_ok=True)
    for n_, st in enumerate(sec['steps']):
        cur = [t['piece'] for t in st['ticks']]
        first = min(P[i]['step'] for i in cur); curset = set(cur)
        prior = [i for i, p in enumerate(P) if p['step'] < first or (p['step'] == first and i < min(cur) and i not in curset)]
        if os.path.exists(f'{rdir}/{st["id"]}_id.png') and all(os.path.exists(f'{rdir}/{t["k"]}_solo.png') for t in st['ticks']) and os.path.exists(f'{rdir}/{st["id"]}_base.png'):
            continue
        pcs = [rec(P[i], pale, '#8C93A0') for i in prior] + [rec(P[i], hexc(P[i]['color']), edgec(P[i]['color'])) for i in cur]
        m, _ = R.job(dict(base_job, pieces=pcs, mode='shaded')); open(f'{rdir}/{st["id"]}_base.png', 'wb').write(m)
        pcs = [rec(P[i], '#000000', '#000000') for i in prior] + [rec(P[i], '#%02X%02X%02X' % render.id_rgb(k + 1), '#000000') for k, i in enumerate(cur)]
        m, solos = R.job(dict(base_job, pieces=pcs, mode='flat', solo=list(range(len(prior), len(prior) + len(cur)))))
        open(f'{rdir}/{st["id"]}_id.png', 'wb').write(m)
        for t, sp in zip(st['ticks'], solos): open(f'{rdir}/{t["k"]}_solo.png', 'wb').write(sp)
        if n_ % 10 == 0: print(f'  {sec["id"]}: {n_ + 1}/{len(sec["steps"])}', flush=True)
    if not os.path.exists(f'{rdir}/done.png'):
        upto = [p for p in P if p['step'] <= sec['last_step']]
        m, _ = R.job(dict(base_job, pieces=[rec(p, hexc(p['color']), edgec(p['color'])) for p in upto], mode='shaded'))
        open(f'{rdir}/done.png', 'wb').write(m)
    h, size = outlines.make_pictures(sec, rdir, cam.W, cam.H, img, frame, bg, cfg.get('jpeg_quality', 74))
    hl.update(h); done[sec['id']] = size
    print('section', sec['id'], 'pictures done', flush=True)
# part thumbnails
pcs_ = sorted({(t['part'], t['color']) for s in sections for st in s['steps'] for t in st['ticks']})
for part, color in pcs_:
    png = R.thumb(part, hexc(color), edgec(color), 224)
    im = Image.open(io.BytesIO(png)).convert('RGBA'); bb = im.getbbox() or (0, 0, im.width, im.height)
    im = im.crop(bb); s_ = max(im.size); sq = Image.new('RGBA', (int(s_ * 1.15), int(s_ * 1.15)), (214, 199, 169, 255))
    sq.alpha_composite(im, ((sq.width - im.width) // 2, (sq.height - im.height) // 2))
    sq.convert('RGB').resize((112, 112), Image.LANCZOS).save(f'{img}/parts/{part}_{color}.jpg', quality=82)
R.close()
stats = geometry.export(lib, sections, os.path.join(OUT, '3d'), pale)
for f in ('viewer.js', 'LICENSE-three.txt'): shutil.copy(f'{REPO}/3d/{f}', f'{OUT}/3d/{f}')

# ---- page: keep the existing head + scripts, regenerate <main> and the highlight data
esc = lambda s: html.escape(str(s), quote=True)
src = open(f'{REPO}/index.html', encoding='utf-8').read()
i0 = src.find('<main class="wrap">'); i1 = src.find('</main>')
oldmain = src[i0:i1]
header = oldmain[oldmain.find('<header class="intro">'):oldmain.find('</header>') + len('</header>')]
total = sum(len(st['ticks']) for s in sections for st in s['steps'])
body = [header]
for s in sections:
    n = sum(len(st['ticks']) for st in s['steps']); bigs = sorted(set(st['big'] for st in s['steps']))
    body.append(f'<section class="sec" id="sec-{s["id"]}"><header class="sechead"><div><h2>{esc(s["name"])}</h2></div>'
                f'<p class="count">{len(bigs)} steps · {len(s["steps"])} sub-steps · {n} pieces</p></header>')
    for b in bigs:
        subs = [st for st in s['steps'] if st['big'] == b]; np_ = sum(len(st['ticks']) for st in subs)
        body.append(f'<div class="big" id="big-{s["id"]}{b}"><div class="bighead"><span class="bnum">{b}</span><div><h3>{esc(subs[0]["title"])}</h3>'
                    f'<p>{np_} piece{"s" if np_ != 1 else ""} in {len(subs)} sub-step{"s" if len(subs) != 1 else ""}</p></div></div>')
        for st in subs:
            lis = []
            for t in st['ticks']:
                k = t['k']
                lis.append(f'<li><input type="checkbox" id="{k}" data-k="{k}"><label for="{k}">'
                           f'<span class="pp" style="background-image:url(img/parts/{esc(t["part"])}_{t["color"]}.jpg)" aria-hidden="true"></span>'
                           f'<span class="pn">{esc(t["name"])} <span class="pid">{esc(t["part"])}</span></span>'
                           f'<span class="pc"><span class="sw" style="background:{t["rgb"]}"></span>{esc(t["colorname"])}</span>'
                           f'<span class="wh">{esc(t["wh"])}</span></label></li>')
            n_t = len(st['ticks'])
            body.append(f'<article class="step" id="{st["id"]}" data-sec="{s["id"]}"><div class="shot"><img src="img/{st["id"]}.jpg" alt="Sub-step {st["label"]}" loading="lazy" width="{frame[0]}" height="{frame[1]}"></div>'
                        f'<div class="side"><div class="snum">{st["label"]}</div><ul class="ticks">{"".join(lis)}</ul><p class="tot">{n_t} piece{"s" if n_t != 1 else ""}</p></div></article>')
        body.append('</div>')
    w, h = done[s['id']]
    body.append(f'<figure class="done"><img src="img/{s["id"]}_done.jpg" alt="{esc(s["name"])} finished" loading="lazy" width="{w}" height="{h}"><figcaption>{esc(s["name"])} finished</figcaption></figure></section>')
newmain = '<main class="wrap">\n' + '\n'.join(body) + '\n'
page = src[:i0] + newmain + src[i1:]
page = re.sub(r'<script>window\.MOCKIT_HL=.*?;</script>', lambda m: '<script>window.MOCKIT_HL=' + json.dumps(hl, separators=(',', ':')) + ';</script>', page, count=1, flags=re.S)
page = page.replace('"prefix": "nbcdisp3"', '"prefix": "nbcdisp4"')
sticky = '<style id="pin-picture">.step{overflow:clip}.shot{position:sticky;top:0;z-index:2}</style>'
page = page.replace('</head>', sticky + '</head>', 1)
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
json.dump(dict(sections=[dict(id=s['id'], name=s['name'], steps=s['steps']) for s in sections]), open(os.path.join(WORK, 'plan.json'), 'w'))
print('done', total, 'pieces', sum(len(s['steps']) for s in sections), 'sub-steps', stats)
