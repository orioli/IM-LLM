import yaml, html, textwrap, sys
g = yaml.safe_load(open(sys.argv[1]))
nodes = {n['id']: n for n in g['nodes']}
edges = g['edges']
COL = dict(Product='#4C72B0', Component='#55A868', Function='#C44E52', MarketNeed='#8172B2',
           Actor='#CCB974', Constraint='#64B5CD', Technology='#DD8452', Field='#937860')
W, X0, X1 = 1820, 200, 1600
BANDS = [  # type, top y, fill, label, stagger
    ('MarketNeed', 90, '#f4f1fa', 'Market needs / wants', True),
    ('Function',   290, '#fbeeee', 'Product function', True),
    ('Component',  490, '#eef6ef', 'Component', True),
    ('Technology', 690, '#fdf1e8', 'Technology', True),
    ('Field',      890, '#f3efea', 'Field', False),
]
BH = 170
H = 890 + 120 + 30
ids_of = lambda t: [i for i, n in nodes.items() if n['type'] == t]
num = lambda i: int(''.join(c for c in i if c.isdigit()) or 0)
order = {t: sorted(ids_of(t), key=num) for t, *_ in BANDS}
nbr = {i: set() for i in nodes}
for e in edges:
    nbr[e['from']].add(e['to']); nbr[e['to']].add(e['from'])
pos = {}
def place():
    for t, top, _, _, stag in BANDS:
        L = order[t]; n = len(L)
        for k, i in enumerate(L):
            x = X0 + (X1 - X0) * (k + 0.5) / n
            y = top + 45 + (60 if stag and k % 2 else 0) if stag else top + 40
            pos[i] = (x, y)
place()
seq = ['Function', 'Component', 'Technology', 'Field', 'Technology', 'Component', 'Function', 'MarketNeed']
for _ in range(6):
    for t in seq:
        def bc(i):
            xs = [pos[j][0] for j in nbr[i] if j in pos and nodes[j]['type'] in ('MarketNeed','Function','Component','Technology','Field') and nodes[j]['type'] != t]
            return sum(xs) / len(xs) if xs else pos[i][0]
        order[t].sort(key=bc); place()
pos['P1'] = (W / 2, 42)
for t, x in (('Actor', 90), ('Constraint', 1720)):
    L = sorted(ids_of(t), key=num)
    if t == 'Constraint':
        L.sort(key=lambda i: sum(pos[j][1] for j in nbr[i] if j in pos) / max(1, sum(1 for j in nbr[i] if j in pos)))
    for k, i in enumerate(L):
        pos[i] = (x, 110 + (H - 150) * (k + 0.5) / len(L))
ESTY = {'contradicts': ('#B22222', '5,4', 0.85), 'causes': ('#B22222', '5,4', 0.7),
        'partially_mitigates': ('#2f9e44', '4,3', 0.75), 'has_component': ('#c5ccd3', '', 0.35),
        'relevant_to': ('#adb5bd', '2,3', 0.5)}
out = []
out.append(f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial,sans-serif" id="G" role="img" aria-label="Innovation matrix graph">')
out.append('<defs>' + ''.join(f'<marker id="a{k}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{c}"/></marker>' for k, c in (('g', '#999'), ('r', '#B22222'), ('t', '#2f9e44'))) + '</defs>')
out.append(f'<rect width="{W}" height="{H}" fill="white"/>')
for t, top, fill, lab, _ in BANDS:
    h = BH if t != 'Field' else 110
    out.append(f'<rect x="{X0-30}" y="{top}" width="{X1-X0+60}" height="{h}" fill="{fill}" rx="6"/>')
    out.append(f'<text x="{X0-22}" y="{top+16}" font-size="13" font-weight="bold" fill="#444">{lab}</text>')
out.append(f'<text x="90" y="100" font-size="13" font-weight="bold" fill="#444" text-anchor="middle">Actors</text>')
out.append(f'<text x="1720" y="100" font-size="13" font-weight="bold" fill="#444" text-anchor="middle">Constraints</text>')
import math
for e in edges:
    a, b = pos[e['from']], pos[e['to']]
    c, d, op = ESTY.get(e['type'], ('#999', '', 0.6))
    mk = 'r' if c == '#B22222' else 't' if c == '#2f9e44' else 'g'
    dx, dy = b[0]-a[0], b[1]-a[1]; L = math.hypot(dx, dy) or 1
    r = 13
    x1, y1, x2, y2 = a[0]+dx/L*r, a[1]+dy/L*r, b[0]-dx/L*(r+2), b[1]-dy/L*(r+2)
    da = f' stroke-dasharray="{d}"' if d else ''
    same = nodes[e['from']]['type'] == nodes[e['to']]['type'] and nodes[e['from']]['type'] not in ('Actor','Constraint')
    if same:
        bulge = min(70, 18 + abs(dx) * 0.12)
        cx, cy = (x1 + x2) / 2, min(y1, y2) - bulge
        out.append(f'<path d="M{x1:.1f},{y1:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}" fill="none" stroke="{c}" stroke-width="1" class="e" data-k="{e["from"]}|{e["to"]}" style="--o:{op}"{da} marker-end="url(#a{mk})"><title>{e["from"]} {e["type"]} {e["to"]}</title></path>')
    else:
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{c}" stroke-width="1" class="e" data-k="{e["from"]}|{e["to"]}" style="--o:{op}"{da} marker-end="url(#a{mk})"><title>{e["from"]} {e["type"]} {e["to"]}</title></line>')
for i, n in nodes.items():
    x, y = pos[i]; t = n['type']
    wrapw = 15 if t in ('Component', 'Function', 'MarketNeed', 'Technology') else 18
    if t in ('Actor', 'Constraint'): wrapw = 30
    lines = textwrap.wrap(n['label'], wrapw)
    mx = 2 if t == 'Constraint' else 3
    if len(lines) > mx: lines = lines[:mx]; lines[-1] = lines[-1].rstrip(' ,') + '…'
    tip = html.escape(n['label'] + (' — ' + n['detail'] if n.get('detail') else ''))
    r = 18 if t == 'Product' else 12
    out.append(f'<g class="n" data-id="{i}" tabindex="0" role="button" aria-label="{i}"><title>{i}: {tip}</title><circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{COL[t]}"/>')
    out.append(f'<text x="{x:.1f}" y="{y+4:.1f}" font-size="9" font-weight="bold" fill="white" text-anchor="middle">{i}</text>')
    if t == 'Product':
        out.append(f'<text x="{x+28:.1f}" y="{y+5:.1f}" font-size="13" font-weight="bold" fill="#212529">{html.escape(n["label"])}</text>')
    else:
        for k, ln in enumerate(lines):
            out.append(f'<text x="{x:.1f}" y="{y+24+k*10.5:.1f}" font-size="9" fill="#333" text-anchor="middle">{html.escape(ln)}</text>')
    out.append('</g>')
out.append('</svg>')
svg = '\n'.join(out)
from collections import Counter
cnt = Counter(n['type'] for n in nodes.values())
legend_types = ''.join(f'<span class="lg"><i style="background:{COL[t]}"></i>{t} ({cnt[t]})</span>' for t in ['Field','Technology','Component','Function','MarketNeed','Actor','Constraint','Product'])
page = f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Microwave Innovation Matrix v2</title>
<style>
* {{ box-sizing: border-box; }}
body {{ font-family: Helvetica, Arial, sans-serif; margin: 0; padding: 24px; background: #fafafa; color: #212529; }}
h1 {{ font-size: 18px; margin: 0 0 4px; }}
p.subtitle {{ font-size: 13px; color: #666; margin: 0 0 18px; max-width: 1100px; line-height: 1.45; }}
.panel {{ border: 1px solid #dee2e6; border-radius: 10px; background: white; padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); max-width: 1800px; margin: 0 auto; }}
.panel h2 {{ font-size: 13px; margin: 0 0 8px; color: #495057; text-transform: uppercase; letter-spacing: 0.04em; }}
.scroll {{ overflow-x: auto; }}
.panel svg {{ width: 100%; min-width: 1100px; height: auto; display: block; }}
.legend {{ font-size: 12px; color: #555; margin: 14px auto 0; max-width: 1800px; display: flex; flex-wrap: wrap; gap: 8px 18px; align-items: center; }}
.lg {{ display: inline-flex; align-items: center; gap: 6px; }}
.lg i {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
.ln {{ display: inline-block; width: 26px; border-top: 2px solid #999; vertical-align: middle; margin-right: 6px; }}
.e {{ opacity: var(--o); transition: opacity .25s, stroke-width .25s; }}
.n {{ pointer-events: bounding-box; cursor: pointer; transition: opacity .25s; outline: none; }}
.n circle {{ transition: stroke-width .2s; }}
.n:hover circle, .n:focus-visible circle {{ stroke: #212529; stroke-width: 2; }}
#G.focus .n {{ opacity: .3; }}
#G.focus .e {{ opacity: calc(var(--o) * .3); }}
#G.focus .n.on {{ opacity: 1; }}
#G.focus .n.sel circle {{ stroke: #212529; stroke-width: 3; }}
#G.focus .e.on {{ opacity: 1; stroke-width: 2; }}
.info {{ max-width: 1800px; margin: 0 auto 12px; min-height: 44px; font-size: 13px; background: white; border: 1px solid #dee2e6; border-radius: 10px; padding: 10px 14px; display: flex; gap: 14px; align-items: center; flex-wrap: wrap; }}
.info b {{ color: #212529; }} .info .muted {{ color: #868e96; }}
.info button {{ margin-left: auto; font: inherit; font-size: 12px; border: 1px solid #ced4da; background: #f8f9fa; border-radius: 6px; padding: 4px 10px; cursor: pointer; }}
.chip {{ display: inline-block; padding: 1px 7px; border-radius: 10px; color: white; font-size: 11px; font-weight: bold; margin: 1px; }}
.note {{ font-size: 12px; color: #868e96; text-align: center; margin-top: 10px; }}
</style></head><body>
<h1>Innovation matrix: basic countertop microwave oven</h1>
<p class="subtitle">Seed graph G (<code>{g['meta']['graph_id']}</code>) laid out in Bernegger's layers: Field &rarr; Technology &rarr; Component &rarr; Function &rarr; Market need, with Actors on the left and Constraints on the right. {len(nodes)} nodes, {len(edges)} edges. Click a node to isolate its chain; hover for full labels.</p>
<div class="info" id="info"><span class="muted">Click any node to trace its chain: down to the nearest Technology node, up to the Market needs. Click it again, the background, or press Esc to reset.</span></div>
<div class="panel"><h2>Graph G &mdash; {html.escape(nodes['P1']['label'])}</h2><div class="scroll">
{svg}
</div></div>
<div class="legend">{legend_types}
<span class="lg"><span class="ln"></span>structural edge</span>
<span class="lg"><span class="ln" style="border-top:2px dashed #B22222"></span>causes / contradicts</span>
<span class="lg"><span class="ln" style="border-top:2px dashed #2f9e44"></span>partially mitigates</span>
<span class="lg"><span class="ln" style="border-top:2px dotted #adb5bd"></span>relevant to</span>
</div>
<p class="note">Faint grey lines from P1 are has_component edges.</p>
<script>
const NODES = __NODES__, EDGES = __EDGES__, COL = __COL__;
const RANK = {{Field:0, Technology:1, Component:2, Function:3, MarketNeed:4}};
const adj = {{}}; Object.keys(NODES).forEach(k => adj[k] = []);
EDGES.forEach(([a,b,t]) => {{ adj[a].push({{o:b, out:true, t}}); adj[b].push({{o:a, out:false, t}}); }});
function chain(id) {{
  const on = new Set([id]), eon = new Set(), t0 = NODES[id].type;
  const key = (a,b,out) => out ? a+'|'+b : b+'|'+a;
  if (!(t0 in RANK)) {{               // Product / Actor / Constraint: direct links only
    adj[id].forEach(x => {{ on.add(x.o); eon.add(key(id,x.o,x.out)); }});
    return {{on, eon}};
  }}
  const walk = up => {{
    const q = [id], seen = new Set([id]);
    while (q.length) {{
      const c = q.shift(), rc = RANK[NODES[c].type];
      if (!up && rc <= 1 && c !== id) continue;           // stop at the closest Technology
      for (const x of adj[c]) {{
        const ro = RANK[NODES[x.o].type]; if (ro === undefined) continue;
        let ok = up ? ro > rc : (ro < rc && ro >= 1);
        if (rc === 3 && ro === 3 && x.t === 'enables_function') ok = up ? x.out : !x.out; // function -> derived function
        if (!ok) continue;
        on.add(x.o); eon.add(key(c,x.o,x.out));
        if (!seen.has(x.o)) {{ seen.add(x.o); q.push(x.o); }}
      }}
    }}
  }};
  walk(true); walk(false);
  adj[id].forEach(x => {{ const t = NODES[x.o].type;             // direct actors / constraints
    if (t === 'Constraint' || t === 'Actor') {{ on.add(x.o); eon.add(key(id,x.o,x.out)); }} }});
  return {{on, eon}};
}}
const G = document.getElementById('G'), info = document.getElementById('info'), idle = info.innerHTML;
const nodeEls = [...G.querySelectorAll('.n')], edgeEls = [...G.querySelectorAll('.e')];
let cur = null;
function reset() {{ cur = null; G.classList.remove('focus'); nodeEls.forEach(n => n.classList.remove('on','sel')); edgeEls.forEach(e => e.classList.remove('on')); info.innerHTML = idle; }}
function select(id) {{
  if (cur === id) return reset();
  cur = id; const {{on, eon}} = chain(id);
  G.classList.add('focus');
  nodeEls.forEach(n => {{ n.classList.toggle('on', on.has(n.dataset.id)); n.classList.toggle('sel', n.dataset.id === id); }});
  edgeEls.forEach(e => e.classList.toggle('on', eon.has(e.dataset.k)));
  const order = ['MarketNeed','Function','Component','Technology','Field','Actor','Constraint','Product'];
  const chips = [...on].filter(x => x !== id).sort((a,b) => order.indexOf(NODES[a].type) - order.indexOf(NODES[b].type))
     .map(x => `<span class="chip" style="background:${{COL[NODES[x].type]}}" title="${{NODES[x].label}}">${{x}}</span>`).join('');
  info.innerHTML = `<span><span class="chip" style="background:${{COL[NODES[id].type]}}">${{id}}</span> <b>${{NODES[id].label}}</b> <span class="muted">· ${{NODES[id].type}} · ${{on.size-1}} linked</span></span><span>${{chips}}</span><button type="button" id="rst">Reset</button>`;
  document.getElementById('rst').onclick = reset;
}}
nodeEls.forEach(n => {{
  n.addEventListener('click', ev => {{ ev.stopPropagation(); select(n.dataset.id); }});
  n.addEventListener('keydown', ev => {{ if (ev.key === 'Enter' || ev.key === ' ') {{ ev.preventDefault(); select(n.dataset.id); }} }});
}});
G.addEventListener('click', reset);
document.addEventListener('keydown', ev => {{ if (ev.key === 'Escape') reset(); }});
</script>
</body></html>'''
import json
page = page.replace('__NODES__', json.dumps({i: {'type': n['type'], 'label': n['label']} for i, n in nodes.items()}))
page = page.replace('__EDGES__', json.dumps([[e['from'], e['to'], e['type']] for e in edges])).replace('__COL__', json.dumps(COL))
open(sys.argv[2], 'w').write(page)
print('ok')
