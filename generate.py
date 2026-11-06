#!/usr/bin/env python3
"""Roll the demo forward so it always shows the last complete months.

The data is invented, so there is nothing to protect and no secret to supply.
That is what lets this run unattended: a scheduled job can regenerate the whole
dashboard with no access to anything real.

template.json is a fully fictional dataset. This script keeps its shape and its
cast of people, moves the window to end on the last complete month, and
re-rolls the activity so the demo never looks abandoned.

    python3 generate.py            # window ends last complete month
    python3 generate.py --months 7
"""
import json, random, sys, datetime as dt, os

BASE = os.path.dirname(os.path.abspath(__file__))
def _p(*a): return os.path.join(BASE, *a)

N = 7
if "--months" in sys.argv:
    N = int(sys.argv[sys.argv.index("--months") + 1])

today = dt.date.today()
# the current month is incomplete, so the window ends on the one before it
end = (today.replace(day=1) - dt.timedelta(days=1))
window = []
y, m = end.year, end.month
for _ in range(N):
    window.append((y, m))
    m -= 1
    if m == 0:
        y, m = y - 1, 12
window.reverse()

MON = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
LONG = ["January","February","March","April","May","June","July","August",
        "September","October","November","December"]
def mdays(y, m):
    return ((dt.date(y + (m == 12), m % 12 + 1, 1)) - dt.date(y, m, 1)).days

# one seed per window, so a given month always regenerates identically
random.seed("lumen-%d-%02d-%d" % (end.year, end.month, N))

d = json.load(open(_p("template.json")))
old_keys = list(d["months"])
new_keys = ["%s %d" % (MON[m-1], y) for (y, m) in window]

def jit(v, lo=0.75, hi=1.3):
    if isinstance(v, bool) or v is None: return v
    if isinstance(v, int):   return max(0, int(round(v * random.uniform(lo, hi))))
    if isinstance(v, float): return round(v * random.uniform(lo, hi), 2)
    return v

months = {}
for i, (key, (y, m)) in enumerate(zip(new_keys, window)):
    src = d["months"][old_keys[min(i, len(old_keys) - 1)]]
    days = mdays(y, m)
    # a gentle upward drift across the window so the series tells a story
    growth = 0.72 + (i / max(N - 1, 1)) * 0.55
    members = []
    for mem in src["members"]:
        n = dict(mem)
        for f in ("chats","messages","coworkMessages","codeSessions","prs",
                  "fileEdits","artifacts","projectsCreated","coworkSessions"):
            if f in n: n[f] = max(0, int(round((n.get(f) or 0) * growth * random.uniform(.7,1.35))))
        if "spend" in n: n["spend"] = round((n.get("spend") or 0) * growth * random.uniform(.6,1.5), 2)
        if "daysActive" in n:
            n["daysActive"] = min(days, max(0, int(round((n.get("daysActive") or 0) * random.uniform(.8,1.15)))))
        members.append(n)
    months[key] = {"period": "%s 1 - %s %d" % (MON[m-1], MON[m-1], days),
                   "days": days, "members": members}
d["months"] = months

# all-time roster is the window summed, so the two always agree
roll = {}
total_days = sum(v["days"] for v in months.values())
for v in months.values():
    for mem in v["members"]:
        a = roll.setdefault(mem["email"], {k: mem.get(k) for k in
            ("name","email","dept","title","created","ranked")})
        for f in ("messages","coworkMessages","codeSessions","daysActive"):
            a[f] = (a.get(f) or 0) + (mem.get(f) or 0)
for a in roll.values():
    a["availDays"] = total_days
    a["pctDaysUsed"] = round(min(100, a["daysActive"] / max(total_days,1) * 100), 1)
    da = max(a["daysActive"], 1)
    a["chatPerDay"]   = round(a["messages"] / da, 2)
    a["coworkPerDay"] = round(a["coworkMessages"] / da, 2)
    a["codePerDay"]   = round(a["codeSessions"] / da, 2)
    a["ranked"] = a["daysActive"] >= 30
d["allTime"]["members"] = list(roll.values())
d["allTime"]["days"] = total_days
sy, sm = window[0]; ey, em = window[-1]
d["allTime"]["period"] = "%s 1 - %s %d %d" % (MON[sm-1], MON[em-1], mdays(ey,em), ey)

# everything else that carries a date
d["meta"]["generated"] = today.isoformat()
d["meta"]["demo"] = True
d["meta"]["monthlySource"] = "Fictional data, regenerated automatically. Not a real organisation."
d["meta"]["snapshotSource"] = d["meta"]["monthlySource"]
last_day = dt.date(ey, em, mdays(ey, em))
d["snapshot"]["dataAsOf"] = last_day.isoformat()
d["snapshot"]["fetchedAt"] = today.isoformat() + "T09:00:00Z"
d["snapshot"]["window"] = "%s %d (rolling 30 days)" % (LONG[em-1], ey)
for h in d.get("history", []):
    h["capturedAt"] = last_day.isoformat()
    h["dataAsOf"]   = last_day.isoformat()
    h["window"]     = d["snapshot"]["window"]
    h["meteredPeriod"] = "1 - %d %s %d" % (mdays(ey,em), LONG[em-1], ey)
if isinstance(d.get("snapshot",{}).get("cost"), dict):
    d["snapshot"]["cost"]["reportedMonth"] = "%s %d" % (LONG[em-1], ey)

json.dump(d, open(_p("data.json"), "w"), separators=(",", ":"))
print("window: %s to %s (%d months, %d days)" % (new_keys[0], new_keys[-1], N, total_days))
print("people: %d   generated: %s" % (len(roll), today))
