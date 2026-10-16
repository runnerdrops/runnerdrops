import json,re
d=json.load(open('imgs.json')); fonts=open('fonts.css').read(); shared=open('shared.css').read()
nav=open('nav.html').read(); foot=open('foot.html').read(); cal=open('cal_block.html').read()
import re as _re
cal=_re.sub(r'<div class="filters">.*?</div>\n','',cal,flags=_re.S)
nav=nav.replace('<a href="#" class="is-on">This week</a><a href="#">Calendar</a><a href="#">Shoes</a><a href="#">Brands</a>',
                '<a href="#">This week</a><a href="#" id="nav-cal">Calendar</a><a href="#" id="nav-shoes">Shoes</a><a href="#" class="is-on" id="nav-brands">Brands</a>')

# ---------------- shoe database ----------------
SHOES=[
 # key, brand, name, cat, price, oz, drop, plate, status, rd, rev, run, img
 dict(k='alphafly',b='Nike',n='Alphafly 3',c='Racing',p=305,oz=7.7,dr=8,pl='Carbon',st='Released',rd='9.2',rv=91,ru=87,img='NIKE_SQ'),
 dict(k='adios',b='adidas',n='Adizero Adios Pro 4',c='Racing',p=255,oz=7.1,dr=6,pl='EnergyRods',st='Released',rd='—',rv=88,ru=78,img='ADI_SQ'),
 dict(k='vf4',b='Nike',n='Vaporfly 4',c='Racing',p=260,oz=6.5,dr=6,pl='Carbon',st='Drops Sep 24',rd='—',rv=90,ru=84,img='VF4_SQ'),
 dict(k='vf3',b='Nike',n='Vaporfly 3',c='Racing',p=260,oz=7.0,dr=8,pl='Carbon',st='Released',rd='8.8',rv=89,ru=86,img='VF3_SQ'),
 dict(k='elite2',b='Saucony',n='Endorphin Elite 2',c='Racing',p=275,oz=7.2,dr=8,pl='Carbon',st='Drops Sep 9',rd='—',rv=86,ru=80,img='SAUC_SQ'),
 dict(k='pro4',b='Saucony',n='Endorphin Pro 4',c='Racing',p=225,oz=7.5,dr=8,pl='Carbon',st='Released',rd='8.4',rv=85,ru=83,img='PRO4_SQ'),
 dict(k='meta',b='Asics',n='Metaspeed Sky Paris',c='Racing',p=250,oz=6.5,dr=5,pl='Carbon',st='Restock',rd='8.9',rv=92,ru=85,img='META_SQ'),
 dict(k='nb',b='New Balance',n='SC Elite v5',c='Racing',p=250,oz=7.3,dr=4,pl='Carbon',st='Drops Sep 14',rd='—',rv=84,ru=79,img='NB_SQ'),
 dict(k='puma',b='Puma',n='Fast-R Nitro Elite 3',c='Racing',p=300,oz=6.0,dr=8,pl='Carbon',st='Drops Sep 16',rd='—',rv=93,ru=81,img='PUMA_SQ'),
 dict(k='brooks',b='Brooks',n='Hyperion Elite 5',c='Racing',p=275,oz=7.4,dr=8,pl='Carbon',st='Drops Sep 22',rd='—',rv=82,ru=76,img='BROOKS_SQ'),
 dict(k='cielo',b='Hoka',n='Cielo X1 2.0',c='Racing',p=275,oz=8.3,dr=7,pl='Carbon',st='Moved to Oct 2',rd='8.1',rv=83,ru=77,img='CIELO_SQ'),
 dict(k='on',b='On',n='Cloudboom Strike LS',c='Racing',p=330,oz=6.1,dr=4,pl='Carbon',st='Drops Sep 10',rd='—',rv=80,ru=72,img='ON_SQ'),
 dict(k='rocket',b='Hoka',n='Rocket X 3',c='Racing',p=250,oz=7.5,dr=7,pl='Carbon',st='Drops Sep 17',rd='—',rv=85,ru=80,img='ROCKET_SQ'),
 dict(k='machx',b='Hoka',n='Mach X 3',c='Super trainer',p=190,oz=8.9,dr=5,pl='Pebax',st='Drops Sep 7',rd='8.7',rv=90,ru=88,img='HOKA_SQ'),
 dict(k='nova',b='Asics',n='Novablast 6',c='Daily trainer',p=150,oz=8.8,dr=8,pl='None',st='Drops Sep 8',rd='8.5',rv=88,ru=91,img='ASICS_SQ'),
]
def score(v,na=False,suffix=''):
    return f'<b class="na">—</b>' if v=='—' else f'<b>{v}<small>{suffix}</small></b>'
def card(x):
    stamp={'Released':'stamp--paper','Restock':'','Moved to Oct 2':''}.get(x['st'],'stamp--red')
    return f'''<article class="sc" data-cat="{x['c']}" data-brand="{x['b']}">
  <div class="pic"><img src="{{{{{x['img']}}}}}" alt="{x['b']} {x['n']}"><span class="stamp {stamp}">{x['st']}</span></div>
  <div class="sc__b">
    <div class="kick"><span class="tag">{x['b']}</span><span class="dim">{x['c']}</span></div>
    <h3>{x['n']}</h3>
    <div class="spec">${x['p']} · {x['oz']} oz · {x['dr']} mm · {x['pl']}</div>
    <div class="scores"><div><h5>RunnerDrops</h5>{score(x['rd'],suffix='/10')}</div><div><h5>Reviewers</h5>{score(x['rv'],suffix='%')}</div><div><h5>Runners</h5>{score(x['ru'],suffix='%')}</div></div>
    <div class="sc__f"><a href="#">SHOE PAGE</a><a href="#" class="hot">NOTIFY</a></div>
  </div>
</article>'''
cards='\n'.join(card(x) for x in SHOES)
from collections import Counter
cats=Counter(x['c'] for x in SHOES); brands=Counter(x['b'] for x in SHOES)
catlist=[('Racing',cats['Racing']),('Daily trainer',cats['Daily trainer']),('Super trainer',cats['Super trainer']),('Max cushion',0),('Trail',0),('Stability',0)]
def facet(name,count,on=False):
    return f'<label class="fct{" is-on" if on else ""}"><input type="checkbox"{" checked" if on else ""}><span>{name}</span><i>{count}</i></label>'
catfacets=''.join(facet(n,c) for n,c in catlist)
brandfacets=''.join(facet(n,c) for n,c in sorted(brands.items(),key=lambda t:-t[1]))

# ---------------- HYROX list ----------------
HYROX=[
 ('machx','The default answer. Enough plate to push the 8K splits, enough rubber up front to hold a sled push. Runners rank it #1 for stations.','Sled push','8K run','$190'),
 ('nova','Unplated, which is the point: stable on the lateral stations and no calf tax on the burpee broad jumps. Best value here.','Burpee BJ','Lunges','$150'),
 ('puma','The racers\' pick. Lightest plated shoe on the list, and the PWRPLATE is forgiving enough for farmer carries. Narrow heel though.','8K run','Carries','$300'),
 ('pro4','More shoe than the Elite, less money. Wider platform than most carbon racers, which matters on the wall balls.','Wall balls','8K run','$225'),
 ('adios','Fast and soft, but the soft narrow heel is a liability on sled pull. Pro Solo and Elite 15 territory only.','8K run','','$255'),
 ('vf3','Reliable, widely available, and a known quantity. Outsole is the weak point on the SkiErg-to-sled transition.','8K run','','$260'),
 ('on','Grippy and stable, but the price and low drop make it a hard sell for a station race.','Sled pull','','$330'),
 ('nb','Low 4 mm drop and a firm platform. Good for midfoot strikers, divisive for everyone else.','Rowing','','$250'),
]
byk={x['k']:x for x in SHOES}
def rankrow(i,k,why,t1,t2,price):
    x=byk[k]
    tags=''.join(f'<span class="chip chip--fill">{t}</span>' for t in (t1,t2) if t)
    return f'''<article class="rk{' rk--one' if i==1 else ''}">
  <div class="rk__n">{i:02d}</div>
  <div class="pic"><img src="{{{{{x['img']}}}}}" alt=""></div>
  <div class="rk__b">
    <div class="kick"><span class="tag">{x['b']}</span><span class="dim">{x['c']} · {x['oz']} oz · {x['dr']} mm</span></div>
    <h3>{x['n']}</h3>
    <p>{why}</p>
    <div class="rk__tags"><span class="dim mono">BEST AT</span>{tags}</div>
  </div>
  <div class="rk__r">
    <div class="scores scores--v"><div><h5>RunnerDrops</h5>{score(x['rd'],suffix='/10')}</div><div><h5>Reviewers</h5>{score(x['rv'],suffix='%')}</div><div><h5>Runners</h5>{score(x['ru'],suffix='%')}</div></div>
    <a class="btn btn--sm" href="#">Shop · {price}</a>
    <a class="rk__link" href="#">FULL REVIEW</a>
  </div>
</article>'''
ranks='\n'.join(rankrow(i+1,*r) for i,r in enumerate(HYROX))

# ---------------- brands ----------------
BRANDS=[
 ('Nike',6,4,87,'Alphafly 3 Platinum Tint','Sep 10','NIKE_SQ'),('adidas',5,3,78,'Adios Pro 4 Berlin','Sep 20','ADI_TOP'),('Hoka',4,3,82,'Mach X 3','Sep 7','HOKA_SQ'),('Asics',4,3,89,'Novablast 6','Sep 8','ASICS_SQ'),
 ('Saucony',3,2,81,'Endorphin Elite 2','Sep 9','SAUC_SQ'),('On',3,1,72,'Cloudboom Strike LS','Sep 10','ON_SQ'),('New Balance',3,1,79,'SC Elite v5','Sep 14','NB_SQ'),('Puma',2,1,81,'Fast-R Nitro Elite 3','Sep 16','PUMA_SQ'),
 ('Brooks',2,1,76,'Hyperion Elite 5','Sep 22','BROOKS_SQ'),('Mizuno',2,0,None,'Rebellion Pro 3','TBC',None),('Altra',1,0,None,'Vanish Carbon 3','Oct 14',None),('Salomon',1,0,None,'S/Lab Phantasm 3','Oct 21',None),('Under Armour',1,0,None,'Velociti Elite 3','Nov 4',None),('Xtep',1,0,None,'160X 7.0 Pro','Nov 11',None),
]
def bcard(b,up,rev,ru,nxt,date,img):
    pic=f'<div class="pic"><img src="{{{{{img}}}}}" alt=""></div>' if img else '<div class="ph">'+b.upper()+'</div>'
    rus=f'{ru}%' if ru else '—'
    return f'''<a class="bc" href="#">
  <div class="bc__h"><h3>{b}</h3><span class="chip">{up} UPCOMING</span></div>
  <div class="bc__stats"><div><h5>Reviewed</h5><b>{rev}</b></div><div><h5>Runners</h5><b{" class=na" if not ru else ""}>{rus}</b></div><div><h5>Next</h5><b>{date}</b></div></div>
  <div class="bc__next">{pic}<div><span class="mono dim">NEXT DROP</span><b>{nxt}</b></div><span class="chip chip--red">FOLLOW</span></div>
</a>'''
bcards='\n'.join(bcard(*b) for b in BRANDS)
BRANDS20=[('361°','361 Degrees'),('adidas','adidas'),('Altra','Altra'),('ANTA','ANTA'),('Asics','ASICS'),('Brooks','Brooks'),('Diadora','Diadora'),('Hoka','HOKA'),('Kiprun','Kiprun'),('Li-Ning','Li-Ning'),('Mizuno','Mizuno'),('New Balance','New Balance'),('Nike','Nike'),('Norda','norda'),('On','On'),('Puma','PUMA'),('Reebok','Reebok'),('Salomon','Salomon'),('Saucony','Saucony'),('Under Armour','Under Armour')]
LOGO_SLUG={'361°':'361','Under Armour':'under-armour','New Balance':'new-balance','Li-Ning':'li-ning'}
def btile(name,wm):
    slug=LOGO_SLUG.get(name,name.lower())
    return f'''<a class="bt" href="#"><div class="bt__logo"><img src="img/logos/{slug}.png" alt="{wm}"></div><div class="bt__n">{name}</div></a>'''
btiles='\n'.join(btile(*b) for b in BRANDS20)


CSS='''
/* ===== page heads ===== */
.phead{max-width:var(--max);margin:0 auto;padding:clamp(22px,3vw,36px) clamp(16px,3vw,40px) 0;display:grid;grid-template-columns:minmax(0,1.4fr) minmax(0,1fr);gap:clamp(24px,3vw,48px);align-items:end}
.phead h1{font-family:var(--disp);font-weight:700;font-size:clamp(42px,5.6vw,78px);line-height:.92;text-transform:uppercase;letter-spacing:-.005em;margin-top:12px}
.phead h1 em{font-style:normal;color:var(--red)}
.phead .dek{font-size:16px;line-height:1.55;max-width:56ch;margin-top:14px}
.crumbs{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;opacity:.6;max-width:var(--max);margin:0 auto;padding:clamp(14px,2vw,22px) clamp(16px,3vw,40px) 0}
.toolbar{max-width:var(--max);margin:clamp(20px,3vw,32px) auto 0;padding:0 clamp(16px,3vw,40px)}
.toolbar__in{display:flex;align-items:center;gap:10px;flex-wrap:wrap;border-top:var(--bw) solid var(--ink);border-bottom:var(--bw) solid var(--ink);padding:10px 0}
.seg{display:flex;border:var(--bw) solid var(--ink)}
.seg button{background:var(--paper);border:none;font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;padding:8px 14px}
.seg button+button{border-left:var(--bw) solid var(--ink)}
.seg button.is-on{background:var(--ink);color:var(--paper)}
.toolbar .chips{gap:6px}
.toolbar .right{margin-left:auto;display:flex;gap:10px;align-items:center}
.search{display:flex;border:var(--bw) solid var(--ink);background:var(--card)}
.search input{border:none;background:none;font-family:var(--mono);font-size:12px;padding:8px 12px;width:220px;min-width:0}
.search input::placeholder{color:color-mix(in srgb,var(--ink) 45%,transparent)}
.search button{border:none;border-left:var(--bw) solid var(--ink);background:var(--ink);color:var(--paper);font-family:var(--mono);font-size:10px;letter-spacing:.12em;padding:0 12px}
.sel{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;border:var(--bw) solid var(--ink);background:var(--card);padding:8px 12px}
.dim{opacity:.55}

/* ===== calendar page additions ===== */
.legend{display:flex;gap:14px;flex-wrap:wrap;font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;margin-left:auto}
.legend span{display:inline-flex;align-items:center;gap:6px}
.legend i{display:inline-block;width:12px;height:12px;border:1.5px solid var(--ink)}
.weekhead{display:flex;align-items:baseline;gap:14px;margin:clamp(28px,4vw,40px) 0 8px}
.weekhead h3{font-family:var(--disp);font-weight:700;font-size:clamp(22px,2.4vw,30px);text-transform:uppercase}
.weekhead span{font-family:var(--mono);font-size:10px;letter-spacing:.12em;opacity:.55}
.weekhead::after{content:"";flex:1;height:1px;background:var(--hair)}
.lrow .n .rum{display:inline-block;font-family:var(--mono);font-size:8.5px;letter-spacing:.12em;border:1.5px dashed var(--ink);padding:2px 6px;margin-left:8px;vertical-align:middle;font-weight:400}
.movedbox{border:var(--bw) solid var(--ink);background:var(--card);margin-top:22px}
.movedbox h4{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--red);padding:12px 14px;border-bottom:var(--bw) solid var(--ink)}
.movedbox div{padding:10px 14px;border-bottom:1px solid var(--hair);font-size:13px;line-height:1.45}
.movedbox div:last-child{border-bottom:none}
.movedbox b{font-family:var(--disp);font-weight:700;font-size:16px;text-transform:uppercase;display:block}
.movedbox s{opacity:.5}

/* ===== shoes index ===== */
.bestfor{max-width:var(--max);margin:0 auto;padding:0 clamp(16px,3vw,40px)}
.bestfor__grid{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}
.bf{border:var(--bw) solid var(--ink);background:var(--card);padding:14px;display:flex;flex-direction:column;gap:8px;min-height:150px;position:relative}
.bf h3{font-family:var(--disp);font-weight:700;font-size:21px;line-height:1;text-transform:uppercase}
.bf span{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;opacity:.6;margin-top:auto}
.bf .stack{display:flex;margin-top:6px}
.bf .stack i{display:block;width:30px;height:30px;border:1.5px solid var(--ink);background:var(--paper);overflow:hidden;margin-right:-8px}
.bf .stack img{width:100%;height:100%;object-fit:cover;mix-blend-mode:multiply}
.bf--red{background:var(--red);color:var(--paper)}
.bf--red .stack i{border-color:var(--paper)}
.bf--ink{background:var(--ink);color:var(--paper)}
.bf--ink .stack i{border-color:var(--paper)}
.bf::after{content:"→";position:absolute;top:12px;right:14px;font-family:var(--mono);font-size:14px}
.dbwrap{max-width:var(--max);margin:clamp(24px,3vw,36px) auto 0;padding:0 clamp(16px,3vw,40px);display:grid;grid-template-columns:230px minmax(0,1fr);gap:clamp(24px,3vw,40px);align-items:start}
.facets{position:sticky;top:86px}
.facets h4{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--red);margin:0 0 6px;padding-top:14px}
.facets h4:first-child{padding-top:0}
.fct{display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid var(--hair2);font-size:13.5px;cursor:pointer}
.fct input{appearance:none;width:14px;height:14px;border:1.5px solid var(--ink);background:var(--paper);flex:0 0 auto;display:grid;place-items:center}
.fct input:checked{background:var(--ink)}
.fct input:checked::after{content:"";width:6px;height:6px;background:var(--paper)}
.fct i{margin-left:auto;font-style:normal;font-family:var(--mono);font-size:10px;opacity:.55}
.rng{display:grid;grid-template-columns:1fr auto 1fr;gap:8px;align-items:center;margin:4px 0 2px}
.rng input{width:100%;font-family:var(--mono);font-size:11px;border:var(--bw) solid var(--ink);background:var(--card);padding:6px 8px}
.rng span{font-family:var(--mono);font-size:10px;opacity:.5}
.facets .btn{width:100%;margin-top:18px;font-size:14px;padding:10px}
.sortbar{display:flex;align-items:center;gap:12px;flex-wrap:wrap;padding-bottom:12px;border-bottom:var(--bw) solid var(--ink)}
.sortbar .count{font-family:var(--disp);font-weight:700;font-size:24px;text-transform:uppercase}
.sortbar .count small{font-family:var(--mono);font-size:10px;letter-spacing:.12em;font-weight:400;opacity:.55;margin-left:8px}
.sortbar .right{margin-left:auto;display:flex;gap:8px;align-items:center;font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase}
.sgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:16px}
.sc{border:var(--bw) solid var(--ink);background:var(--card);display:flex;flex-direction:column}
.sc .pic{border:none;border-bottom:var(--bw) solid var(--ink);aspect-ratio:1}
.sc__b{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;flex:1}
.sc__b h3{font-family:var(--disp);font-weight:700;font-size:22px;text-transform:uppercase;line-height:1}
.sc__b .spec{font-family:var(--mono);font-size:10px;letter-spacing:.06em;opacity:.65}
.sc__b .scores{margin-top:6px}
.sc__b .scores>div{padding:6px 8px}
.sc__b .scores b{font-size:20px}
.sc__f{display:flex;justify-content:space-between;margin-top:auto;padding-top:10px;font-family:var(--mono);font-size:10px;letter-spacing:.1em}
.sc__f a{border-bottom:1.5px solid var(--ink);padding-bottom:1px}
.sc__f a.hot{border:var(--bw) solid var(--ink);background:var(--red);color:var(--paper);padding:6px 12px}
.pager{display:flex;justify-content:center;gap:0;margin-top:24px;border:var(--bw) solid var(--ink);width:max-content;margin-left:auto;margin-right:auto}
.pager a{font-family:var(--mono);font-size:11px;padding:8px 14px;border-right:var(--bw) solid var(--ink)}
.pager a:last-child{border-right:none}
.pager a.is-on{background:var(--ink);color:var(--paper)}

/* ===== best-for list ===== */
.listwrap{max-width:var(--max);margin:clamp(24px,3vw,36px) auto 0;padding:0 clamp(16px,3vw,40px);display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:clamp(24px,3vw,40px);align-items:start}
.byline{display:flex;gap:16px;flex-wrap:wrap;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;margin-top:16px;padding-top:12px;border-top:var(--bw) solid var(--ink)}
.byline b{color:var(--red)}
.method{border:var(--bw) solid var(--ink);background:var(--card);padding:16px 18px;display:grid;grid-template-columns:auto minmax(0,1fr);gap:16px;align-items:start;margin-bottom:20px}
.method .n{font-family:var(--mono);font-size:11px;letter-spacing:.14em;border:1.5px solid var(--ink);padding:4px 8px}
.method h4{font-family:var(--disp);font-weight:700;font-size:20px;text-transform:uppercase;line-height:1}
.method p{font-size:13.5px;line-height:1.5;margin-top:6px;opacity:.85}
.rk{border:var(--bw) solid var(--ink);background:var(--card);display:grid;grid-template-columns:56px 170px minmax(0,1fr) 190px;margin-top:14px}
.rk__n{font-family:var(--disp);font-weight:700;font-size:34px;display:grid;place-items:center;border-right:var(--bw) solid var(--ink);background:var(--paper)}
.rk--one .rk__n{background:var(--red);color:var(--paper)}
.rk .pic{border:none;border-right:var(--bw) solid var(--ink);aspect-ratio:auto}
.rk__b{padding:14px 18px 16px}
.rk__b h3{font-family:var(--disp);font-weight:700;font-size:26px;text-transform:uppercase;line-height:1;margin-top:6px}
.rk__b p{font-size:14px;line-height:1.5;margin-top:8px;max-width:60ch}
.rk__tags{display:flex;gap:6px;align-items:center;margin-top:10px;font-size:9.5px;letter-spacing:.12em}
.rk__r{border-left:var(--bw) solid var(--ink);padding:12px 14px;display:flex;flex-direction:column;gap:10px}
.scores--v{grid-template-columns:1fr;margin-top:0}
.scores--v>div{border-right:none;border-bottom:1px solid var(--hair);padding:6px 10px;display:flex;justify-content:space-between;align-items:baseline}
.scores--v>div:last-child{border-bottom:none}
.scores--v h5{margin:0}
.scores--v b{font-size:20px}
.rk__r .btn{font-size:14px;padding:9px 12px;box-shadow:3px 3px 0 var(--ink)}
.rk__link{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-align:center;border-bottom:1.5px solid var(--ink);align-self:center}
.jump{border:var(--bw) solid var(--ink);background:var(--card)}
.jump h4{font-family:var(--mono);font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--red);padding:12px 14px;border-bottom:var(--bw) solid var(--ink)}
.jump a{display:grid;grid-template-columns:28px minmax(0,1fr);gap:8px;align-items:baseline;padding:8px 14px;border-bottom:1px solid var(--hair);font-family:var(--disp);font-weight:600;font-size:15px;text-transform:uppercase;letter-spacing:.03em}
.jump a:last-child{border-bottom:none}
.jump a i{font-style:normal;font-family:var(--mono);font-size:10px;opacity:.5}
.jump a:hover{background:var(--paper)}
.related{margin-top:22px}
.related .bf{min-height:0;margin-top:10px}

/* ===== brands ===== */
.btgrid{display:grid;grid-template-columns:repeat(5,1fr);gap:var(--bw);background:var(--ink);border:var(--bw) solid var(--ink)}
.bt{display:flex;flex-direction:column;background:var(--card);min-width:0}
.bt__logo{aspect-ratio:5/3;display:grid;place-items:center;padding:18px;border-bottom:1px solid var(--hair)}
.bt__logo img{width:46%;aspect-ratio:1;height:auto;object-fit:contain;display:block}
.bt__logo span{font-family:var(--disp);font-weight:700;font-size:clamp(22px,2.4vw,34px);text-transform:uppercase;letter-spacing:.02em;opacity:.25;text-align:center;line-height:1}
.bt__n{font-family:var(--mono);font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;padding:10px 14px;display:flex;justify-content:space-between;align-items:center}
.bt__n::after{content:"→";opacity:.4}
.bt:hover{background:var(--paper)}
.bt:hover .bt__n{background:var(--ink);color:var(--paper)}
.bt:hover .bt__n::after{opacity:1}
.btgrid-wrap{max-width:var(--max);margin:clamp(24px,3vw,36px) auto 0;padding:0 clamp(16px,3vw,40px)}

.bgrid{max-width:var(--max);margin:clamp(24px,3vw,36px) auto 0;padding:0 clamp(16px,3vw,40px);display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.bc{border:var(--bw) solid var(--ink);background:var(--card);display:flex;flex-direction:column}
.bc__h{display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:var(--bw) solid var(--ink)}
.bc__h h3{font-family:var(--disp);font-weight:700;font-size:30px;text-transform:uppercase;line-height:1}
.bc__stats{display:grid;grid-template-columns:repeat(3,1fr);border-bottom:1px solid var(--hair)}
.bc__stats>div{padding:10px 16px;border-right:1px solid var(--hair)}
.bc__stats>div:last-child{border-right:none}
.bc__stats h5{font-family:var(--mono);font-size:8.5px;letter-spacing:.14em;text-transform:uppercase;opacity:.55;margin-bottom:3px}
.bc__stats b{font-family:var(--disp);font-weight:700;font-size:20px;text-transform:uppercase;white-space:nowrap}
.bc__stats b.na{opacity:.35}
.bc__next{display:grid;grid-template-columns:54px minmax(0,1fr) auto;gap:12px;align-items:center;padding:12px 16px}
.bc__next .pic,.bc__next .ph{aspect-ratio:1}
.bc__next .ph{padding:2px;font-size:7px;line-height:1.3}
.bc__next span.mono{font-size:9px;letter-spacing:.12em;display:block}
.bc__next b{font-family:var(--disp);font-weight:700;font-size:17px;text-transform:uppercase;line-height:1;display:block;margin-top:3px}
.bc:hover .bc__h{background:var(--ink);color:var(--paper)}
.bc:hover .bc__h .chip{border-color:var(--paper)}
.bhead{max-width:var(--max);margin:0 auto;padding:clamp(14px,2vw,22px) clamp(16px,3vw,40px) 0;display:grid;grid-template-columns:minmax(0,1fr) auto;gap:32px;align-items:end}
.bhead h1{font-family:var(--disp);font-weight:700;font-size:clamp(60px,9vw,128px);line-height:.85;text-transform:uppercase;letter-spacing:-.01em}
.bhead .dek{font-size:16px;line-height:1.55;max-width:60ch;margin-top:14px}
.bhead .stats{margin-bottom:6px}
.bwrap{max-width:var(--max);margin:clamp(24px,3vw,36px) auto 0;padding:0 clamp(16px,3vw,40px);display:grid;grid-template-columns:minmax(0,1fr) 300px;gap:clamp(24px,3vw,40px);align-items:start}
.lineup{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.lineup .sc .pic{aspect-ratio:4/3}
.lineup .ph{aspect-ratio:4/3;border:none;border-bottom:var(--bw) solid var(--ink)}
.rrow .nxt{font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-align:right;line-height:1.4}
.rrow .nxt b{font-size:12px;display:block}
.pricewatch{display:grid;grid-template-columns:minmax(0,1fr) auto auto;gap:12px;align-items:center;padding:10px 14px;border-bottom:1px solid var(--hair);font-size:13px}
.pricewatch:last-child{border-bottom:none}
.pricewatch b{font-family:var(--disp);font-weight:700;font-size:16px;text-transform:uppercase;display:block;line-height:1}
.pricewatch .mono{font-size:11px}
.pricewatch .up{color:var(--red);font-weight:700}

@media(max-width:1000px){
  .phead,.dbwrap,.listwrap,.bwrap,.bhead{grid-template-columns:1fr}
  .facets{position:static;display:grid;grid-template-columns:1fr 1fr;gap:0 24px}
  .facets .btn{grid-column:1/-1}
  .bestfor__grid{grid-template-columns:repeat(3,1fr)}
  .sgrid,.bgrid,.lineup{grid-template-columns:repeat(2,1fr)}
  .btgrid{grid-template-columns:repeat(4,1fr)}
  .rk{grid-template-columns:48px 130px minmax(0,1fr)}
  .rk__r{grid-column:1/-1;border-left:none;border-top:var(--bw) solid var(--ink);flex-direction:row;align-items:center;justify-content:space-between}
  .rk__r .scores--v{grid-template-columns:repeat(3,auto);gap:0 18px}
  .rk__r .scores--v>div{border-bottom:none;flex-direction:column;gap:2px;align-items:flex-start}
}
@media(max-width:720px){
  .bestfor__grid{grid-template-columns:1fr 1fr}
  .sgrid,.bgrid,.lineup{grid-template-columns:1fr}
  .btgrid{grid-template-columns:repeat(2,1fr)}
  .facets{grid-template-columns:1fr}
  .toolbar .right{margin-left:0;width:100%}
  .search{flex:1}.search input{width:100%}
  .rk{grid-template-columns:40px minmax(0,1fr)}
  .rk .pic{grid-column:2;border-right:none;border-bottom:var(--bw) solid var(--ink);aspect-ratio:3/2}
  .rk__n{grid-row:span 2}
  .rk__b{grid-column:2}
  .rk__r{flex-wrap:wrap;gap:12px}
  .rk__r .scores--v{width:100%}
  .legend{margin-left:0}
}
'''

PAGES=f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>RunnerDrops — Calendar · Shoes · Brands</title>
<style>{fonts}</style>
<style>{shared}{CSS}</style>
</head><body>
{nav}
<div class="comp"><div class="comp__in">
  <span class="stamp">SECTION PAGES · V1 · OCT 8, 2026</span>
  <div class="dev" role="tablist">
    <button data-p="cal">CALENDAR</button><button data-p="shoes">SHOES</button><button data-p="best">BEST FOR: HYROX</button><button class="is-on" data-p="brands">BRANDS</button><button data-p="brand">BRAND: NIKE</button>
  </div>
</div></div>

<!-- ================= CALENDAR ================= -->
<section class="page" id="cal">
<div class="phead">
  <div>
    <div class="kick"><span class="tag tag--red">Live</span><span>Updated Sat Sep 5 · 9:14 AM CT</span><span>·</span><span>38 upcoming · 14 brands</span></div>
    <h1>Release <em>calendar.</em></h1>
    <p class="dek">Every confirmed drop, restock, price change and delay. Dashed entries are rumored or unconfirmed; we text you when they firm up.</p>
  </div>
  <div class="stats"><div><h5>This week</h5><b>6</b><span>SEP 7 – 13</span></div><div><h5>Next 30 days</h5><b>21</b><span>12 CONFIRMED · 9 RUMORED</span></div><div><h5>Moved</h5><b>3</b><span>IN THE LAST 7 DAYS</span></div></div>
</div>
<div class="toolbar"><div class="toolbar__in">
  <div class="seg"><button class="is-on">Month</button><button>List</button></div>
  <div class="chips"><span class="chip chip--fill">All</span><span class="chip">Racing</span><span class="chip">Daily</span><span class="chip">Super trainer</span><span class="chip">Trail</span><span class="chip">Restocks</span></div>
  <div class="right"><select class="sel"><option>All brands</option><option>Nike</option><option>adidas</option><option>Hoka</option></select><select class="sel"><option>Confirmed + rumored</option><option>Confirmed only</option></select></div>
  <div class="legend"><span><i style="background:var(--red)"></i>Lead drop</span><span><i style="background:var(--ink)"></i>Restock</span><span><i></i>Confirmed</span><span><i style="border-style:dashed"></i>Rumored / released</span></div>
</div></div>
{cal.replace('<div class="rrow"><div class="pic"><img src="{{NIKE_SQ}}" alt=""></div><div><b>Alphafly 3</b>','<div class="rrow"><div class="pic"><img src="{{NIKE_SQ}}" alt=""></div><div><b>Alphafly 3</b>')}
<div class="cal-list">
  <div class="twocol">
    <div>
      <div class="shead"><h2>Upcoming</h2><span class="no">LIST VIEW · NEXT 30 DAYS</span></div>
      <div class="weekhead"><h3>Week of Sep 7</h3><span>6 DROPS</span></div>
      <div class="ledger">
        <div class="lrow"><div class="d">MON<b>07</b></div><div class="th"><div class="pic"><img src="{{{{HOKA_SQ}}}}" alt=""></div></div><div class="n">Hoka Mach X 3<small>Super trainer · $190 · Hoka.com, RW</small></div><a class="a" href="#">NOTIFY</a></div>
        <div class="lrow"><div class="d">TUE<b>08</b></div><div class="th"><div class="pic"><img src="{{{{ASICS_SQ}}}}" alt=""></div></div><div class="n">Asics Novablast 6<small>Daily trainer · $150 · Asics.com, Fleet Feet</small></div><a class="a" href="#">NOTIFY</a></div>
        <div class="lrow"><div class="d">WED<b>09</b></div><div class="th"><div class="pic"><img src="{{{{SAUC_SQ}}}}" alt=""></div></div><div class="n">Saucony Endorphin Elite 2<small>Racing · $275 · Saucony.com</small></div><a class="a" href="#">NOTIFY</a></div>
        <div class="lrow today"><div class="d">THU<b>10</b></div><div class="th"><div class="pic"><img src="{{{{NIKE_SQ}}}}" alt=""></div></div><div class="n">Nike Alphafly 3 Platinum Tint<small>Racing · $305 · 10:00 AM ET · Nike.com, RW, Fleet Feet</small></div><a class="a hot" href="#">NOTIFY</a></div>
        <div class="lrow"><div class="d">THU<b>10</b></div><div class="th"><div class="pic"><img src="{{{{ON_SQ}}}}" alt=""></div></div><div class="n">On Cloudboom Strike LS<small>Racing · $330 · On.com</small></div><a class="a" href="#">NOTIFY</a></div>
        <div class="lrow"><div class="d">SAT<b>12</b></div><div class="th"><div class="pic"><img src="{{{{ADI_SQ}}}}" alt=""></div></div><div class="n">adidas Adios Pro 4<small>Restock · $255 · adidas.com</small></div><span class="chip chip--fill">RESTOCK</span></div>
      </div>
      <div class="weekhead"><h3>Week of Sep 14</h3><span>4 DROPS · 1 RUMORED</span></div>
      <div class="ledger">
        <div class="lrow"><div class="d">MON<b>14</b></div><div class="th"><div class="pic"><img src="{{{{NB_SQ}}}}" alt=""></div></div><div class="n">New Balance SC Elite v5<small>Racing · $250</small></div><a class="a" href="#">NOTIFY</a></div>
        <div class="lrow"><div class="d">WED<b>16</b></div><div class="th"><div class="pic"><img src="{{{{PUMA_SQ}}}}" alt=""></div></div><div class="n">Puma Fast-R Nitro Elite 3<small>Racing · $300</small></div><a class="a" href="#">NOTIFY</a></div>
        <div class="lrow"><div class="d">THU<b>17</b></div><div class="th"><div class="pic"><img src="{{{{ROCKET_SQ}}}}" alt=""></div></div><div class="n">Hoka Rocket X 3<small>Racing · $250</small></div><a class="a" href="#">NOTIFY</a></div>
        <div class="lrow"><div class="d">FRI<b>18</b></div><div class="th"><div class="pic"><img src="{{{{PEGPLUS2_SQ}}}}" alt=""></div></div><div class="n">Nike Pegasus Plus 2<span class="rum">RUMORED</span><small>Daily trainer · est. $180 · source: retailer listing</small></div><a class="a" href="#">WATCH</a></div>
        <div class="lrow"><div class="d">SUN<b>20</b></div><div class="th"><div class="pic"><img src="{{{{ADI_TOP}}}}" alt=""></div></div><div class="n">adidas Adios Pro 4 'Berlin'<small>Racing · $255 · Lead drop</small></div><a class="a hot" href="#">NOTIFY</a></div>
      </div>
      <div class="weekhead"><h3>Week of Sep 21</h3><span>3 DROPS · 1 RUMORED</span></div>
      <div class="ledger">
        <div class="lrow"><div class="d">TUE<b>22</b></div><div class="th"><div class="pic"><img src="{{{{BROOKS_SQ}}}}" alt=""></div></div><div class="n">Brooks Hyperion Elite 5<small>Racing · $275</small></div><a class="a" href="#">NOTIFY</a></div>
        <div class="lrow"><div class="d">THU<b>24</b></div><div class="th"><div class="pic"><img src="{{{{VF4_SQ}}}}" alt=""></div></div><div class="n">Nike Vaporfly 4 Volt<small>Racing · $260</small></div><a class="a" href="#">NOTIFY</a></div>
        <div class="lrow"><div class="d">SAT<b>26</b></div><div class="th"><div class="pic"><img src="{{{{MIZ_SQ}}}}" alt=""></div></div><div class="n">Mizuno Wave Rebellion Pro 3<span class="rum">RUMORED</span><small>Racing · est. $250 · source: Japan release</small></div><a class="a" href="#">WATCH</a></div>
      </div>
    </div>
    <div>
      <div class="shead"><h2>Moved &amp; changed</h2><span class="no">LAST 7 DAYS</span></div>
      <div class="movedbox">
        <h4>Delays</h4>
        <div><b>Hoka Cielo X1 2.0</b><s>Sep 4</s> → Oct 2 · Hoka confirmed via retailer memo</div>
        <div><b>Altra Vanish Carbon 3</b><s>Sep 30</s> → Oct 14 · Running Warehouse listing updated</div>
      </div>
      <div class="movedbox">
        <h4>Price changes</h4>
        <div><b>Nike Alphafly 3</b>$285 → <span class="up">$305</span> on all new colorways</div>
        <div><b>Saucony Endorphin Pro 4</b>$225 → $180 at Fleet Feet · deal</div>
      </div>
      <div class="movedbox">
        <h4>Newly confirmed</h4>
        <div><b>adidas Adios Pro 4 'Berlin'</b>Sep 20 · was rumored, now confirmed by adidas</div>
        <div><b>Nike Vaporfly 4 Volt</b>Sep 24 · colorway and date confirmed</div>
      </div>
    </div>
  </div>
</div>
<div class="band"><div class="band__in"><h2>Follow a shoe.<br><span>We'll do the refreshing.</span></h2><div><form class="sms" onsubmit="return false"><input type="tel" placeholder="Your mobile number"><button class="btn">Get alerts</button></form><div class="fine">FREE · ONE TEXT PER DROP YOU FOLLOW · REPLY STOP TO LEAVE</div></div></div></div>
</section>

<!-- ================= SHOES INDEX ================= -->
<section class="page" id="shoes">
<div class="phead">
  <div>
    <div class="kick"><span class="tag">Database</span><span>{len(SHOES)} shoes tracked · 9 reviewed · updated Sat Sep 5</span></div>
    <h1>Every shoe <em>we track.</em></h1>
    <p class="dek">Specs, release status, and the three-tier score on one card. Filter by what matters to you, or start from a list built around how you run.</p>
  </div>
  <div class="stats"><div><h5>Tracked</h5><b>{len(SHOES)}</b><span>ACROSS 9 BRANDS</span></div><div><h5>Reviewed</h5><b>9</b><span>RUNNERDROPS SCORE</span></div><div><h5>Runner reviews</h5><b>4.1K</b><span>SYNTHESIZED</span></div></div>
</div>
<div class="bestfor">
  <div class="shead"><h2>Best for</h2><span class="no">RANKED LISTS · UPDATED WEEKLY</span><a class="more" href="#">All lists</a></div>
  <div class="bestfor__grid">
    <a class="bf bf--red" href="#"><h3>HYROX</h3><div class="stack"><i><img src="{{{{HOKA_SQ}}}}" alt=""></i><i><img src="{{{{ASICS_SQ}}}}" alt=""></i><i><img src="{{{{PUMA_SQ}}}}" alt=""></i></div><span>8 SHOES · 612 RUNNERS</span></a>
    <a class="bf" href="#"><h3>Marathon racers</h3><div class="stack"><i><img src="{{{{NIKE_SQ}}}}" alt=""></i><i><img src="{{{{ADI_SQ}}}}" alt=""></i><i><img src="{{{{META_SQ}}}}" alt=""></i></div><span>10 SHOES · 1,840 RUNNERS</span></a>
    <a class="bf" href="#"><h3>Daily trainers under $150</h3><div class="stack"><i><img src="{{{{ASICS_SQ}}}}" alt=""></i><i class="ph"></i><i class="ph"></i></div><span>10 SHOES · 920 RUNNERS</span></a>
    <a class="bf" href="#"><h3>Low drop trainers</h3><div class="stack"><i><img src="{{{{NB_SQ}}}}" alt=""></i><i><img src="{{{{HOKA_SQ}}}}" alt=""></i><i><img src="{{{{ON_SQ}}}}" alt=""></i></div><span>8 SHOES · 540 RUNNERS</span></a>
    <a class="bf" href="#"><h3>Trail</h3><div class="stack"><i class="ph"></i><i class="ph"></i><i class="ph"></i></div><span>10 SHOES · 710 RUNNERS</span></a>
    <a class="bf bf--ink" href="#"><h3>Wide feet</h3><div class="stack"><i><img src="{{{{PRO4_SQ}}}}" alt=""></i><i><img src="{{{{ASICS_SQ}}}}" alt=""></i><i><img src="{{{{SAUC_SQ}}}}" alt=""></i></div><span>7 SHOES · 388 RUNNERS</span></a>
  </div>
</div>
<div class="dbwrap">
  <aside class="facets">
    <h4>Category</h4>{catfacets}
    <h4>Brand</h4>{brandfacets}<label class="fct"><span class="dim">+ 5 more</span></label>
    <h4>Drop</h4><div class="rng"><input value="0 mm"><span>TO</span><input value="12 mm"></div>
    <h4>Price</h4><div class="rng"><input value="$100"><span>TO</span><input value="$350"></div>
    <h4>Plate</h4>{facet('Carbon',12)}{facet('Pebax / nylon',1)}{facet('None',1)}
    <h4>Status</h4>{facet('Released',6)}{facet('Upcoming',8)}{facet('Reviewed by us',9)}
    <button class="btn btn--ghost">Clear filters</button>
  </aside>
  <div>
    <div class="sortbar"><div class="count">{len(SHOES)} shoes<small>SHOWING ALL</small></div><div class="right"><span class="dim">SORT</span><select class="sel"><option>Runner score</option><option>RunnerDrops score</option><option>Release date</option><option>Price · low to high</option><option>Weight</option></select></div></div>
    <div class="sgrid">{cards}</div>
    <div class="pager"><a class="is-on" href="#">1</a><a href="#">2</a><a href="#">3</a><a href="#">→</a></div>
  </div>
</div>
</section>

<!-- ================= BEST FOR: HYROX ================= -->
<section class="page" id="best">
<div class="crumbs">Shoes / Best for / HYROX</div>
<div class="phead">
  <div>
    <div class="kick"><span class="tag tag--red">Best for</span><span>Ranked list</span><span>·</span><span>Updated Sep 5</span></div>
    <h1>The 8 best shoes for <em>HYROX.</em></h1>
    <p class="dek">Eight kilometers of running broken up by sleds, burpees and carries. The fastest shoe isn't the best shoe here; the one that survives the stations is. Ranked by our testing, the expert consensus, and 612 runners who've raced in them.</p>
    <div class="byline"><span>BY <b>RUNNERDROPS TESTING TEAM</b></span><span>8 SHOES</span><span>612 RUNNER REVIEWS</span><span>LAST CHANGE: MACH X 3 → #1</span></div>
  </div>
  <div class="pull"><p>The fastest shoe isn't the best shoe here.</p><cite>— HOW WE RANK FOR HYROX</cite></div>
</div>
<div class="listwrap">
  <div>
    <div class="method"><span class="n">HOW</span><div><h4>How this list is ranked</h4><p>Weighted blend of the three tiers: 40% RunnerDrops testing (we raced in each pair), 30% expert consensus, 30% runner reviews filtered to people who mention HYROX, sled work or station racing. Shoes we haven't tested yet are ranked on the other two tiers and marked. Re-ranked every Monday as reviews come in.</p></div></div>
    {ranks}
    <div class="shead"><h2>Didn't make the cut</h2><span class="no">AND WHY</span></div>
    <div class="ledger">
      <div class="lrow"><div class="d"><b>09</b></div><div class="th"><div class="pic"><img src="{{{{NIKE_SQ}}}}" alt=""></div></div><div class="n">Nike Alphafly 3<small>Our 9.2, but the Air pods are a liability on the sled push and burpees. Marathon shoe, not a HYROX shoe.</small></div><a class="a" href="#">REVIEW</a></div>
      <div class="lrow"><div class="d"><b>10</b></div><div class="th"><div class="pic"><img src="{{{{CIELO_SQ}}}}" alt=""></div></div><div class="n">Hoka Cielo X1 2.0<small>Too much stack for the lateral stations. Great on the road, unstable on the carpet.</small></div><a class="a" href="#">REVIEW</a></div>
    </div>
  </div>
  <aside class="calrail">
    <div class="jump"><h4>In this list</h4>{''.join(f'<a href="#"><i>{i+1:02d}</i>{byk[k]["n"]}</a>' for i,(k,*_) in enumerate(HYROX))}</div>
    <div class="rel" style="margin-top:22px">
      <div class="rel__head"><span>HYROX drop alerts</span><span class="chip chip--red">Free</span></div>
      <div class="rel__body"><h4>Text me when a shoe on this list drops or restocks.</h4><p>One message per drop. We'll also text you when the ranking changes.</p><input type="tel" placeholder="Your mobile number"></div>
      <div class="rel__buy"><button>Follow this list</button></div>
    </div>
    <div class="related"><div class="railkick">Related lists</div>
      <a class="bf" href="#"><h3>Low drop trainers</h3><span>8 SHOES</span></a>
      <a class="bf" href="#"><h3>Super trainers</h3><span>9 SHOES</span></a>
      <a class="bf" href="#"><h3>Best outsole grip</h3><span>10 SHOES</span></a>
    </div>
  </aside>
</div>
</section>

<!-- ================= BRANDS INDEX ================= -->
<section class="page is-on" id="brands">
<div class="phead">
  <div>
    <div class="kick"><span class="tag">Brands</span><span>20 brands · A to Z</span></div>
    <h1>Brands.</h1>
    <p class="dek">Pick a brand for its release calendar, lineup, reviews and price history. Follow one and every drop, restock and price change from them lands in a text.</p>
  </div>
  <div class="right" style="justify-self:end"><div class="search"><input placeholder="Search a brand or model"><button>GO</button></div></div>
</div>
<div class="btgrid-wrap"><div class="btgrid">{btiles}</div></div>
<div class="band"><div class="band__in"><h2>Follow a brand.<br><span>Every drop, one text.</span></h2><div><form class="sms" onsubmit="return false"><input type="tel" placeholder="Your mobile number"><button class="btn">Get alerts</button></form><div class="fine">FREE · ONE TEXT PER DROP · REPLY STOP TO LEAVE</div></div></div></div>
</section>

<!-- ================= BRAND: NIKE ================= -->
<section class="page" id="brand">
<div class="crumbs">Brands / Nike</div>
<div class="bhead">
  <div>
    <div class="kick"><span class="tag">Brand</span><span>Beaverton, OR</span><span>·</span><span>6 upcoming · 4 reviewed</span></div>
    <h1>Nike</h1>
    <p class="dek">The Alphafly and Vaporfly set the super-shoe template and still move the most units of anything we track. Also the brand most likely to raise a price mid-cycle, so the price watch below earns its keep.</p>
  </div>
  <div><div class="stats"><div><h5>Upcoming</h5><b>6</b><span>NEXT: SEP 10</span></div><div><h5>Runners</h5><b>87%</b><span>AVG · 2,310 REVIEWS</span></div><div><h5>Avg retail</h5><b>$249</b><span>UP $12 YOY</span></div></div><a class="btn" href="#" style="width:100%;margin-top:12px">Follow Nike</a></div>
</div>
<div class="bwrap">
  <div>
    <div class="shead"><h2>Upcoming</h2><span class="no">6 DROPS · 2 RUMORED</span><a class="more" href="#">Calendar</a></div>
    <div class="ledger">
      <div class="lrow today"><div class="d">SEP<b>10</b></div><div class="th"><div class="pic"><img src="{{{{NIKE_SQ}}}}" alt=""></div></div><div class="n">Alphafly 3 Platinum Tint<small>Racing · $305 · 10:00 AM ET · Lead drop</small></div><a class="a hot" href="#">NOTIFY</a></div>
      <div class="lrow"><div class="d">SEP<b>18</b></div><div class="th"><div class="pic"><img src="{{{{PEGPLUS2_SQ}}}}" alt=""></div></div><div class="n">Pegasus Plus 2<span class="rum">RUMORED</span><small>Daily trainer · est. $180</small></div><a class="a" href="#">WATCH</a></div>
      <div class="lrow"><div class="d">SEP<b>24</b></div><div class="th"><div class="pic"><img src="{{{{VF4_SQ}}}}" alt=""></div></div><div class="n">Vaporfly 4 Volt<small>Racing · $260</small></div><a class="a" href="#">NOTIFY</a></div>
      <div class="lrow"><div class="d">OCT<b>03</b></div><div class="th"><div class="pic"><img src="{{{{NIKE_OUT}}}}" alt=""></div></div><div class="n">Alphafly 3 Volt<small>Restock · $305 · Nike.com</small></div><span class="chip chip--fill">RESTOCK</span></div>
      <div class="lrow"><div class="d">OCT<b>15</b></div><div class="th"><div class="pic"><img src="{{{{PEG42_SQ}}}}" alt=""></div></div><div class="n">Pegasus 42 Shield<small>Daily trainer · $150 · Winterized</small></div><a class="a" href="#">NOTIFY</a></div>
      <div class="lrow"><div class="d">NOV<b>TBC</b></div><div class="th"><div class="pic"><img src="{{{{AF4_SQ}}}}" alt=""></div></div><div class="n">Alphafly 4<span class="rum">RUMORED</span><small>Racing · est. $310 · source: athlete samples at Berlin</small></div><a class="a" href="#">WATCH</a></div>
    </div>
    <div class="shead"><h2>Lineup</h2><span class="no">BY CATEGORY</span></div>
    <div class="kick" style="margin-bottom:10px"><span class="tag tag--red">Racing</span><span class="dim">3 shoes · all reviewed</span></div>
    <div class="lineup">
      {card(byk['alphafly'])}{card(byk['vf4'])}{card(byk['vf3'])}
    </div>
    <div class="kick" style="margin:22px 0 10px"><span class="tag">Daily trainer</span><span class="dim">2 shoes · 1 reviewed</span></div>
    <div class="lineup">
      <article class="sc"><div class="pic"><img src="{{{{PEG42_SQ}}}}" alt=""><span class="stamp stamp--paper">Released</span></div><div class="sc__b"><div class="kick"><span class="tag">Nike</span><span class="dim">Daily trainer</span></div><h3>Pegasus 42</h3><div class="spec">$150 · 9.6 oz · 10 mm · None</div><div class="scores"><div><h5>RunnerDrops</h5><b>8.0<small>/10</small></b></div><div><h5>Reviewers</h5><b>84<small>%</small></b></div><div><h5>Runners</h5><b>89<small>%</small></b></div></div><div class="sc__f"><a href="#">SHOE PAGE</a><a href="#" class="hot">NOTIFY</a></div></div></article>
      <article class="sc"><div class="pic"><img src="{{{{PEGPLUS2_SQ}}}}" alt=""><span class="stamp">Rumored</span></div><div class="sc__b"><div class="kick"><span class="tag">Nike</span><span class="dim">Daily trainer · Rumored</span></div><h3>Pegasus Plus 2</h3><div class="spec">est. $180 · — · — · —</div><div class="scores"><div><h5>RunnerDrops</h5><b class="na">—</b></div><div><h5>Reviewers</h5><b class="na">—</b></div><div><h5>Runners</h5><b class="na">—</b></div></div><div class="sc__f"><a href="#">SHOE PAGE</a><a href="#" class="hot">WATCH</a></div></div></article>
    </div>
  </div>
  <aside class="calrail">
    <div class="rel">
      <div class="rel__head"><span>Nike alerts</span><span class="chip chip--red">Free</span></div>
      <div class="rel__body"><h4>Every Nike drop, one text.</h4><p>Or narrow it to the models you'd actually buy.</p><input type="tel" placeholder="Your mobile number"><h5>Models</h5><div class="chips"><span class="chip chip--fill">Alphafly</span><span class="chip chip--fill">Vaporfly</span><span class="chip">Pegasus</span><span class="chip">Streakfly</span><span class="chip">Zegama</span></div></div>
      <div class="rel__buy"><button>Follow Nike</button></div>
    </div>
    <div class="railkick">Price watch</div>
    <div class="rel">
      <div class="pricewatch"><div><b>Alphafly 3</b><span class="mono dim">JUN 2026</span></div><span class="mono">$285</span><span class="mono up">→ $305</span></div>
      <div class="pricewatch"><div><b>Vaporfly 4</b><span class="mono dim">LAUNCH</span></div><span class="mono">$260</span><span class="mono dim">—</span></div>
      <div class="pricewatch"><div><b>Pegasus 42</b><span class="mono dim">AUG 2026</span></div><span class="mono">$150</span><span class="mono dim">—</span></div>
    </div>
    <div class="railkick">Most followed</div>
    <div class="rrow"><div class="pic"><img src="{{{{NIKE_SQ}}}}" alt=""></div><div><b>Alphafly 3 Platinum</b><div class="st">2,140 FOLLOWING</div></div><div class="nxt"><b>SEP 10</b></div></div>
    <div class="rrow"><div class="pic"><img src="{{{{VF4_SQ}}}}" alt=""></div><div><b>Vaporfly 4 Volt</b><div class="st">1,102 FOLLOWING</div></div><div class="nxt"><b>SEP 24</b></div></div>
    <div class="rrow"><div class="pic"><img src="{{{{VF3_SQ}}}}" alt=""></div><div><b>Vaporfly 3 Volt</b><div class="st">SOLD OUT · 22 MIN</div></div><div class="nxt"><b>GONE</b></div></div>
  </aside>
</div>
</section>

{foot}
<script>
const tabs=document.querySelectorAll('.comp .dev button');
function go(k){{tabs.forEach(b=>b.classList.toggle('is-on',b.dataset.p===k));document.querySelectorAll('.page').forEach(p=>p.classList.toggle('is-on',p.id===k));
 const m={{cal:'nav-cal',shoes:'nav-shoes',best:'nav-shoes',brands:'nav-brands',brand:'nav-brands'}};document.querySelectorAll('.nav__links a').forEach(a=>a.classList.toggle('is-on',a.id===m[k]));window.scrollTo({{top:0,behavior:'smooth'}});}}
tabs.forEach(b=>b.addEventListener('click',()=>go(b.dataset.p)));
document.getElementById('nav-cal').onclick=e=>{{e.preventDefault();go('cal')}};document.getElementById('nav-shoes').onclick=e=>{{e.preventDefault();go('shoes')}};document.getElementById('nav-brands').onclick=e=>{{e.preventDefault();go('brands')}};
document.querySelectorAll('#shoes .bf--red, #best .jump a').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();go('best')}}));
document.querySelectorAll('#brands .bt').forEach(a=>a.addEventListener('click',e=>{{e.preventDefault();if(a.textContent.includes('Nike'))go('brand')}}));
</script>
</body></html>'''
PAGES=re.sub(r'src="\{\{([A-Z_0-9]+)\}\}"',r'data-img="\1" src=""',PAGES)
PAGES=PAGES.replace('</body>','<script>const IMG='+json.dumps(d)+';document.querySelectorAll("img[data-img]").forEach(i=>i.src=IMG[i.dataset.img]);</script></body>')
left=set(re.findall(r'\{\{[A-Z_0-9]+\}\}',PAGES)); print('unreplaced',left)
open('/mnt/user-data/outputs/RunnerDrops_Section_Pages.html','w').write(PAGES); print(len(PAGES)//1000,'KB')
