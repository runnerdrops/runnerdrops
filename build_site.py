import re, json, base64, os, shutil, subprocess
OUT='/home/claude/site'
shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT+'/img'); os.makedirs(OUT+'/css')
d=json.load(open('imgs.json')); rev={v:k for k,v in d.items()}
for k,v in d.items():
    open(f'{OUT}/img/{k}.jpg','wb').write(base64.b64decode(v.split(',',1)[1]))
def deimg(s):
    s=re.sub(r'data:image/jpeg;base64,[^"]+',lambda m:'img/'+rev.get(m.group(0),'MISSING')+'.jpg',s)
    s=re.sub(r'data-img="([A-Z_0-9]+)" src=""',r'src="img/\1.jpg"',s)
    return s

home=open('/mnt/user-data/outputs/RunnerDrops_Homepage_Concepts.html').read()
shoe=open('/mnt/user-data/outputs/RunnerDrops_Shoe_Page_v2.html').read()
# rebuild section pages to pull latest
subprocess.run(['python3','build_pages.py'],check=True)
sec=open('/mnt/user-data/outputs/RunnerDrops_Section_Pages.html').read()

def styles(s): return re.findall(r'<style>(.*?)</style>',s,flags=re.S)
fonts=styles(home)[0]
site_css=styles(home)[1]
sec_css=styles(sec)[1][len(site_css):] if styles(sec)[1].startswith(site_css) else styles(sec)[1]
shoe_css=styles(shoe)[1]
fix='''
.nav{top:env(safe-area-inset-top,0px)}
.page{display:block}
.concepts{background:var(--ink);color:var(--paper);border-bottom:var(--bw) solid var(--ink)}
.concepts__in{max-width:var(--max);margin:0 auto;padding:8px clamp(16px,3vw,40px);display:flex;align-items:center;gap:14px;flex-wrap:wrap;font-family:var(--mono);font-size:10px;letter-spacing:.12em}
.concepts .dev{margin-left:auto;display:flex;border:var(--bw) solid var(--paper)}
.concepts .dev a{padding:6px 14px;border-right:1px solid color-mix(in srgb,var(--paper) 35%,transparent);color:var(--paper)}
.concepts .dev a:last-child{border-right:none}
.concepts .dev a.is-on{background:var(--paper);color:var(--ink)}
.mock{opacity:.9}
'''
open(f'{OUT}/css/fonts.css','w').write(fonts)
open(f'{OUT}/css/site.css','w').write(site_css+sec_css+fix)
import re as _r
btn='\n'.join(l for l in site_css.split('\n') if l.startswith('.btn'))
open(f'{OUT}/css/shoe.css','w').write(shoe_css+fix+btn+'\n.nav .btn{font-size:15px;padding:9px 18px}')

NAV=['index.html','calendar.html','shoes.html','brands.html']
def nav(active):
    labels=['This week','Calendar','Shoes','Brands']
    links=''.join(f'<a href="{h}"{" class=\"is-on\"" if h==active else ""}>{l}</a>' for h,l in zip(NAV,labels))
    return f'''<header class="nav"><div class="nav__in">
<a class="nav__logo" href="index.html">Runner<em>Drops</em></a>
<nav class="nav__links" aria-label="Primary">{links}</nav>
<a class="btn" href="#alerts" style="font-size:15px;padding:9px 18px">Get alerts</a>
<button class="nav__burger" aria-label="Menu" onclick="document.querySelector('.nav__links').style.display='flex'"><span></span><span></span><span></span></button>
</div></header>'''
FOOT='''<footer class="footer" id="alerts">
  <div class="footer__in">
    <div><div class="footer__wm">Runner<em>Drops</em></div><p>The release calendar for running shoes. A text before it drops, not a tweet after it's gone.</p></div>
    <div><h5>Site</h5><ul><li><a href="index.html">This week</a></li><li><a href="calendar.html">Calendar</a></li><li><a href="shoes.html">Shoes</a></li><li><a href="brands.html">Brands</a></li></ul></div>
    <div><h5>Alerts</h5><ul><li>SMS drops</li><li>Email digest</li><li>Restocks</li></ul></div>
    <div><h5>RunnerDrops</h5><ul><li>About</li><li><a href="shoe-alphafly-3.html#tiers">How we review</a></li><li>Partnerships</li><li>Contact</li></ul></div>
  </div>
  <div class="footer__base"><div><span>© 2026 RUNNERDROPS</span><span>PRIVACY · TERMS · AFFILIATE DISCLOSURE</span></div></div>
</footer>'''

def section(html,sid):
    m=re.search(r'<section class="page[^"]*" id="'+sid+r'">(.*?)</section>',html,flags=re.S)
    return m.group(1)

SHOE_LINK={'Alphafly 3':'shoe-alphafly-3.html','Adios Pro 4':'shoe-adios-pro-4.html','Adizero Adios Pro 4':'shoe-adios-pro-4.html'}
def wire(s):
    # generic link fixes
    s=re.sub(r'<a class="more" href="#">All reviews</a>','<a class="more" href="shoes.html">All reviews</a>',s)
    s=re.sub(r'<a class="more" href="#">(Full calendar|Calendar|Everything)</a>',r'<a class="more" href="calendar.html">\1</a>',s)
    s=re.sub(r'<a class="more" href="#">All lists</a>','<a class="more" href="shoes.html#bestfor">All lists</a>',s)
    # review cards / rows that mention the two built shoes
    def link_block(pattern,url):
        nonlocal s
        s=re.sub(pattern,lambda m:m.group(0).replace('href="#"',f'href="{url}"'),s,flags=re.S)
    link_block(r'<article class="rev">.*?Alphafly 3.*?</article>','shoe-alphafly-3.html')
    link_block(r'<article class="rev">.*?Adios Pro 4.*?</article>','shoe-adios-pro-4.html')
    # rank rows / shoe cards: FULL REVIEW + SHOE PAGE
    for name,url in SHOE_LINK.items():
        s=re.sub(r'(<article class="(?:rk|sc)[^>]*>(?:(?!</article>).)*?<h3>'+re.escape(name)+r'</h3>(?:(?!</article>).)*?)href="#">(SHOE PAGE|FULL REVIEW)',lambda m:m.group(1)+f'href="{url}">'+m.group(2),s,flags=re.S)
        s=re.sub(r'(<article class="card[^>]*>(?:(?!</article>).)*?<h3>'+re.escape(name)+r'[^<]*</h3>(?:(?!</article>).)*?)<a class="a(?: out)?" href="#">',lambda m:m.group(1)+f'<a class="a" href="{url}">',s,flags=re.S)
    # ledger / rail rows: wrap name in link
    s=re.sub(r'<div class="n">(Nike Alphafly 3[^<]*)<',r'<div class="n"><a href="shoe-alphafly-3.html">\1</a><',s)
    s=re.sub(r'<div class="n">(adidas Adios Pro 4[^<]*)<',r'<div class="n"><a href="shoe-adios-pro-4.html">\1</a><',s)
    s=re.sub(r'<div class="n">(Alphafly 3[^<]*)<',r'<div class="n"><a href="shoe-alphafly-3.html">\1</a><',s)
    s=re.sub(r'<div><b>(Alphafly 3[^<]*)</b>',r'<div><b><a href="shoe-alphafly-3.html">\1</a></b>',s)
    s=re.sub(r'<div><b>(Adios Pro 4[^<]*)</b>',r'<div><b><a href="shoe-adios-pro-4.html">\1</a></b>',s)
    s=re.sub(r'<div><b>(adidas Adios Pro 4[^<]*)</b>',r'<div><b><a href="shoe-adios-pro-4.html">\1</a></b>',s)
    # calendar chips
    s=re.sub(r'(<div class="drop[^"]*">)(<span class="t"><img src="img/(?:NIKE_SQ)\.jpg"[^>]*></span><span>Alphafly 3)',r'<a href="shoe-alphafly-3.html" style="display:contents">\1\2',s)
    s=re.sub(r'(<div class="drop[^"]*">)(<span class="t"><img src="img/(?:ADI_SQ|ADI_TOP)\.jpg"[^>]*></span><span>Adios Pro 4)',r'<a href="shoe-adios-pro-4.html" style="display:contents">\1\2',s)
    s=re.sub(r'(<a href="shoe-[a-z0-9-]+\.html" style="display:contents"><div class="drop[^"]*">.*?</small></span></div>)',r'\1</a>',s,flags=re.S)
    # best-for tiles
    s=s.replace('<a class="bf bf--red" href="#"><h3>HYROX</h3>','<a class="bf bf--red" href="best-hyrox.html"><h3>HYROX</h3>')
    # brand tiles / brand grid
    s=re.sub(r'<a class="bt" href="#"><div class="bt__logo"><span>Nike</span>','<a class="bt" href="brand-nike.html"><div class="bt__logo"><span>Nike</span>',s)
    s=s.replace('<a href="#">Nike<span>6 UPCOMING</span></a>','<a href="brand-nike.html">Nike<span>6 UPCOMING</span></a>')
    s=s.replace('<span class="tag">Nike</span>','<a class="tag" href="brand-nike.html">Nike</a>').replace('<span class="tag tag--ink">Nike</span>','<a class="tag" href="brand-nike.html">Nike</a>')
    s=s.replace('<div class="wrap crumbs">Shoes / Nike / Alphafly 3</div>','<div class="wrap crumbs"><a href="shoes.html">Shoes</a> / <a href="brand-nike.html">Nike</a> / Alphafly 3</div>')
    s=s.replace('<div class="wrap crumbs">Shoes / adidas / Adizero Adios Pro 4</div>','<div class="wrap crumbs"><a href="shoes.html">Shoes</a> / <a href="brands.html">adidas</a> / Adizero Adios Pro 4</div>')
    s=s.replace('<div class="crumbs">Shoes / Best for / HYROX</div>','<div class="crumbs"><a href="shoes.html">Shoes</a> / <a href="shoes.html#bestfor">Best for</a> / HYROX</div>')
    s=s.replace('<div class="crumbs">Brands / Nike</div>','<div class="crumbs"><a href="brands.html">Brands</a> / Nike</div>')
    s=s.replace('<a class="btn" href="#">Text me when it drops</a><a class="btn btn--ghost" href="#">Release info &amp; sizing</a>','<a class="btn" href="#alerts">Text me when it drops</a><a class="btn btn--ghost" href="shoe-alphafly-3.html">Release info &amp; sizing</a>')
    s=s.replace('<div class="shead"><h2>Best for</h2>','<div class="shead" id="bestfor"><h2>Best for</h2>')
    s=s.replace('<div class="shead"><h2>What people are saying</h2>','<div class="shead" id="tiers"><h2>What people are saying</h2>')
    # homepage C brands grid: nike link
    s=s.replace('<a href="#">Nike<span>6 UPCOMING</span></a>','<a href="brand-nike.html">Nike<span>6 UPCOMING</span></a>')
    s=s.replace('class="disagree">\n        <h3>Where they<br>disagree</h3>','class="disagree">\n        <h3>Where they<br>disagree</h3>')
    s=re.sub(r'(<div class="disagree">.*?)<a class="btn btn--sm" href="#">Read the split</a>',r'\1<a class="btn btn--sm" href="shoe-adios-pro-4.html#tiers">Read the split</a>',s,flags=re.S)
    return s

def page(fname,title,active,body,css,doctype=True,extra_head=''):
    head=f'''<title>{title}</title>
<link rel="stylesheet" href="css/fonts.css"><link rel="stylesheet" href="css/{css}">{extra_head}'''
    body=wire(deimg(body))
    html=f'{head}\n{nav(active)}\n{body}\n{FOOT}\n'
    if doctype:
        html=f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">{head}</head><body>\n{nav(active)}\n{body}\n{FOOT}\n</body></html>'
    open(f'{OUT}/{fname}','w').write(html); print(fname,len(html)//1000,'KB')

def concepts(cur):
    items=[('index.html','A · FRONT PAGE'),('home-calendar.html','B · THE CALENDAR'),('home-board.html','C · THE DROP BOARD')]
    links=''.join(f'<a href="{h}"{" class=\"is-on\"" if h==cur else ""}>{l}</a>' for h,l in items)
    return f'<div class="concepts"><div class="concepts__in"><span class="mock">HOMEPAGE CONCEPT · MOCKUP</span><div class="dev">{links}</div></div></div>'

# homepage concepts
page('index.html','RunnerDrops','index.html',concepts('index.html')+section(home,'a'),'site.css',doctype=False)
hb=section(home,'b')
for ph,key in [('HOKA<br>CLIFTON','CLIFTON_SQ'),('NIKE<br>PEG 42','PEG42_SQ'),('MIZUNO<br>REB 3','MIZ_SQ')]:
    hb=hb.replace(f'<span class="t ph">{ph}</span>',f'<span class="t"><img src="{d[key]}" alt=""></span>')
page('home-calendar.html','RunnerDrops','index.html',concepts('home-calendar.html')+hb,'site.css')
page('home-board.html','RunnerDrops','index.html',concepts('home-board.html')+section(home,'c'),'site.css')
# section pages
page('calendar.html','RunnerDrops Calendar','calendar.html',section(sec,'cal'),'site.css')
page('shoes.html','RunnerDrops Shoes','shoes.html',section(sec,'shoes'),'site.css')
page('best-hyrox.html','Best Shoes for HYROX','shoes.html',section(sec,'best'),'site.css')
page('brands.html','RunnerDrops Brands','brands.html',section(sec,'brands'),'site.css')
page('brand-nike.html','Nike on RunnerDrops','brands.html',section(sec,'brand'),'site.css')
# shoe pages (own stylesheet) + static buybar
bb_a='<div class="buybar"><div class="t">ALPHAFLY 3 · $305<br>IN STOCK AT 2 RETAILERS</div><a class="btn" href="#alerts" style="margin-left:auto;font-size:15px;padding:10px 22px;box-shadow:none;border-color:var(--paper)">Get alerts</a></div>'
bb_b='<div class="buybar"><div class="t">ADIOS PRO 4 · $255<br>IN STOCK AT 3 RETAILERS</div><a class="btn" href="#alerts" style="margin-left:auto;font-size:15px;padding:10px 22px;box-shadow:none;border-color:var(--paper)">Get alerts</a></div>'
page('shoe-alphafly-3.html','Nike Alphafly 3 Review','shoes.html',section(shoe,'alphafly')+bb_a,'shoe.css')
page('shoe-adios-pro-4.html','adidas Adios Pro 4 Review','shoes.html',section(shoe,'adios')+bb_b,'shoe.css')

# sanity: unresolved image paths / leftover scripts
for f in os.listdir(OUT):
    if f.endswith('.html'):
        t=open(f'{OUT}/{f}').read()
        assert 'MISSING' not in t and 'data:image' not in t and '<script' not in t, f
print('ok', sorted(os.listdir(OUT)), sum(os.path.getsize(f'{OUT}/img/{x}') for x in os.listdir(OUT+'/img'))//1000,'KB images')

# ---- GitHub Pages copy: docs/ (same site, index.html gets a full document shell, no Jekyll)
DOCS='/home/claude/docs'
shutil.rmtree(DOCS, ignore_errors=True); shutil.copytree(OUT, DOCS)
_idx=open(f'{OUT}/index.html').read()
open(f'{DOCS}/index.html','w').write('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'+_idx.replace('\n','</head><body>\n',1)+'</body></html>')
open(f'{DOCS}/.nojekyll','w').write('')
print('docs/ written for GitHub Pages')
