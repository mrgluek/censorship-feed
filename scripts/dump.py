#!/usr/bin/env python3
"""Сохраняет issues/PR и комментарии за последние 48 ч в data/latest.json."""
import json, os, urllib.request, datetime as dt

REPOS = [
    "net4people/bbs",
    "yggdrasil-network/yggdrasil-go",
    "PurpleI2P/i2pd",
    "markqvist/Reticulum",
    "XTLS/Xray-core",
    "amnezia-vpn/amnezia-client",
    "apernet/hysteria",
]
WINDOW_H = 48
now = dt.datetime.now(dt.timezone.utc)
since = (now - dt.timedelta(hours=WINDOW_H)).strftime("%Y-%m-%dT%H:%M:%SZ")
H = {"Accept": "application/vnd.github+json", "User-Agent": "gh-digest"}
if os.environ.get("GITHUB_TOKEN"):
    H["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]

def get(url):
    out = []
    while url:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=H), timeout=30)
        out += json.load(r)
        nxt = [p for p in r.headers.get("Link", "").split(",") if 'rel="next"' in p]
        url = nxt[0].split(";")[0].strip(" <>") if nxt else None
    return out

result = {"generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"), "since": since, "repos": {}}
for repo in REPOS:
    base = f"https://api.github.com/repos/{repo}"
    entry = {}
    try:
        issues = get(f"{base}/issues?state=all&since={since}&sort=updated&direction=desc&per_page=100")
        entry["issues"] = [{
            "number": i["number"], "title": i["title"], "is_pr": "pull_request" in i,
            "state": i["state"], "created_at": i["created_at"], "updated_at": i["updated_at"],
            "user": i["user"]["login"], "url": i["html_url"], "body": (i.get("body") or "")[:4000],
        } for i in issues]
        titles = {i["number"]: i["title"] for i in issues}
        comments = get(f"{base}/issues/comments?since={since}&sort=created&direction=desc&per_page=100")
        entry["comments"] = []
        for c in comments:
            n = int(c["issue_url"].rsplit("/", 1)[1])
            entry["comments"].append({
                "id": c["id"], "issue": n, "issue_title": titles.get(n),
                "created_at": c["created_at"], "user": c["user"]["login"],
                "url": c["html_url"], "body": (c.get("body") or "")[:4000],
            })
        # дотянуть названия тем, у которых новые только комментарии
        for c in entry["comments"]:
            if c["issue_title"] is None:
                t = json.load(urllib.request.urlopen(urllib.request.Request(
                    f"{base}/issues/{c['issue']}", headers=H), timeout=30))["title"]
                titles[c["issue"]] = t
                c["issue_title"] = t
    except Exception as e:
        entry["error"] = repr(e)
    result["repos"][repo] = entry

os.makedirs("data", exist_ok=True)
with open("data/latest.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)
