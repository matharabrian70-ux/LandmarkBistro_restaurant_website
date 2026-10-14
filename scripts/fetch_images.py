#!/usr/bin/env python3
"""Fetch the approved property-image set into the Pages artifact.

Images are downloaded at build time and served from the site's own assets path,
so the browser no longer hotlinks image hosts directly. Every requested asset
has multiple source candidates; the build stops rather than shipping missing files.
"""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

OUT = Path("assets/images")
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
    "Referer": "https://thelandmarksuites.com/",
    "Accept": "image/jpeg,image/png,image/webp,*/*;q=0.8",
}
BASE = "https://thelandmarksuites.com/wp-content/uploads/2025/06/"
EXPEDIA = "https://images.trvl-media.com/lodging/17000000/16230000/16228700/16228682/"
UNSPLASH = "https://images.unsplash.com/"

ASSETS = {
    "hotel-hero.jpg": [
        BASE + "slider-1.jpg",
        EXPEDIA + "5119d445.jpg?h=1600&impolicy=fcrop&quality=high&w=2200",
        BASE + "slider-3.jpg",
    ],
    "hotel-about.jpg": [
        BASE + "about-1.jpg",
        EXPEDIA + "0d4fdad4.jpg?h=1200&impolicy=fcrop&quality=high&w=1600",
        UNSPLASH + "photo-1566073771259-6a8506099945?fit=crop&fm=jpg&w=1600&q=82",
    ],
    "room-standard.jpg": [
        BASE + "h4-738x1024.jpg",
        EXPEDIA + "480dd53b.jpg?h=1000&impolicy=fcrop&quality=high&w=1200",
        UNSPLASH + "photo-1611892440504-42a792e24d32?fit=crop&fm=jpg&w=1200&q=82",
    ],
    "room-deluxe.jpg": [
        BASE + "h1-738x1024.jpg",
        EXPEDIA + "05463512.jpg?h=1000&impolicy=fcrop&quality=high&w=1200",
        UNSPLASH + "photo-1618773928121-c32242e63f39?fit=crop&fm=jpg&w=1200&q=82",
    ],
    "room-superior.jpg": [
        BASE + "g-27.jpg",
        EXPEDIA + "bdd7a130.jpg?h=1000&impolicy=fcrop&quality=high&w=1200",
        UNSPLASH + "photo-1566665797739-1674de7a421a?fit=crop&fm=jpg&w=1200&q=82",
    ],
    "room-presidential.jpg": [
        BASE + "new-738x1024.jpg",
        EXPEDIA + "05463512.jpg?h=1000&impolicy=fcrop&quality=high&w=1200",
        UNSPLASH + "photo-1582719478250-c89cae4dc85b?fit=crop&fm=jpg&w=1200&q=82",
    ],
    "hotel-bar.jpg": [
        BASE + "bar.jpg",
        UNSPLASH + "photo-1514933651103-005eec06c04b?fit=crop&fm=jpg&w=1200&q=82",
        UNSPLASH + "photo-1517248135467-4c7edcad34c4?fit=crop&fm=jpg&w=1200&q=82",
    ],
    "poolside.jpg": [
        BASE + "h7.jpg",
        UNSPLASH + "photo-1576013551627-0cc20b96c2a7?fit=crop&fm=jpg&w=1600&q=82",
        EXPEDIA + "0d4fdad4.jpg?h=1200&impolicy=fcrop&quality=high&w=1600",
    ],
    "bistro-terrace.jpg": [
        BASE + "dinep-2.jpg",
        UNSPLASH + "photo-1517248135467-4c7edcad34c4?fit=crop&fm=jpg&w=2200&q=88",
        UNSPLASH + "photo-1414235077428-338989a2e8c0?fit=crop&fm=jpg&w=2200&q=88",
    ],
    "bistro-story.jpg": [
        BASE + "dinep-1.jpg",
        BASE + "dinep-4.jpg",
        UNSPLASH + "photo-1414235077428-338989a2e8c0?fit=crop&fm=jpg&w=1600&q=82",
    ],
    "bistro-dining.jpg": [
        BASE + "dinep-4.jpg",
        BASE + "dinep-1.jpg",
        UNSPLASH + "photo-1414235077428-338989a2e8c0?fit=crop&fm=jpg&w=1600&q=82",
    ],
    "bistro-table.jpg": [
        BASE + "dinep-1.jpg",
        BASE + "dinep-4.jpg",
        UNSPLASH + "photo-1515003197210-e0cd7184f8b5?fit=crop&fm=jpg&w=1200&q=82",
    ],
    "hotel-gallery.jpg": [
        BASE + "slider-3.jpg",
        BASE + "slider-1.jpg",
        EXPEDIA + "5119d445.jpg?h=1300&impolicy=fcrop&quality=high&w=1800",
    ],
}

def looks_like_image(data: bytes) -> bool:
    return (
        data.startswith(b"\xff\xd8\xff")
        or data.startswith(b"\x89PNG\r\n\x1a\n")
        or data.startswith(b"RIFF") and data[8:12] == b"WEBP"
        or data.startswith((b"GIF87a", b"GIF89a"))
    )

errors = []
for filename, candidates in ASSETS.items():
    target = OUT / filename
    last_error = None
    for url in candidates:
        try:
            request = Request(url, headers=HEADERS)
            with urlopen(request, timeout=25) as response:
                data = response.read()
                content_type = response.headers.get("Content-Type", "")
            if len(data) < 6000 or not looks_like_image(data) or "image/" not in content_type.lower():
                raise ValueError(f"not a valid image response (type={content_type}, bytes={len(data)})")
            target.write_bytes(data)
            print(f"OK {filename}: {len(data):,} bytes from {url}")
            break
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            print(f"Retry source for {filename}: {url} -> {last_error}")
    else:
        errors.append(f"{filename}: {last_error}")

if errors:
    raise SystemExit("Could not stage required photos; refusing to deploy broken image slots:\n" + "\n".join(errors))

print(f"Prepared {len(ASSETS)} local images under {OUT}.")
