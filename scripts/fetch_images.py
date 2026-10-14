#!/usr/bin/env python3
"""Fetch the approved property-image set into the Pages artifact.

Images are downloaded at build time and served from the site's own assets path,
so the browser no longer hotlinks image hosts directly. Every requested asset
has multiple source candidates; the build stops rather than shipping missing files.
"""
from pathlib import Path
from urllib.request import Request, urlopen
import ssl
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
        EXPEDIA + "5119d445.jpg?h=1600&impolicy=fcrop&quality=high&w=2400",
        EXPEDIA + "5119d445.jpg?impolicy=resizecrop&ra=fill&rh=1400&rw=2200",
        BASE + "slider-1.jpg",
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
    "food-breakfast.jpg": [
        UNSPLASH + "photo-1525351484163-7529414344d8?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1533089860892-a7c6f0a88666?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1495214783159-3503fd1b572d?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-pastries.jpg": [
        UNSPLASH + "photo-1555507036-ab1f4038808a?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1509440159596-0249088772ff?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1623334044303-241021148842?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-fruit.jpg": [
        UNSPLASH + "photo-1490474418585-ba9bad8fd0ea?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1511690743698-d9d85f2fbf38?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1547592180-85f173990554?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-soup.jpg": [
        UNSPLASH + "photo-1547592180-85f173990554?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1547592166-23ac45744acd?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1476718406336-bb5a9690ee2a?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-calamari.jpg": [
        UNSPLASH + "photo-1599487488170-d11ec9c172f0?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1565680018434-b513d5e5fd47?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1565299624946-b28f40a0ae38?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-salad.jpg": [
        UNSPLASH + "photo-1512621776951-a57141f2eefd?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1540420773420-3366772f4999?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1511690743698-d9d85f2fbf38?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-chicken.jpg": [
        UNSPLASH + "photo-1532550907401-a500c9a57435?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1604908176997-125f25cc6f3d?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1603894584373-5ac82b2ae398?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-burger.jpg": [
        UNSPLASH + "photo-1568901346375-23c9450c58cd?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1550547660-d9450f859349?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1561758033-d89a9ad46330?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-fish.jpg": [
        UNSPLASH + "photo-1519708227418-c8fd9a32b7a2?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1510130387422-82bed34b37e9?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1535399831218-d5bd36d1a6b3?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-cheesecake.jpg": [
        UNSPLASH + "photo-1533134242443-d4fd215305ad?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1578985545062-69928b1d9587?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1565958011703-44f9829ba187?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-brownie.jpg": [
        UNSPLASH + "photo-1606313564200-e75d5e30476c?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1601972599720-36938d4ecd31?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1606890737304-57a1ca8a5b62?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-coffee.jpg": [
        UNSPLASH + "photo-1509042239860-f550ce710b93?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1495474472287-4d71bcdd2085?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1517701550927-30cf4ba1dba5?fit=crop&fm=jpg&w=1400&q=88",
    ],
    "food-cooler.jpg": [
        UNSPLASH + "photo-1513558161293-cdaf765edfd7?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1551024709-8f23befc6f87?fit=crop&fm=jpg&w=1400&q=88",
        UNSPLASH + "photo-1517701550927-30cf4ba1dba5?fit=crop&fm=jpg&w=1400&q=88",
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
            context = ssl._create_unverified_context() if url.startswith("https://thelandmarksuites.com/") else ssl.create_default_context()
            with urlopen(request, timeout=25, context=context) as response:
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
