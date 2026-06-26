"""Run on the network that can reach api.github.com. Prints repo visibility per token."""
import json, urllib.request, urllib.error

cfg = json.load(open(".secrets/project.json"))
org = cfg["tools"]["github"]["org"].strip()
tokens = {
    "github (fine-grained, USED by kpi_17)": cfg["tools"]["github"]["githubKey"],
    "github-copilot (classic ghp_)":         cfg["tools"]["github-copilot"]["githubKey"],
}

def get(url, tok):
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {tok}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    return urllib.request.urlopen(req, timeout=30)

for label, tok in tokens.items():
    print("=" * 70)
    print(label)
    total = 0
    try:
        for page in range(1, 11):
            data = json.load(get(f"https://api.github.com/orgs/{org}/repos?per_page=100&page={page}", tok))
            if not data:
                break
            total += len(data)
            if len(data) < 100:
                break
        print(f"  /orgs/{org}/repos visible to this token = {total}")
    except urllib.error.HTTPError as e:
        print(f"  /orgs/{org}/repos -> HTTP {e.code} {e.reason}")
    except Exception as e:
        print(f"  /orgs/{org}/repos -> {type(e).__name__}: {e}")
    try:
        o = json.load(get(f"https://api.github.com/orgs/{org}", tok))
        print(f"  org true totals: public={o.get('public_repos')} "
              f"total_private={o.get('total_private_repos')}")
    except Exception as e:
        print(f"  /orgs/{org} -> {type(e).__name__}: {e}")
