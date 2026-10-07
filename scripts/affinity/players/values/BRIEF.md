# Values tagging (Kevin, 2026-10-07, quiz round 11)

Tag each player on ten off-pitch traits Kevin weighted in quiz round 11. Facts only, documented in reliable sources; when
unsure or nothing is known, use 0. Neutral wording. Today is October 2026. Use the batch file's causes/stances as leads and
check with a web search for anything you tag non-zero. Do not read scores/, ratings.json, lists.json or other outputs.

Traits (value 0 = not true / nothing known; 1 = clearly true; 0.5 = partly or briefly true):
- causes: spoke out publicly on racism, inequality or other social justice issues (campaigns, statements, taking a stand).
- armband: wore the rainbow armband / backed Pride or LGBTQ+ inclusion publicly (OneLove armband plans count; coming out counts).
- refused_pride: refused to wear a Pride shirt/armband, or made anti-LGBTQ+ remarks.
- left: publicly campaigned for or endorsed a left-leaning candidate or party (e.g. US Democrats, Lula, Labour).
- right: publicly campaigned for or endorsed a right-leaning or hard-right candidate or party (e.g. Trump, Bolsonaro, Le Pen).
- gives: substantial charity of their own: funding schools, clinics, hospitals, foundations (not just appearances).
- fair: known for fair play and sportsmanship (1); known for diving, simulation or time-wasting: use -1. 0 if neither.
- private: low-key private life (1); flashy lifestyle and big social-media brand: use -1. 0 if neither.
- speaks_up: publicly criticised FIFA, UEFA, league bosses or club owners (fixture load, Qatar, Super League, ownership).
- betting: fronted a betting, casino or crypto/NFT brand as a paid ambassador (1); 0.5 for a small or brief deal.

Output values/outN.json: {"Player Name": {"causes": 1, "armband": 0, "refused_pride": 0, "left": 0, "right": 0, "gives": 0.5,
"fair": 0, "private": 1, "speaks_up": 0, "betting": 0, "notes": "one short clause per non-zero tag, with year"}} for every
player in the batch, exact names. Check the JSON parses with python3. No other files, no git.
