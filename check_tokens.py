"""Read-only connection check (posts nothing): is the page token valid, for the right page,
linked to the right Instagram account, and does it expire?"""
import os, sys, requests
G = "https://graph.facebook.com/v21.0"
def main():
    tok, page, ig = os.environ["FB_PAGE_TOKEN"], os.environ["FB_PAGE_ID"], os.environ["IG_USER_ID"]
    ok = True
    p = requests.get(f"{G}/me", params={"fields": "id,name", "access_token": tok}).json()
    print("Token belongs to:", p.get("name"), p.get("id"), "| error:" , p.get("error", {}).get("code"))
    ok &= p.get("id") == page
    i = requests.get(f"{G}/{ig}", params={"fields": "username", "access_token": tok}).json()
    print("Instagram:", i.get("username"), "| error:", i.get("error", {}).get("code"))
    ok &= i.get("username") == "color.bloop"
    d = requests.get(f"{G}/debug_token", params={"input_token": tok, "access_token": tok}).json().get("data", {})
    print("Type:", d.get("type"), "| expires_at:", d.get("expires_at"), "(0 = never) | scopes:", ",".join(d.get("scopes", [])))
    ok &= d.get("expires_at", 1) == 0
    if os.environ.get("YT_REFRESH_TOKEN"):
        t = requests.post("https://oauth2.googleapis.com/token", data={"client_id": os.environ["YT_CLIENT_ID"],
            "client_secret": os.environ["YT_CLIENT_SECRET"], "grant_type": "refresh_token",
            "refresh_token": os.environ["YT_REFRESH_TOKEN"]}).json()
        if "access_token" in t:
            ch = requests.get("https://www.googleapis.com/youtube/v3/channels", params={"part": "snippet", "mine": "true"},
                              headers={"Authorization": "Bearer " + t["access_token"]}).json().get("items", [{}])[0]
            print("YouTube:", ch.get("snippet", {}).get("title"), ch.get("snippet", {}).get("customUrl"), ch.get("id"))
            ok &= ch.get("id") == os.environ.get("YT_CHANNEL_ID")
        else:
            print("YouTube token exchange failed"); ok = False
    else:
        print("YouTube: not connected yet")
    print("RESULT:", "ALL GOOD" if ok else "PROBLEM")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("Connection check failed (response details withheld)")
        sys.exit(1)
