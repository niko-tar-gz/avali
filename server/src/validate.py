import re
from urllib.parse import urlparse, parse_qs

YOUTUBE_HOST_RE = re.compile(r"^(www\.|m\.)?(youtube\.com|youtu\.be)$")
TIKTOK_HOST_RE = re.compile(r"^(www\.|vm\.|vt\.|m\.)?tiktok\.com$")

YOUTUBE_VIDEO_ID_RE = re.compile(r"^[a-zA-Z0-9_-]{11}$")

ALLOWED_FORMATS = ["video", "video+audio", "audio"]


def normalize_url(url: str) -> str:
    url = url.strip()
    if not re.match(r"^https?://", url):
        url = f"https://{url}"
    return url


def get_hostname(url: str) -> str | None:
    try:
        return urlparse(url).hostname
    except Exception:
        return None


def is_youtube_url(url: str) -> bool:
    host = get_hostname(url)
    return bool(host and YOUTUBE_HOST_RE.match(host))


def is_tiktok_url(url: str) -> bool:
    host = get_hostname(url)
    return bool(host and TIKTOK_HOST_RE.match(host))


def is_supported_url(url: str) -> bool:
    return is_youtube_url(url) or is_tiktok_url(url)


def extract_video_id(url: str) -> str | None:
    """youtube-only: pulls the video id out of a youtube url, used to
    sanity-check the link actually points at a single video"""
    try:
        parsed = urlparse(url)
        if parsed.hostname == "youtu.be":
            return parsed.path.lstrip("/").split("/")[0] or None
        if parsed.hostname and parsed.hostname.endswith("youtube.com"):
            qs = parse_qs(parsed.query)
            return qs.get("v", [None])[0]
        return None
    except Exception:
        return None


def is_valid_video_id(vid: str | None) -> bool:
    return vid is not None and bool(YOUTUBE_VIDEO_ID_RE.match(vid))


def validate_download_input(url: str, fmt: str) -> str | None:
    if not url or not url.strip():
        return "url is required!"
    if fmt not in ALLOWED_FORMATS:
        return f"format must be one of these: {', '.join(ALLOWED_FORMATS)}"
    url = normalize_url(url)
    if not is_supported_url(url):
        return "url must be a youtube or tiktok link!"
    if is_youtube_url(url):
        vid = extract_video_id(url)
        if not is_valid_video_id(vid):
            return "url does not contain a valid video ID!"
    return None
