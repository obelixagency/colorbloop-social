"""Platform publishing. Facebook and Instagram call the real Graph API now that those accounts are
connected. TikTok and YouTube are still stubs until those accounts are connected - same pattern:
each function checks its own secrets, nothing else in the pipeline needs to change when they're filled in.

Facebook: uses direct file upload (multipart), so no public hosting is needed.
Instagram: the Graph API only accepts a public image_url/video_url (it fetches the file itself), so
The repo itself is public with GitHub Pages on main, so every file in assets/ has a public URL
(_public_url) that the Instagram API can fetch. No secrets live in the repo (they are Actions secrets).
"""
import os, time, json, subprocess
import requests

GRAPH = "https://graph.facebook.com/v21.0"
MEDIA_REPO_OWNER = "obelixagency"
MEDIA_REPO_NAME = "colorbloop-social"


def _cover_offset_ms(path):
    """Colorbloop reels open on the "NEW BOOK!" title card with the cover, so use a frame ~1.2 s in
    (after the gentle zoom has started) as the cover/thumbnail."""
    return 1200


class NotConnected(Exception):
    pass


def _need(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing: raise NotConnected(f"missing secrets: {', '.join(missing)}")


def _fb_page():
    _need("FB_PAGE_ID", "FB_PAGE_TOKEN")
    return os.environ["FB_PAGE_ID"], os.environ["FB_PAGE_TOKEN"]


def _ig():
    _need("IG_USER_ID", "FB_PAGE_TOKEN")   # Instagram Graph API calls are authenticated with the linked Page's token
    return os.environ["IG_USER_ID"], os.environ["FB_PAGE_TOKEN"]


def _check(resp):
    try:
        data = resp.json()
    except ValueError:
        resp.raise_for_status(); raise RuntimeError(f"non-JSON response: {resp.text[:200]}")
    if resp.status_code >= 400 or "error" in data:
        raise RuntimeError(data.get("error", data))
    return data


def _public_url(path):
    return f"https://{MEDIA_REPO_OWNER}.github.io/{MEDIA_REPO_NAME}/assets/{os.path.basename(path)}"


# ---------------- Facebook (direct file upload, no public URL needed) ----------------
def publish_facebook_post(path, caption):
    page_id, token = _fb_page()
    with open(path, "rb") as f:
        r = requests.post(f"{GRAPH}/{page_id}/photos", data={"caption": caption, "access_token": token}, files={"source": f})
    return _check(r)["id"]


def _fb_rupload(endpoint, path, token, finish_params):
    """3-phase upload used by /video_reels and /video_stories: start -> binary to rupload -> finish."""
    page_id = endpoint.split("/")[0]
    start = _check(requests.post(f"{GRAPH}/{endpoint}", data={"upload_phase": "start", "access_token": token}))
    with open(path, "rb") as f:
        up = requests.post(start["upload_url"], data=f.read(),
                           headers={"Authorization": f"OAuth {token}", "offset": "0", "file_size": str(os.path.getsize(path))})
    _check(up)
    return _check(requests.post(f"{GRAPH}/{endpoint}",
                                data={"upload_phase": "finish", "video_id": start["video_id"], "access_token": token, **finish_params}))


def publish_facebook_reel(path, caption):
    """Publishes through the Reels API so the video lands in the Facebook Reels tray (far more reach than a
    plain Page video). Falls back to a standard Page video if the Reels API refuses it."""
    page_id, token = _fb_page()
    try:
        r = _fb_rupload(f"{page_id}/video_reels", path, token, {"video_state": "PUBLISHED", "description": caption})
        return r.get("post_id") or r.get("video_id") or r
    except Exception as ex:
        print(f"facebook_reel: Reels API failed ({str(ex)[:150]}), falling back to Page video")
    data = {"description": caption, "access_token": token}
    offset = _cover_offset_ms(path)
    if offset is not None: data["thumb_offset"] = offset
    with open(path, "rb") as f:
        r = requests.post(f"{GRAPH}/{page_id}/videos", data=data, files={"source": f})
    return _check(r)["id"]


def publish_facebook_story(path, caption):
    page_id, token = _fb_page()
    if str(path).endswith(".mp4"):
        # Video stories need the 3-phase upload; posting an existing video_id fails with "upload_phase is required".
        return _fb_rupload(f"{page_id}/video_stories", path, token, {})
    with open(path, "rb") as f:
        r = requests.post(f"{GRAPH}/{page_id}/photos", data={"published": "false", "access_token": token},
                          files={"source": f})
    media_id = _check(r)["id"]
    return _check(requests.post(f"{GRAPH}/{page_id}/photo_stories", data={"photo_id": media_id, "access_token": token}))


def publish_facebook_carousel(paths, caption):
    """One native multi-photo Page post (photos uploaded unpublished, then attached to a single feed post),
    instead of N separate posts that flood followers' feeds."""
    page_id, token = _fb_page()
    ids = []
    for p in paths:
        with open(p, "rb") as f:
            r = requests.post(f"{GRAPH}/{page_id}/photos", data={"published": "false", "access_token": token}, files={"source": f})
        ids.append(_check(r)["id"])
    data = {"message": caption, "access_token": token}
    for i, mid in enumerate(ids):
        data[f"attached_media[{i}]"] = json.dumps({"media_fbid": mid})
    return _check(requests.post(f"{GRAPH}/{page_id}/feed", data=data))["id"]


# ---------------- Instagram (needs a public URL - see _public_url) ----------------
def _ig_wait_ready(creation_id, token, tries=10, wait_s=3):
    for _ in range(tries):
        status = _check(requests.get(f"{GRAPH}/{creation_id}", params={"fields": "status_code", "access_token": token}))
        if status.get("status_code") == "FINISHED": return
        time.sleep(wait_s)
    raise RuntimeError(f"Instagram container {creation_id} never finished processing")


def _ig_create_and_publish(media_params):
    ig_id, token = _ig()
    r = requests.post(f"{GRAPH}/{ig_id}/media", data={**media_params, "access_token": token})
    creation_id = _check(r)["id"]
    _ig_wait_ready(creation_id, token)
    r2 = requests.post(f"{GRAPH}/{ig_id}/media_publish", data={"creation_id": creation_id, "access_token": token})
    return _check(r2)["id"]


def publish_instagram_post(path, caption):
    return _ig_create_and_publish({"image_url": _public_url(path), "caption": caption})


def publish_instagram_reel(path, caption):
    params = {"media_type": "REELS", "video_url": _public_url(path), "caption": caption}
    offset = _cover_offset_ms(path)
    if offset is not None: params["thumb_offset"] = offset
    return _ig_create_and_publish(params)


def publish_instagram_story(path, caption):
    is_video = str(path).endswith(".mp4")
    params = {"media_type": "STORIES", ("video_url" if is_video else "image_url"): _public_url(path)}
    if is_video:
        offset = _cover_offset_ms(path)
        if offset is not None: params["thumb_offset"] = offset
    return _ig_create_and_publish(params)


def publish_instagram_carousel(paths, caption):
    ig_id, token = _ig()
    item_ids = []
    for p in paths:
        r = requests.post(f"{GRAPH}/{ig_id}/media", data={"image_url": _public_url(p), "is_carousel_item": "true", "access_token": token})
        item_ids.append(_check(r)["id"])
    return _ig_create_and_publish({"media_type": "CAROUSEL", "children": ",".join(item_ids), "caption": caption})


# ---------------- TikTok ----------------
TIKTOK_API = "https://open.tiktokapis.com/v2"


def _tiktok_access_token():
    r = requests.post(f"{TIKTOK_API}/oauth/token/", data={
        "client_key": os.environ["TIKTOK_CLIENT_KEY"],
        "client_secret": os.environ["TIKTOK_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": os.environ["TIKTOK_REFRESH_TOKEN"],
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    data = r.json()
    if "access_token" not in data: raise RuntimeError(data)
    return data["access_token"]


def _publish_tiktok_real(path, caption):
    """Pushes the video to the authorized account's TikTok inbox as a draft, for the creator to review
    and post from the TikTok app. Needs TIKTOK_CLIENT_KEY/SECRET/REFRESH_TOKEN (after app review passes)
    and the stoic-media domain verified in the TikTok app (Content Posting API -> Verify domains) so
    TikTok is allowed to pull video_url."""
    token = _tiktok_access_token()
    r = requests.post(f"{TIKTOK_API}/post/publish/inbox/video/init/",
                       headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=UTF-8"},
                       json={"source_info": {"source": "PULL_FROM_URL", "video_url": _public_url(path)}})
    data = r.json()
    if data.get("error", {}).get("code") not in (None, "ok"): raise RuntimeError(data)
    return data.get("data", {}).get("publish_id")


def _notify_ntfy_tiktok(path, caption):
    """TikTok's app review hasn't passed yet, so we can't post automatically. Instead, ping a private
    ntfy.sh topic with today's video link and caption so it can be posted by hand from the TikTok app."""
    topic = os.environ.get("NTFY_TOPIC")
    if not topic: raise NotConnected("TikTok not connected yet, and NTFY_TOPIC isn't set for manual-post pings")
    url = _public_url(path)
    r = requests.post(f"https://ntfy.sh/{topic}", data=caption.encode("utf-8"), headers={
        "Title": "Colorbloop: post this on TikTok".encode("utf-8"),
        "Click": url, "Attach": url, "Tags": "tiktok,memo",
    })
    r.raise_for_status()
    return {"ntfy_topic": topic, "media_url": url}


def publish_tiktok(path, caption):
    if os.environ.get("TIKTOK_REFRESH_TOKEN"):
        return _publish_tiktok_real(path, caption)
    return _notify_ntfy_tiktok(path, caption)


# ---------------- YouTube ----------------
YT_UPLOAD_API = "https://www.googleapis.com/upload/youtube/v3/videos"


def _yt_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
    })
    data = r.json()
    if "access_token" not in data: raise RuntimeError(data)
    return data["access_token"]


def yt_title(caption, limit=90):
    """First caption line, <=90 chars (cut at a word, with an ellipsis), + " #Shorts" -> always <=100 chars,
    YouTube's hard title limit. '<' and '>' are not allowed in YouTube titles."""
    t = (caption.splitlines()[0] if caption else "").strip().replace("<", "").replace(">", "") or "Colorbloop"
    if len(t) > limit:
        cut = t[:limit - 1]
        t = (cut.rsplit(" ", 1)[0] if " " in cut[20:] else cut).rstrip(" ,.;:—–-") + "…"
    return t + " #Shorts"


def publish_youtube_short(path, caption):
    """Uploads path as a public video on the authorized channel (YT_CHANNEL_ID is the account the
    refresh token already belongs to; the API has no separate "post as channel X" switch, so this
    secret is just for our own bookkeeping/sanity-check, not sent in the request). Tagging the title
    #Shorts plus a vertical <=60s video is what gets it treated as a Short."""
    _need("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN", "YT_CHANNEL_ID")
    token = _yt_access_token()
    title = yt_title(caption)
    metadata = {
        "snippet": {"title": title, "description": caption, "categoryId": "27", "tags": ["coloring book", "kids activities", "preschool", "Colorbloop"]},
        "status": {"privacyStatus": "public", "selfDeclaredMadeForKids": False},
    }
    boundary = "colorbloop_upload_boundary"
    with open(path, "rb") as f:
        video_bytes = f.read()
    body = (
        f"--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(metadata)}\r\n"
        f"--{boundary}\r\nContent-Type: video/mp4\r\n\r\n"
    ).encode("utf-8") + video_bytes + f"\r\n--{boundary}--".encode("utf-8")
    r = requests.post(YT_UPLOAD_API, params={"uploadType": "multipart", "part": "snippet,status"},
                       headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/related; boundary={boundary}"},
                       data=body)
    return _check(r)["id"]

DISPATCH = {
    "facebook_reel": publish_facebook_reel, "facebook_post": publish_facebook_post, "facebook_story": publish_facebook_story,
    "facebook_carousel": publish_facebook_carousel,
    "instagram_reel": publish_instagram_reel, "instagram_post": publish_instagram_post, "instagram_story": publish_instagram_story,
    "instagram_carousel": publish_instagram_carousel,
    "tiktok": publish_tiktok, "youtube_short": publish_youtube_short,
}


def publish(platform, path_or_paths, caption):
    """path_or_paths: the file (or, for *_carousel platforms, the ordered list of files) render_day.py made.
    Returns (ok, detail)."""
    try:
        ref = DISPATCH[platform](path_or_paths, caption)
        return True, {"platform_ref": ref}
    except NotConnected as e:
        return False, {"error": "not_connected", "message": str(e)}
    except Exception as e:
        return False, {"error": "publish_failed", "message": str(e)}
