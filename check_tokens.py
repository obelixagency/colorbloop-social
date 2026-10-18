"""Read-only connection check (posts nothing): is the page token valid, for the right page,
linked to the right Instagram account, and does it expire?"""
import os, sys, requests
G = "https://graph.facebook.com/v21.0"
tok, page, ig = os.environ["FB_PAGE_TOKEN"], os.environ["FB_PAGE_ID"], os.environ["IG_USER_ID"]
ok = True
p = requests.get(f"{G}/me", params={"fields": "id,name", "access_token": tok}).json()
print("Token belongs to:", p.get("name"), p.get("id"), "| error:" , p.get("error", {}).get("message"))
ok &= p.get("id") == page
i = requests.get(f"{G}/{ig}", params={"fields": "username", "access_token": tok}).json()
print("Instagram:", i.get("username"), "| error:", i.get("error", {}).get("message"))
ok &= i.get("username") == "color.bloop"
d = requests.get(f"{G}/debug_token", params={"input_token": tok, "access_token": tok}).json().get("data", {})
print("Type:", d.get("type"), "| expires_at:", d.get("expires_at"), "(0 = never) | scopes:", ",".join(d.get("scopes", [])))
ok &= d.get("expires_at", 1) == 0
print("RESULT:", "ALL GOOD" if ok else "PROBLEM")
sys.exit(0 if ok else 1)
