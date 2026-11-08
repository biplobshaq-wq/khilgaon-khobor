# Khilgaon event-news watcher: Google News RSS -> index.html + data.json
import json, re, os, html, urllib.parse, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
BD = timezone(timedelta(hours=6))
AREAS = ['খিলগাঁও','খিলগাঁওয়ে','খিলগাঁয়ে','Khilgaon','তালতলা','গোড়ান','মেরাদিয়া','বাসাবো','সিপাহীবাগ','নন্দীপাড়া','ত্রিমোহনী','নাসিরাবাদ']
KEYS = ['মিলাদ','দোয়া','দোআ','চেহলাম','চল্লিশা','কুলখানি','মৃত্যুবার্ষিকী','মৃত্যু বার্ষিকী','উদ্বোধন','তবারক','তাবারক','তবরুক','মেজবান','মেজবানি','জেয়াফত','জিয়াফত','শিরনি','ভোজ','ওরস','মাহফিল','ইফতার','খাবার বিতরণ','কাঙালি','স্মরণসভা','শোকসভা','জন্মবার্ষিকী','পাগড়ি','ওয়াজ','বার্ষিকী','অনুষ্ঠান','সমাপনী','দাওয়াত','জানাজা']
QUERIES = ['খিলগাঁও', 'খিলগাঁওয়ে', 'Khilgaon'] + ['খিলগাঁও ' + k for k in ['মিলাদ','দোয়া মাহফিল','চেহলাম','কুলখানি','মৃত্যুবার্ষিকী','উদ্বোধন','তবারক','মেজবান','মাহফিল','খাবার বিতরণ']]
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36'}
DATA = 'data.json'
def fetch(q):
    u = 'https://news.google.com/rss/search?q=' + urllib.parse.quote(q + ' when:14d') + '&hl=bn&gl=BD&ceid=BD:bn'
    try:
        return ET.fromstring(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read())
    except Exception as e:
        print('ERR', q, e); return None
def clean(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s or ''))).strip()
old = json.load(open(DATA, encoding='utf-8')) if os.path.exists(DATA) else {}
now = datetime.now(BD)
for q in QUERIES:
    r = fetch(q)
    if r is None: continue
    for it in r.findall('.//item'):
        t = clean(it.findtext('title')); link = it.findtext('link') or ''
        desc = clean(it.findtext('description'))
        txt = t + ' ' + desc
        if any(x in txt for x in ['পূবাইল','গাজীপুর','টঙ্গী']): continue
        hit = [k for k in KEYS if k in txt]
        if not hit: continue
        key = re.sub(r'\s+-\s+[^-]+$', '', t)[:80]
        if key in old: continue
        try: d = parsedate_to_datetime(it.findtext('pubDate')).astimezone(BD)
        except Exception: d = now
        src = it.findtext('source') or ''
        old[key] = {'title': re.sub(r'\s+-\s+[^-]+$', '', t), 'src': src, 'link': link, 'date': d.isoformat(),
                    'found': now.isoformat(), 'keys': hit[:4],
                    'soon': any(w in txt for w in ['আগামী','আগামীকাল','আজ ','অনুষ্ঠিত হবে','হবে।','করা হবে'])}
# keep 60 days
cut = now - timedelta(days=60)
old = {k: v for k, v in old.items() if datetime.fromisoformat(v['date']) > cut}
json.dump(old, open(DATA, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
items = sorted(old.values(), key=lambda v: v['date'], reverse=True)
BN = str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')
MON = ['জানুয়ারি','ফেব্রুয়ারি','মার্চ','এপ্রিল','মে','জুন','জুলাই','আগস্ট','সেপ্টেম্বর','অক্টোবর','নভেম্বর','ডিসেম্বর']
def bd(iso):
    d = datetime.fromisoformat(iso); return f"{str(d.day).translate(BN)} {MON[d.month-1]}"
rows = ''
for v in items:
    new = (now - datetime.fromisoformat(v['found'])).days < 1
    tag = ('<b class=s>🔔 সামনে হবে</b> ' if v['soon'] else '') + ('<b class=n>নতুন</b> ' if new else '')
    rows += f"<a class=c href='{html.escape(v['link'])}' target=_blank><div class=d>{bd(v['date'])} · {html.escape(v['src'])}</div>{tag}<div class=t>{html.escape(v['title'])}</div><div class=k>{' · '.join(v['keys'])}</div></a>"
if not rows: rows = "<p class=e>গত ১৪ দিনে পত্রিকায় খিলগাঁওয়ের কোনো মিলাদ / দোয়া / চেহলাম / উদ্বোধনের খবর আসেনি। প্রতি ৬ ঘণ্টায় আবার খোঁজা হয়।</p>"
page = f"""<!doctype html><html lang=bn><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'>
<title>খিলগাঁও অনুষ্ঠানের খবর</title><style>
body{{font-family:system-ui,'Noto Sans Bengali',sans-serif;background:#f4f1ea;margin:0;padding:14px;color:#222;max-width:680px;margin:auto}}
h1{{font-size:22px;margin:6px 0}} .u{{color:#666;font-size:14px;margin-bottom:12px}}
.c{{display:block;background:#fff;border-radius:12px;padding:12px 14px;margin:10px 0;text-decoration:none;color:#222;box-shadow:0 1px 3px #0002}}
.d{{font-size:13px;color:#777}} .t{{font-size:17px;font-weight:600;margin:4px 0}} .k{{font-size:13px;color:#2a7}}
.s{{background:#e33;color:#fff;border-radius:6px;padding:1px 6px;font-size:12px}} .n{{background:#36c;color:#fff;border-radius:6px;padding:1px 6px;font-size:12px}}
.e{{background:#fff;padding:16px;border-radius:12px}}</style></head><body>
<h1>🕌 খিলগাঁও অনুষ্ঠানের খবর</h1><div class=u>মিলাদ · দোয়া · চেহলাম · কুলখানি · মৃত্যুবার্ষিকী · উদ্বোধন · মেজবান<br>শেষ খোঁজা: {bd(now.isoformat())}, {now.strftime('%I:%M %p').translate(BN)} (প্রতি ৬ ঘণ্টায় নিজে থেকে খোঁজে)</div>
{rows}</body></html>"""
open('index.html', 'w', encoding='utf-8').write(page)
print(len(items), 'items')
