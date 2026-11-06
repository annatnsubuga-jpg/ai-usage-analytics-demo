#!/usr/bin/env python3
"""Build template.json from scratch for a fictional 120-person publisher.

Nothing here is derived from any real dataset. The roster, the department split,
the seat economics, the invoice figures and every activity number are generated
from the constants below, so no magnitude in the demo traces back to anywhere.

Run this only when the shape of the fiction needs to change. Day to day,
generate.py rolls this template forward a month at a time.
"""
import json, random, os, datetime as dt

BASE = os.path.dirname(os.path.abspath(__file__))
def _p(*a): return os.path.join(BASE, *a)

RNG = random.Random(20261029)

ORG   = "Ashgrove Press"
DOMAIN= "ashgrovepress.test"
DEPTS = {"Department 1":9, "Department 2":7, "Department 3":6,
         "Department 4":4, "Department 5":4}
HEAD  = sum(DEPTS.values())                      # 120
SEATS_PURCHASED, SEATS_IN_USE = 34, 30
SEATS_BILLED   = 31   # 30 in use + 1 invite outstanding, of 34 purchased
SEAT_RATE_GBP  = 24.90                           # per seat per month
# "placeholder" labels people as (Name 01) with a generic (Job title), so nothing in the demo
# can be mistaken for a real person. "invented" uses the fictional name pools below instead.
NAMING = "placeholder"

GIVEN = ["Abel","Agnes","Anneke","Bjorn","Callum","Dara","Dmitri","Emeka","Greta","Halim",
 "Hugo","Ilse","Imani","Ingrid","Jonas","Juno","Kwame","Leila","Linnea","Lukas","Noor","Ode",
 "Pia","Ravi","Rowan","Saoirse","Selina","Soren","Tariq","Theo","Viktor","Zuri","Mirela","Tomas",
 "Nadia","Elif","Jonah","Petra","Casimir","Yusuf","Marit","Otto","Sanne","Bram","Tove","Niamh",
 "Rafael","Annika","Cosmo","Esme","Fenna","Gideon","Hana","Isidore","Jolanta","Kasper","Liesel",
 "Malou","Nerys","Osian","Perrin","Quilla","Rasmus","Sable","Tadeo","Ulla","Veda","Wim","Xanthe",
 "Yannick","Zola","Alba","Benedek","Ciaran","Delphine","Eero","Faye","Guro","Hedda","Idris",
 "Janvier","Kiri","Lorcan","Maja","Nikolai","Orla","Pascale","Quentin","Rune","Sigrid","Taavi",
 "Ursula","Vesna","Wren","Yael","Zephyr","Amara","Brielle","Cato","Dagny","Elowen","Fabian",
 "Giselle","Hamish","Iria","Jarek","Kenji","Lysander","Mireille","Nils","Oriane","Priya","Raul",
 "Senna","Thabo","Ulrich","Vidar","Wanda","Ylva","Zubair","Caius","Mirren"]
SUR = ["Rutherford","Whitlock","Jerrold","Zabala","Novak","Eriksen","Jarvis","Dessau","Tennant",
 "Hartmann","Lindqvist","Fairweather","Dunmore","Partridge","Ibori","Ashworth","Fenwick","Castellan",
 "Ingram","Bellamy","Ueda","Vasquez","Arkwright","Everley","Quill","Yeomans","Okonjo","Yarrow",
 "Winterbourne","Calloway","Oyelaran","Rasmussen","Quintero","Marchetti","Halloran","Pemberton",
 "Oduya","Strand","Vance","Blackwood","Carrow","Delacroix","Fairlie","Grimshaw","Holloway","Ivers",
 "Kestrel","Lammert","Mowbray","Nystrom","Ormerod","Prydain","Rooke","Selby","Thorne","Underhill",
 "Vilhjalm","Wrenfield","Yates","Abernethy","Brightwell","Cadogan","Dunsmore","Ellery","Fallowfield",
 "Garbutt","Hawksley","Inchbald","Jellicoe","Kirkbride","Lavenham","Merriweather","Netherton",
 "Oakhurst","Pennington","Quarles","Ravensworth","Stapleton","Trelawney","Urquhart","Vennor",
 "Wolstenholme","Yelverton","Ziegler","Anstruther","Birtwistle","Colquhoun","Dalrymple","Ennismore",
 "Fotheringay","Gillingwater","Harkaway","Illingworth","Jephcott","Kenwright","Longstaffe","Moncrieff",
 "Norrington","Oglethorpe","Pargeter","Quennell","Redmayne","Sitwell","Tarbuck","Uttley","Villiers",
 "Wadsworth","Yoxall","Zouche","Ashcombe","Braithwaite","Chadderton","Drummond","Elphinstone",
 "Farquhar","Glendinning","Hesketh","Inglethorpe","Jerningham","Kettlewell"]

TITLES = {
 "Editorial":["Commissioning Editor","Development Editor","Assistant Editor","Editorial Assistant",
   "Senior Editor","Managing Editor","Copy Editor","Editorial Director","Series Editor","Proofreader"],
 "Production":["Production Controller","Head of Production","Production Editor","Typesetter",
   "Print Buyer","Audio Producer","Production Assistant","Studio Manager"],
 "Marketing":["Campaign Manager","Publicist","Marketing Executive","Head of Marketing",
   "Social Media Manager","Events Coordinator","Marketing Assistant"],
 "Digital":["Head of Digital","Digital Producer","Metadata Specialist","Ecommerce Manager",
   "Data Analyst","Platform Engineer","Digital Assistant"],
 "Design":["Art Director","Designer","Senior Designer","Junior Designer","Cover Designer",
   "Production Designer"],
 "Rights & Contracts":["Rights Director","Senior Rights Manager","Contracts Manager",
   "Rights Executive","Permissions Assistant","Contracts Assistant"],
}

# ── roster ────────────────────────────────────────────────────────────────────
# one given name and one surname each, paired 1:1, so nobody shares either half
assert len(set(GIVEN)) >= HEAD and len(set(SUR)) >= HEAD, "name pools too small"
g_pool, s_pool = sorted(set(GIVEN)), sorted(set(SUR))
RNG.shuffle(g_pool); RNG.shuffle(s_pool)
names = [f"{g} {s}" for g, s in zip(g_pool[:HEAD], s_pool[:HEAD])]

people, emails = [], set()
i = 0
for dept, n in DEPTS.items():
    for _ in range(n):
        if NAMING == "placeholder":
            full  = f"Name {i+1}"
            local = f"person{i+1}"
            title = "Job title"
        else:
            full = names[i]
            g, s = full.split(" ", 1)
            local = f"{g.lower()}.{s[0].lower()}"
            k = 2
            while local in emails:
                local = f"{g.lower()}.{s[:k].lower()}"; k += 1
            title = RNG.choice(list(TITLES.values())[list(DEPTS).index(dept)])
        i += 1
        emails.add(local)
        people.append({"name": full, "email": f"{local}@{DOMAIN}", "dept": dept,
                       "title": title,
                       # How heavily this person uses the tools, fixed for their whole history.
                       # A real rollout has a tail who never take it up and a few who live in it.
                       "_intensity": RNG.choices([0.0,0.18,0.55,1.05,1.9,3.6],
                                                 [13,14,24,27,16,6])[0]})

# Only a small technical minority ever run Claude Code. A publisher is not an
# engineering org, and PR counts are what drive the time-saved figure, so letting
# everyone code produces a wildly overstated headline.
for p in people: p["_codes"] = False
for p in RNG.sample(people, max(2, round(HEAD * 0.18))): p["_codes"] = True

MONTHS = [("Mar",31),("Apr",30),("May",31),("Jun",30),("Jul",31),("Aug",31),("Sep",30)]
YEAR = 2026
ROLE = lambda idx: "Primary Owner" if idx == 0 else ("Owner" if idx < 4 else "User")

months = {}
for mi,(mon,days) in enumerate(MONTHS):
    growth = 0.45 + 0.11*mi                       # adoption climbs over the window
    members = []
    for idx,p in enumerate(people):
        f = p["_intensity"] * growth * RNG.uniform(.7,1.3)
        active = min(days, int(round(days * min(.94, f/1.7))) ) if f > .12 else 0
        chats  = int(max(0, RNG.gauss(14*f, 5*f)))
        msgs   = int(chats * RNG.uniform(3.5, 9.5))
        code   = int(max(0, RNG.gauss(9*f, 5*f))) if p["_codes"] else 0
        cow    = int(max(0, RNG.gauss(5*f, 3*f)))
        members.append({
          "name":p["name"], "email":p["email"], "dept":p["dept"], "title":p["title"],
          "role":ROLE(idx), "tier":"Premium" if p["_intensity"]>=1.05 else "Standard",
          "daysActive":active, "chats":chats, "messages":msgs,
          "projectsCreated":int(max(0,RNG.gauss(.8*f,.6*f))),
          "projectsUsed":int(max(0,RNG.gauss(1.1*f,.8*f))),
          "prs":int(code*RNG.uniform(.4,1.3)), "codeSessions":code,
          "fileEdits":int(max(0,RNG.gauss(9*f,6*f))),
          "coworkSessions":int(cow*RNG.uniform(.3,.8)), "coworkMessages":cow,
          "artifacts":int(max(0,RNG.gauss(4*f,3*f))),
          # only heavy users ever pass their plan limit, so most people never meter
          "spend":round(max(0.0, RNG.gauss(34*f, 26*f)), 2)
                   if (p["_intensity"] >= 1.9 and RNG.random() < .45) else 0.0,
        })
    months[f"{mon} {YEAR}"] = {"period":f"{mon} 1 - {mon} {days}", "days":days, "members":members}

TOTAL_DAYS = sum(d for _,d in MONTHS)
allm = []
for p in people:
    rows=[m["members"][people.index(p)] for m in months.values()]
    da=sum(r["daysActive"] for r in rows); msg=sum(r["messages"] for r in rows)
    cw=sum(r["coworkMessages"] for r in rows); cs=sum(r["codeSessions"] for r in rows)
    allm.append({"name":p["name"],"email":p["email"],"dept":p["dept"],"title":p["title"],
      "created":None,"ranked":da>=30,"messages":msg,"coworkMessages":cw,"codeSessions":cs,
      "daysActive":da,"availDays":TOTAL_DAYS,"pctDaysUsed":round(da/TOTAL_DAYS*100,1),
      "chatPerDay":round(msg/da,2) if da else 0,"coworkPerDay":round(cw/da,2) if da else 0,
      "codePerDay":round(cs/da,2) if da else 0})

dc = dict(DEPTS)
alltime = {"period":f"Mar 1 - Sep 30 {YEAR}", "days":TOTAL_DAYS, "minDaysToRank":30,
  "unranked":sum(1 for m in allm if not m["ranked"]), "noAccount":[],
  "deptPct":{k:round(v/HEAD*100,1) for k,v in dc.items()}, "deptCount":dc, "members":allm}

json.dump({"people":people,"months":months,"alltime":alltime},
          open(_p("_roster_tmp.json"),"w"), ensure_ascii=False)
print(f"roster: {HEAD} people across {len(DEPTS)} departments {dc}")
print(f"ranked: {sum(1 for m in allm if m['ranked'])}  unranked: {alltime['unranked']}")

# ── the rest of the document ──────────────────────────────────────────────────
# Everything below is derived from the roster above, so the figures agree with each
# other at any headcount. Nothing is a fixed magnitude.
sep   = months[f"Sep {YEAR}"]["members"]
aug   = months[f"Aug {YEAR}"]["members"]
jul   = months[f"Jul {YEAR}"]["members"]

top  = lambda rows,k,n=5: sorted(rows, key=lambda r: r[k], reverse=True)[:n]
sum_ = lambda rows,k: sum(r[k] for r in rows)

sep_active = sum(1 for m in sep if m["daysActive"] > 0)
sep_weekly = sum(1 for m in sep if m["daysActive"] >= 8)
sep_daily  = sum(1 for m in sep if m["daysActive"] >= 18)
aug_weekly = sum(1 for m in aug if m["daysActive"] >= 8)
coders     = [m for m in sep if m["codeSessions"] > 0]
cowork_use = [m for m in sep if m["coworkSessions"] > 0]

billed = sorted([m for m in sep if m["spend"] > 0.5], key=lambda m: m["spend"], reverse=True)
metered_total = round(sum(m["spend"] for m in billed), 2)
sub_amount    = round(SEATS_BILLED * SEAT_RATE_GBP, 2)
projected     = round(sub_amount + metered_total * 1.18, 2)
top_two_share = round((billed[0]["spend"] + billed[1]["spend"]) / metered_total * 100) if len(billed) > 1 else 0

usd = lambda rows: round(sum(m["spend"] for m in rows) * 1.27)
jul_usd, aug_usd, sep_usd = usd(jul), usd(aug), usd(sep)

prs   = sum_(sep,"prs");    cowork = sum_(sep,"coworkSessions")
convs = sum_(sep,"chats");  files  = sum_(sep,"fileEdits"); arts = sum_(sep,"artifacts")
designs = max(1, arts // 9)

# ── projects ──────────────────────────────────────────────────────────────────
_ALL = ["Autumn catalogue copy","Audiobook pipeline","Backlist royalties review","Blurb writer",
 "Contract clause library","Cover brief generator","Debut fiction scouting","Digital-first imprint",
 "Editorial calendar","Foreign rights tracker","Frankfurt prep","Indexing assistant",
 "Jacket copy drafts","Manuscript triage","Metadata cleanup","Newsletter","Permissions log",
 "Print run forecasting","Proof correction notes","Reader report summaries","Returns analysis",
 "Rights deal memos","Royalty statement checker","Sales conference deck","School and library outreach",
 "Series bible","Style sheet assistant","Submission responses","Subsidiary rights pipeline",
 "Supply chain and paper costs","Translation queries","Trade review digest","Typesetting spec",
 "Author care emails","Festival scheduling","Prize submissions","Repackage proposals","Social copy",
 "Warehouse stock queries","Publicity pitch drafts"]
RNG.shuffle(_ALL)
# roughly three projects for every five people: most are one person's working space
PROJECTS = _ALL[:max(4, min(len(_ALL), round(HEAD * 0.6)))]
MONN = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep"]
creators = [m["email"] for m in top(sep,"projectsCreated", max(3, round(HEAD * 0.35)))]

projectsAll = []
for proj in PROJECTS:
    users = RNG.choices([1,2,3,5], [78,14,6,2])[0]
    convos = RNG.choices([1,2,3,6,12], [38,24,18,14,6])[0]
    projectsAll.append({"project":proj, "users":users, "conversations":convos,
      "messages":int(max(1, RNG.gauss(14*convos, 9*convos))),
      "created":f"{RNG.choice(MONN[2:])} {RNG.randint(1,28)}, {YEAR}",
      "createdBy":RNG.choice(creators)})
projectsAll.sort(key=lambda r: r["messages"], reverse=True)
proj_msgs = sum(r["messages"] for r in projectsAll)
shared    = sum(1 for r in projectsAll if r["users"] > 1)
single    = sum(1 for r in projectsAll if r["conversations"] == 1)
distinct  = len({r["createdBy"] for r in projectsAll})

# ── connectors: reads scale with the people using them ────────────────────────
CONN = [("google-drive", .30, .07), ("notion", .22, .28), ("claude-ai-notion", .16, .95),
        ("Slack", .26, .12), ("claude-in-chrome", .18, 0.0)]
connectors = []
for name, share, wr in CONN:
    users = max(1, round(HEAD * share * RNG.uniform(.7,1.3)))
    reads = int(users * RNG.uniform(18, 52))
    connectors.append({"connector":name, "users":users, "reads":reads,
                       "writes":int(reads * wr * RNG.uniform(.7,1.3))})

# ── spend concentration ───────────────────────────────────────────────────────
spends = sorted((m["spend"] for m in sep), reverse=True)
tot    = sum(spends) or 1
top10  = round(sum(spends[:max(1, round(len(spends)*.1))]) / tot, 3)
n      = len(spends); asc = sorted(spends)
gini   = round((2*sum((i+1)*v for i,v in enumerate(asc)))/(n*sum(asc) or 1) - (n+1)/n, 3) if sum(asc) else 0

_dau = lambda rows: round(sum(m["daysActive"] for m in rows)/max(1,len(rows))/30, 2) if rows else 0

PRODUCTS = [("Claude Code", .46), ("Claude.ai", .31), ("Cowork", .18), ("Office Agents", .05)]

doc = {
 "meta":{"org":ORG,"seatsPurchased":SEATS_PURCHASED,"seatsInUse":SEATS_IN_USE,
   "seatsUnused":SEATS_PURCHASED-SEATS_IN_USE,"members":SEATS_BILLED,"invitesPending":2,
   "people":distinct,"deptTotals":dc,"generated":dt.date.today().isoformat(),
   "monthlySource":"Fictional data, regenerated automatically. Not a real organisation.",
   "snapshotSource":"Fictional data, regenerated automatically. Not a real organisation.",
   "schema":"v6","demo":True},
 "months":months, "allTime":alltime,
 "snapshot":{
   "fetchedAt":f"{YEAR}-10-06T09:00:00Z","window":f"September {YEAR} (rolling 30 days)",
   "dataAsOf":f"{YEAR}-09-30","source":"Fictional data, regenerated automatically.",
   "headline":{"weeklyActive":sep_weekly,"seats":SEATS_IN_USE,
     "weeklyActiveWoW":sep_weekly-aug_weekly,"prsCreated":prs,"coworkSessions":cowork,
     "totalSpend":round(metered_total)},
   "outputs":{"prsCreated":prs,"designsCreated":designs,"fileOperations":files,
     "conversations":convs,"mcpWrites":sum(c["writes"] for c in connectors)},
   "timeSaved":{"hours":round((prs*145 + files*1 + convs*4 + designs*37)/60),
     "assumptions":[{"output":f"{prs} PRs","minutesEach":145},
       {"output":f"{files} file operations","minutesEach":1},
       {"output":f"{convs} conversations","minutesEach":4},
       {"output":f"{designs} designs","minutesEach":37}]},
   "agentic":{"actionsPerPrompt":round(RNG.uniform(5.5,9.5),2)},
   "adoptionLevel":{"allMembers":SEATS_IN_USE,"monthly":sep_active,"weekly":sep_weekly,"daily":sep_daily},
   # stickiness is daily-over-monthly actives, measured per product rather than guessed
   # Days used divided by days available, averaged over the people who use each product.
   # Counting "people active 18+ days / people who touched it" pins to 1.0 the moment a
   # product has only two or three users, which is meaningless at this headcount.
   "stickiness":[
     {"product":"Claude.ai","dauMau":_dau(sep)},
     {"product":"Claude Code","dauMau":_dau(coders)},
     {"product":"Cowork","dauMau":_dau(cowork_use)},
     {"product":"Office Agents","dauMau":round(RNG.uniform(.05,.2),2)}],
   "skills":[{"skill":s,"builtBy":b,"runs":max(4, int(convs * r))} for s,b,r in
     [("blurb-writer",ORG,.21),("manuscript-triage",ORG,.17),("metadata-fixer",ORG,.09),
      ("code-review","Other",.12),("brainstorming","Other",.08),("inbox-triage","Other",.06)]],
   "connectors":connectors,
   "fileCategories":{"total":0,"asOf":f"{YEAR}-10-01","categories":[]},
   "topCoworkMembers":[{"email":m["email"],"sessions":m["coworkSessions"]} for m in top(sep,"coworkSessions")],
   "projects":projectsAll[:5],
   "projectsMeta":{"createdInWindow":sum(1 for r in projectsAll if r["created"].startswith(("Jul","Aug","Sep"))),
     "usersWithOneOrMore":round(distinct/SEATS_IN_USE,2),"totalProjects":len(projectsAll),
     "totalMessages":proj_msgs,"sharedProjects":shared,"distinctCreators":distinct,
     "singleConversation":single,
     "createdByMonth":[[m,sum(1 for r in projectsAll if r["created"].startswith(m))] for m in MONN],
     "source":"Fictional data, regenerated automatically.","coworkProjectsExcluded":True,
     "coworkNote":"These live in the cloud and can be set public or private. Cowork projects are "
       "separate: they sit locally on a person’s desktop and stay private to them, so the real "
       f"total across {ORG} is higher.",
     "sharedMeaning":"\"Shared\" counts projects more than one person has actually opened, which is "
       "a stricter test than the public/private setting."},
   "topProjectUsers":[{"email":m["email"],"projects":m["projectsUsed"]} for m in top(sep,"projectsUsed")],
   "spend":{"mtdActual":round(sep_usd*RNG.uniform(.01,.04),2),"projectedEom":round(sep_usd*1.08,2),
     "currency":"USD","dailyActuals":[{"date":f"{YEAR}-10-01","value":round(sep_usd/30)}],
     "byProduct":[{"product":p,"periodToDate":round(sep_usd*sh*.03,2),
       "projectedEom":round(sep_usd*sh)} for p,sh in PRODUCTS],
     "byModel":[{"model":m,"spend":round(sep_usd*sh)} for m,sh in
       [("Opus",.42),("Sonnet",.31),("Fable",.24),("Haiku",.03)]],
     "topMembers":[{"email":m["email"],"spend":m["spend"]} for m in billed[:5]],
     "concentration":{"gini":gini,"top10Share":top10,"users":len(billed),"asOf":f"{YEAR}-10-01"}},
   "cost":{"reportedMonth":f"September {YEAR}",
     "explainer":f"{ORG} pays a monthly fee for each seat. When someone goes past their plan limit, "
       "any further usage draws on a prepaid credit balance. Those are two separate charges, shown "
       "separately below.",
     "subscription":{"currency":"GBP","invoiceDate":f"16 September {YEAR}","amount":sub_amount,
       "members":SEATS_BILLED,
       "note":"The monthly bill for seats. This is the large majority of what Claude costs."},
     "metered":{"currency":"GBP","period":f"1 – 30 September {YEAR}","total":metered_total,
       "usersBilled":len(billed),"resets":f"1 October {YEAR}",
       "top":[{"email":m["email"],"name":m["name"],"title":m["title"],"amount":m["spend"]}
              for m in billed[:max(5, round(HEAD*.25))]]},
     "usage":{"currency":"USD","amount":sep_usd,
       "note":"Metered usage from 1 to 30 September, on top of the plan. Drawn from prepaid credits."},
     "credits":{"currency":"GBP","balance":round(RNG.uniform(40,180),2),"purchasedInMonth":0,
       "note":f"Prepaid balance that absorbs usage spikes. Includes credits granted by Anthropic, so "
         f"it is not all money {ORG} has spent.",
       "autoReload":"Tops up to £150 when the balance falls to £50"},
     "nextInvoice":{"currency":"GBP","date":f"16 October {YEAR}","projected":projected,
       "seats":SEATS_BILLED,"seatsAvailable":SEATS_PURCHASED-SEATS_BILLED},
     "usageByMonth":[{"month":mo,"total":v,"code":round(v*.46),"cowork":round(v*.18),
       "chat":round(v*.31),"other":round(v*.05)}
       for mo,v in [("Jul",jul_usd),("Aug",aug_usd),("Sep",sep_usd)]],
     "watch":[
       {"title":"September metered usage against August",
        "body":f"${sep_usd:,} between 1 and 30 September against ${aug_usd:,} for the whole of "
               f"August, both in US dollars from the same series. The current period resets on "
               f"1 October {YEAR}."},
       {"title":f"Two accounts are {top_two_share}% of it",
        "body":f"Of the £{metered_total:,.2f} billed, £{billed[0]['spend']:,.2f} and "
               f"£{billed[1]['spend']:,.2f} are two people. {len(billed)} of {SEATS_IN_USE} have "
               "any metered usage at all, so this is a small number of heavy workloads rather than "
               "a broad rise."}]},
   "claudeCode":{"suggestionAcceptRate":round(RNG.uniform(.58,.84),2),
     "linesOfCodeAccepted":prs * RNG.randint(180, 420),"perUserAvailable":False,
     "blockedReason":"The per-user pull request and lines-of-code charts show “Data processing in "
       f"progress”. The Claude Code GitHub app needs confirming on the {ORG} repositories before "
       "per-engineer detail appears."},
   "claudeDesign":{"dailyActive":0,"weeklyActive":0,"monthlyActive":0},
 },
 "history":[], "modelSpend":{},
}

# design usage: monthly >= weekly >= daily, by construction
dm = max(1, round(HEAD * .12)); dw = RNG.randint(0, dm); dd = RNG.randint(0, dw)
doc["snapshot"]["claudeDesign"] = {"dailyActive":dd,"weeklyActive":dw,"monthlyActive":dm}

# a publisher's output is documents first, not code
cats = [("Documents & reports",.34),("Code & scripts",.18),("Spreadsheets & tabular data",.14),
        ("Config & structured data",.11),("Slides & decks",.08),("Images",.07),
        ("Web pages & styles",.05),("Other",.03)]
ftotal = files*4 + convs*2
doc["snapshot"]["fileCategories"]["total"] = ftotal
doc["snapshot"]["fileCategories"]["categories"] = [
    {"category":c,"count":round(ftotal*s),"share":round(s,4)} for c,s in cats]

for mon,rows,days in (("August",aug,31), ("September",sep,30)):
    b=sorted([m for m in rows if m["spend"]>0.5], key=lambda m:m["spend"], reverse=True)
    wk=sum(1 for m in rows if m["daysActive"]>=8)
    cvs=sum_(rows,"chats")
    doc["history"].append({"capturedAt":f"{YEAR}-09-30","window":f"{mon} {YEAR} (rolling 30 days)",
      "dataAsOf":f"{YEAR}-09-30","actionsPerPrompt":round(RNG.uniform(5.0,8.5),2),
      "adoptionLevel":{"allMembers":SEATS_IN_USE,"monthly":sum(1 for m in rows if m["daysActive"]>0),
        "weekly":wk,"daily":sum(1 for m in rows if m["daysActive"]>=18)},
      "stickiness":{"Cowork":round(RNG.uniform(.1,.35),2),"Claude.ai":round(RNG.uniform(.1,.3),2),
        "Claude Code":round(RNG.uniform(.05,.25),2),"Office Agents":0},
      "outputs":{"prsCreated":sum_(rows,"prs"),"designsCreated":max(1,sum_(rows,"artifacts")//9),
        "fileOperations":sum_(rows,"fileEdits"),"conversations":cvs,
        "mcpWrites":int(cvs*RNG.uniform(1.4,2.2))},
      "timeSavedHours":round((sum_(rows,"prs")*145+cvs*4)/60),
      "skillsInUse":6,"connectorsInUse":len(connectors),"projectsTotal":len(projectsAll),
      "projectsShared":shared,"projectsSingleConversation":single,
      "meteredPeriod":f"1 - {days} {mon} {YEAR}",
      "meteredTotalGBP":round(sum(m["spend"] for m in b),2),"meteredUsersBilled":len(b),
      "meteredTop":[{"email":m["email"],"name":m["name"],"title":m["title"],"amount":m["spend"]}
                    for m in b[:max(5, round(HEAD*.3))]],
      "seats":{"seatsPurchased":SEATS_PURCHASED,"seatsInUse":SEATS_IN_USE-RNG.randint(0,2),
        "seatsUnused":SEATS_PURCHASED-SEATS_IN_USE}})

doc["modelSpend"]={"currency":"USD","source":"Fictional data, regenerated automatically.",
 "caveat":"These are the charges for usage above plan limits, so this shows which models the "
   "overspill ran on. Everyday work inside a seat is free and sits outside these figures.",
 "derivedNote":"Each month is summed from the daily spend-by-model series, so every figure is read "
   "directly; nothing is derived from quarter or year-to-date totals.",
 "reported":{"YTD":"1 January – 30 September"},
 "windows":[{"label":l,"sub":s,"byModel":[{"model":mm,"spend":round(v*sh)} for mm,sh in
     [("Opus",.42),("Sonnet",.31),("Fable",.24),("Haiku",.03)]]}
   for l,s,v in [("July","full month",jul_usd),("August","full month",aug_usd),
                 ("September","full month",sep_usd),
                 ("October","1 – 30, read 2 October 2026",round(sep_usd*.05))]]}

for p in people: p.pop("_intensity", None); p.pop("_codes", None)
json.dump(doc, open(_p("template.json"),"w",encoding="utf-8"), ensure_ascii=False, separators=(",",":"))
print(f"template.json: {HEAD} people, {len(coders)} of them code, {len(projectsAll)} projects, "
      f"{len(billed)} metered, subscription £{sub_amount:,.2f}")
