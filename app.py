import math
import random
import re
import html
from urllib.parse import urlencode
import threading
import webbrowser

from deep_translator import GoogleTranslator
from flask import Flask, render_template, request, session
import requests
from rapidfuzz import fuzz

from config import Config

# สร้าง Flask Application
app = Flask(__name__)

# โหลดค่าจาก config.py
app.config.from_object(Config)

# ใช้ SECRET_KEY จาก config.py
app.secret_key = app.config["SECRET_KEY"]
GAME_CACHE = {
    "ids": [],
    "data": {},
    "query": ""
}
TOKEN_MAP = {
    # Free / Paid / Pricing
    "free game": "free to play",
    "free to play": "free to play",
    "free": "free",
    "giveaway": "free",
    "cheap": "cheap",
    "sale": "sale",
    "discount": "sale",
    "demo": "demo",
    # Specific Sub-genres & Themes (Expanded & Refined)
    "fish": "fish",
    "fishing": "fishing",
    "fish hunting": "fishing",
    "hunting": "hunting",
    "sniper": "sniper",
    "zombie shooter": "shooter zombie",
    "shooter horror": "shooter horror",
    "shooter": "shooter",
    "fps": "fps shooter",
    "tps": "third person shooter",
    "gun": "shooter",
    "action": "action",
    "sword action": "sword action",
    "stealth": "stealth",
    "ninja": "ninja",
    "samurai": "samurai",
    "space shooter": "space shooter",
    "mecha": "mecha",
    "robot": "mecha",
    "superhero": "superhero",
    "fighting": "fighting",
    "beat em up": "beat em up",
    "hack and slash": "hack and slash",
    "survival": "survival",
    "zombie": "zombie",
    "horror": "horror",
    "psychological horror": "psychological horror",
    "haunted house": "haunted house horror",
    "survival horror": "survival horror",
    "vampire": "vampire",
    "monster": "monster",
    "post-apocalyptic": "post-apocalyptic",
    "crafting": "crafting",
    "building": "building",
    "open world": "open world",
    "sandbox": "sandbox",
    "space": "space",
    "space exploration": "space exploration",
    "underwater": "underwater",
    "exploration": "exploration",
    "survival crafting": "survival crafting",
    "physics": "physics",
    "farming": "farming",
    "agriculture": "farming",
    "cooking": "cooking",
    "restaurant simulation": "restaurant simulation",
    "casual": "casual",
    "chill": "casual",
    "simulation": "simulation",
    "life simulation": "life simulation",
    "management": "management",
    "city builder": "city builder",
    "theme park": "theme park",
    "pets": "pets",
    "dating sim": "dating sim",
    "farming sim": "farming sim",
    "train simulator": "train simulator",
    "flight simulator": "flight simulator",
    "rpg": "rpg",
    "fantasy rpg": "fantasy rpg",
    "jrpg": "jrpg",
    "mmorpg": "mmorpg",
    "story rich": "story rich",
    "drama": "story rich",
    "visual novel": "visual novel",
    "card game": "card game",
    "deckbuilding": "deckbuilding",
    "detective": "detective",
    "puzzle": "puzzle",
    "magic": "magic",
    "turn-based": "turn-based",
    "strategy": "strategy",
    "grand strategy": "grand strategy",
    "4x": "4x strategy",
    "tower defense": "tower defense",
    "tactical": "tactical",
    "dungeon crawler": "dungeon crawler",
    "roguelike": "roguelike",
    "roguelite": "roguelite",
    "souls-like": "souls-like",
    "co-op": "co-op",
    "online co-op": "online co-op",
    "local co-op": "local co-op",
    "multiplayer": "multiplayer",
    "mmo": "mmo",
    "pvp": "pvp",
    "pve": "pve",
    "party": "party",
    "funny": "funny",
    "meme": "funny",
    "difficult rage": "difficult rage",
    "hardcore": "hardcore",
    "psychological": "psychological",
    "racing": "racing",
    "driving": "driving",
    "motorbike": "motorbike",
    "sports": "sports",
    "football": "football",
    "soccer": "football",
    "basketball": "basketball",
    "golf": "golf",
    "skateboarding": "skateboarding",
    "skateboard": "skateboarding",
    "tennis": "tennis",
    "boxing": "boxing",
    "wrestling": "wrestling",
    "anime": "anime",
    "pixel art": "pixel art",
    "2d": "2d",
    "3d": "3d",
    "retro": "retro",
    "nostalgia": "retro",
    "cute": "cute",
    "relaxing": "relaxing",
    "atmospheric": "atmospheric",
    "minimalist": "minimalist",
    "stylized": "stylized",
    "isometric": "isometric",
    "anime horror": "anime horror",
    # Women-friendly / cute / aesthetic themes
    "beautiful": "beautiful",
    "visually stunning": "beautiful",
    "pretty": "beautiful",
    "fashion": "fashion",
    "dress up": "dress up",
    "romance": "romance",
    "romantic": "romance",
    "princess": "princess",
    "girly": "cute",
    "cozy": "cozy",
    "wholesome": "wholesome",
}
TH_TO_EN_MAP = {
    "เกมตกปลา": "fishing",
    "เกมยิงปลา": "fish shooter",
    "เกมยิงปลา": "fish shooter",
    "ยิงปลา": "fish shooter",
    "ตกปลา": "fishing",
    "ล่าสัตว์": "hunting",
    "สไนเปอร์": "sniper",
    "ซุ่มยิง": "sniper",
    "แอคชั่น": "action",
    "บู๊": "action",
    "ยิงปืน": "shooter",
    "ยิง": "shooting",
    "ซอมบี้": "zombie",
    "สยองขวัญ": "horror",
    "ผี": "horror",
    "น่ากลัว": "horror",
    "เอาชีวิตรอด": "survival",
    "เอาตัวรอด": "survival",
    "สร้างบ้าน": "building",
    "สร้างเมือง": "city builder",
    "สร้าง": "crafting",
    "คราฟของ": "crafting",
    "โลกเปิด": "open world",
    "แมพกว้าง": "open world",
    "ทำฟาร์ม": "farming",
    "ปลูกผัก": "farming",
    "ทำอาหาร": "cooking",
    "ร้านอาหาร": "restaurant simulation",
    "จำลอง": "simulation",
    "ผ่อนคลาย": "casual",
    "สบายๆ": "casual",
    "ชิลๆ": "casual",
    "ผู้จัดการ": "management",
    "บริหาร": "management",
    "สวมบทบาท": "rpg",
    "เก็บเลเวล": "rpg",
    "เนื้อเรื่อง": "story rich",
    "ดราม่า": "story rich",
    "การ์ด": "card game",
    "จัดเด็ค": "deckbuilding",
    "ไขปริศนา": "puzzle",
    "แก้ปริศนา": "puzzle",
    "สืบสวน": "detective",
    "นักสืบ": "detective",
    "กลยุทธ์": "strategy",
    "วางแผน": "strategy",
    "โร๊คไลค์": "roguelike",
    "หัวร้อน": "difficult rage",
    "ยาก": "hardcore",
    "เล่นกับเพื่อน": "co-op",
    "หลายคน": "multiplayer",
    "ออนไลน์": "multiplayer",
    "ตลก": "funny",
    "ฮาๆ": "funny",
    "แข่งรถ": "racing",
    "ขับรถ": "driving",
    "กีฬา": "sports",
    "ฟุตบอล": "football",
    "บอล": "football",
    "บาส": "basketball",
    "อนิเมะ": "anime",
    "น่ารัก": "cute",
    "พิกเซล": "pixel art",
    "ภาพพิกเซล": "pixel art",
    "เรโทร": "retro",
    "คลาสสิก": "retro",
    "ฟรี": "free",
    "เกมฟรี": "free",
    "เสียเงิน": "paid",
    "เกมเสียเงิน": "paid",
    "ซื้อ": "paid",
    "ลดราคา": "sale",
    # หมวดหมู่สำหรับผู้หญิง / สายคิวท์ / สายสวยงาม
    "เกมสวยงาม": "beautiful",
    "สวยงาม": "beautiful",
    "ภาพสวย": "beautiful",
    "กราฟิกสวย": "beautiful",
    "เกมน่ารัก": "cute",
    "น่ารัก": "cute",
    "เกมแฟชั่น": "fashion",
    "แฟชั่น": "fashion",
    "เกมแต่งตัว": "dress up",
    "แต่งตัว": "dress up",
    "เกมโรแมนติก": "romance",
    "โรแมนติก": "romance",
    "เกมเจ้าหญิง": "princess",
    "เจ้าหญิง": "princess",
    "เกมอบอุ่น": "cozy",
    "อบอุ่น": "cozy",
    "เกมสบายใจ": "cozy",
    "เกมฮีลใจ": "cozy",
    "เกมละมุน": "wholesome",
}
PLAY_MODE_MAP = {
    "เล่นคนเดียว": "singleplayer",
    "คนเดียว": "singleplayer",
    "เล่น 1 คน": "singleplayer",
    "เล่นสองคน": "local co-op",
    "เล่น 2 คน": "local co-op",
    "2 คน": "local co-op",
    "เล่นกับเพื่อน": "co-op",
    "กับเพื่อน": "co-op",
    "หลายคน": "multiplayer",
    "ออนไลน์": "multiplayer",
    "ออนไลน์หลายคน": "multiplayer",
    "pvp": "pvp",
    "สู้กัน": "pvp",
    "pve": "pve",
    "split screen": "split screen",
    "จอเดียว": "split screen",
}
GENRE_MAP = {
    "ยิงปืน":"Shooter",
    "fps":"FPS",
    "tps":"Third-Person",
    "แอคชั่น":"Action",
    "ต่อสู้":"Action",
    "ผจญภัย":"Adventure",
    "สวมบทบาท":"RPG",
    "จำลอง":"Simulation",
    "วางแผน":"Strategy",
    "เอาชีวิตรอด":"Survival",
    "สยอง":"Horror",
    "แข่งรถ":"Racing",
    "กีฬา":"Sports",
    "ปริศนา":"Puzzle",
    "ทำฟาร์ม":"Farming",
    "สร้างบ้าน":"Building",
    "โลกเปิด":"Open World",
    "Sandbox":"Sandbox",
}
# Steam tag-based category profiles. These are used for category searches so the
# result source itself is filtered by Steam tags instead of being filled with random
# keyword matches. Steam tag IDs are public storefront tag IDs.
CATEGORY_PROFILES = {
    "beautiful": {
        "label": "✨ เกมสวยงาม",
        "tag_sets": [["5411"]],  # Beautiful
        "terms": ["เกมสวยงาม", "สวยงาม", "ภาพสวย", "กราฟิกสวย"]
    },
    "cute": {
        "label": "🎀 เกมน่ารัก",
        "tag_sets": [["4726"]],  # Cute
        "terms": ["เกมน่ารัก", "น่ารัก"]
    },
    "cozy": {
        "label": "🧸 เกมอบอุ่น / ฮีลใจ",
        "tag_sets": [["97376"], ["97376", "4726"]],  # Cozy / Cozy + Cute
        "terms": ["เกมอบอุ่น", "อบอุ่น", "เกมสบายใจ", "เกมฮีลใจ", "เกมละมุน"]
    },
    "romance": {
        "label": "💕 เกมโรแมนติก",
        "tag_sets": [["4947"], ["9551"], ["31579"]],  # Romance / Dating Sim / Otome
        "terms": ["เกมโรแมนติก", "โรแมนติก", "เกมรัก", "เกมจีบ"]
    },
    "fashion": {
        "label": "👗 เกมแฟชั่น / แต่งตัว",
        "tag_sets": [["4747", "7208"], ["4747"], ["7208"]],  # Character Customization / Female Protagonist
        "terms": ["เกมแฟชั่น", "แฟชั่น", "เกมแต่งตัว", "แต่งตัว"]
    },
    "princess": {
        "label": "👑 เกมเจ้าหญิง",
        "tag_sets": [["4726", "7208"], ["5411", "7208"], ["4726"]],
        "terms": ["เกมเจ้าหญิง", "เจ้าหญิง"]
    },
    "women": {
        "label": "💗 เกมสำหรับผู้หญิง",
        "tag_sets": [["4726"], ["97376"], ["5411"], ["4747", "7208"], ["4947"]],
        "terms": ["เกมผู้หญิง", "เกมสำหรับผู้หญิง", "ผู้หญิง", "สายผู้หญิง"]
    },
}

CATEGORY_ALIASES = {}
for _category_key, _profile in CATEGORY_PROFILES.items():
    for _term in _profile["terms"]:
        CATEGORY_ALIASES[_term] = _category_key

def detect_category_profile(user_input):
    """Return a strict Steam-tag category when the user selected a known category."""
    if not user_input:
        return None
    text = user_input.strip().lower()
    for term in sorted(CATEGORY_ALIASES, key=len, reverse=True):
        if term in text:
            return CATEGORY_ALIASES[term]
    return None

def _clean_html_text(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return html.unescape(re.sub(r"\s+", " ", value)).strip()

def fetch_games_by_steam_tags(tag_sets, headers, pages_per_set=2):
    """Fetch actual Steam storefront search results filtered by tag IDs.

    We intentionally do not use storesearch/?term= here. That endpoint searches
    text and can return unrelated games for words such as 'beautiful' or 'cute'.
    The storefront search URL's `tags=` filter is the authoritative category filter.
    """
    games = {}
    for tag_set in tag_sets:
        for page_no in range(pages_per_set):
            params = {
                "tags": ",".join(str(t) for t in tag_set),
                "category1": "998",
                "ignore_preferences": "1",
                "cc": "US",
                "l": "english",
                "start": str(page_no * 50),
                "count": "50",
            }
            url = "https://store.steampowered.com/search/?" + urlencode(params)
            try:
                response = requests.get(url, headers=headers, timeout=8)
                if response.status_code != 200:
                    continue
                body = response.text
                # Steam search result rows contain the app id in data-ds-appid.
                row_pattern = re.compile(
                    r'<a[^>]+class="search_result_row[^>]*"[^>]*data-ds-appid="([0-9]+)"[^>]*>(.*?)</a>',
                    re.I | re.S
                )
                matches = row_pattern.findall(body)
                if not matches:
                    # Attribute order can change, so use a second, more tolerant pattern.
                    row_pattern = re.compile(
                        r'<a[^>]+data-ds-appid="([0-9]+)"[^>]+class="search_result_row[^>]*"[^>]*>(.*?)</a>',
                        re.I | re.S
                    )
                    matches = row_pattern.findall(body)
                for app_id, row in matches:
                    title_match = re.search(r'<span[^>]+class="title"[^>]*>(.*?)</span>', row, re.I | re.S)
                    name = _clean_html_text(title_match.group(1)) if title_match else "Unknown Game"
                    img_match = re.search(r'<img[^>]+src="([^"]+)"', row, re.I | re.S)
                    image = html.unescape(img_match.group(1)) if img_match else ""
                    price_match = re.search(r'<div[^>]+class="discount_final_price"[^>]*>(.*?)</div>', row, re.I | re.S)
                    price_text = _clean_html_text(price_match.group(1)) if price_match else ""
                    if not price_text:
                        price_match = re.search(r'<div[^>]+class="search_price"[^>]*>(.*?)</div>', row, re.I | re.S)
                        price_text = _clean_html_text(price_match.group(1)) if price_match else ""
                    price_usd = 0.0
                    prices = re.findall(r'\$\s*([0-9]+(?:\.[0-9]{1,2})?)', price_text)
                    if prices:
                        try:
                            price_usd = float(prices[-1])
                        except ValueError:
                            price_usd = 0.0
                    meta_match = re.search(r'<span[^>]+class="search_review_summary[^>]*data-tooltip-html="([^"]*)"', row, re.I | re.S)
                    rating_label = "General"
                    metascore = 0
                    if meta_match:
                        tooltip = html.unescape(meta_match.group(1))
                        if "Overwhelmingly Positive" in tooltip or "Very Positive" in tooltip or "Positive" in tooltip:
                            rating_label = "Popular"
                    games[int(app_id)] = {
                        "id": int(app_id),
                        "name": name,
                        "price_usd": price_usd,
                        "initial_price": price_usd,
                        "discount_percent": 0,
                        "genres": "Steam tag: " + ", ".join(str(t) for t in tag_set),
                        "image": image,
                        "platforms": {"windows": True, "mac": False, "linux": False},
                        "release_date": "Unknown",
                        "metascore": metascore,
                        "rating_label": rating_label,
                        "link": f"https://store.steampowered.com/app/{app_id}/",
                        "category_match": True,
                        "matched_tags": list(tag_set),
                    }
            except requests.RequestException as exc:
                print("Steam Tag Fetch Error:", exc)
    return games

STEAM_TAGS = {
    "อนิเมะ":"Anime",
    "พิกเซล":"Pixel Graphics",
    "ซอมบี้":"Zombies",
    "สร้างบ้าน":"Building",
    "คราฟ":"Crafting",
    "เอาชีวิตรอด":"Survival",
    "โลกเปิด":"Open World",
    "ทำฟาร์ม":"Farming",
    "น่ารัก":"Cute",
    "ชิล":"Relaxing",
    "อินดี้":"Indie",
    "สยอง":"Horror",
    "ผี":"Horror",
    "เนื้อเรื่อง":"Story Rich",
    "นักสืบ":"Detective",
    "การ์ด":"Card Game",
    "หัวร้อน":"Difficult",
    "ดันเจี้ยน":"Dungeon Crawler",
    "เวทมนตร์":"Magic",
    "สร้างเมือง":"City Builder",
    "สวยงาม":"Beautiful",
    "แฟชั่น":"Fashion",
    "แต่งตัว":"Dress-Up",
    "โรแมนติก":"Romance",
    "เจ้าหญิง":"Cute",
    "อบอุ่น":"Cozy",
    "ฮีลใจ":"Relaxing"
}
def parse_free_text_search(user_input):
    if not user_input:
        return ""
    try:
        text = user_input.strip().lower()
        clean_text = text
        for price_keyword in [
            "เกมฟรี",
            "ฟรี",
            "free",
            "เกมเสียเงิน",
            "เสียเงิน",
            "paid",
            "ซื้อ"
        ]:
            clean_text = clean_text.replace(price_keyword, "")
        clean_text = clean_text.strip()
        for th_word, en_word in sorted(
            TH_TO_EN_MAP.items(),
            key=lambda x: len(x[0]),
            reverse=True
        ):
            if th_word in clean_text:
                clean_text = clean_text.replace(
                    th_word,
                    en_word
                )
        found_keywords = []
        for key in sorted(
            TOKEN_MAP.keys(),
            key=len,
            reverse=True
        ):
            if key in clean_text:
                found_keywords.append(
                    TOKEN_MAP[key]
                )
        if found_keywords:
            return " ".join(
                list(dict.fromkeys(found_keywords))
            )
        translated = GoogleTranslator(
            source="auto",
            target="en"
        ).translate(clean_text)
        return translated if translated else clean_text
    except Exception as e:
        print(
            "Translation Error:",
            e
        )
        return user_input
def calculate_similarity(query, game):
    if not query:
        return 0
    query = str(query).lower()
    score = 0
    game_name = str(game.get("name", "")).lower()
    genres = str(game.get("genres", "")).lower()
    rating = str(game.get("rating_label", "")).lower()
    score += fuzz.partial_ratio(query, game_name) * 0.45
    score += fuzz.token_set_ratio(query, genres) * 0.35
    score += fuzz.partial_ratio(query, rating) * 0.05
    for th, tag in STEAM_TAGS.items():
        if th in query:
            if tag.lower() in genres:
                score += 30
    # -----------------------------
    for th, genre in GENRE_MAP.items():
        if th in query:
            if genre.lower() in genres:
                score += 35
    for th, mode in PLAY_MODE_MAP.items():
        if th in query:
            if mode.lower() in genres:
                score += 40
    return round(score, 2)
def fetch_raw_games_from_steam(search_term, headers, count=100):
    if not search_term:
        return {}
    url = f"https://store.steampowered.com/api/storesearch/?term={search_term}&l=english&cc=US&start=0&count={count}"
    games_dict = {}
    try:
        # เพิ่ม Retry Mechanism เพื่อความเสถียรป้องกัน Timeout หรือ Network Error ชั่วคราว
        response = None
        for _ in range(3):
            try:
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    break
            except requests.exceptions.RequestException:
                pass
        if response and response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            if not isinstance(items, list):
                return games_dict
            for item in items:
                if not isinstance(item, dict):
                    continue
                game_id = item.get("id")
                if not game_id:
                    continue
                price_info = item.get("price") or {}
                try:
                    price_usd = float(price_info.get("final", 0)) / 100.0
                except (ValueError, TypeError):
                    price_usd = 0.0
                try:
                    initial_price = float(price_info.get("initial", 0)) / 100.0
                except (ValueError, TypeError):
                    initial_price = 0.0
                try:
                    discount_percent = int(price_info.get("discount_percent", 0))
                except (ValueError, TypeError):
                    discount_percent = 0
                genres_list = []
                genres_raw = item.get("genres")
                if isinstance(genres_raw, list):
                    for g in genres_raw:
                        if isinstance(g, dict) and "description" in g:
                            genres_list.append(str(g["description"]))
                        elif isinstance(g, str):
                            genres_list.append(g)
                if not genres_list:
                    categories = item.get("category")
                    if isinstance(categories, list):
                        for cat in categories:
                            if isinstance(cat, dict) and cat.get("name"):
                                genres_list.append(str(cat.get("name")))
                genres_str = ", ".join(genres_list) if genres_list else "Unspecified"

                platforms = item.get("platforms") or {
                    "windows": True,
                    "mac": False,
                    "linux": False,
                }

                release_info = item.get("release_date") or {}
                release_date = str(
                    release_info.get("date", "Unknown")
                )
                raw_score = item.get("metascore", 0)
                try:
                    metascore = int(raw_score) if raw_score else 0
                except (ValueError, TypeError):
                    metascore = 0
                rating_label = "Popular" if metascore > 70 else "General"
                games_dict[game_id] = {
                    "id": game_id,
                    "name": str(item.get("name", "Unknown Game")),
                    "price_usd": price_usd,
                    "initial_price": initial_price,
                    "discount_percent": discount_percent,
                    "genres": genres_str,
                    "image": item.get("tiny_image"),
                    "platforms": platforms,
                    "release_date": release_date,
                    "metascore": metascore,
                    "rating_label": rating_label,
                    "link": f"https://store.steampowered.com/app/{game_id}",
                }
    except Exception as e:
        print("Data Fetch Error:", e)
    return games_dict
def fetch_game_details(app_id):
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}&cc=TH&l=english"

    try:
        response = requests.get(url, timeout=5)

        if response.status_code != 200:
            return {}

        data = response.json()

        game_data = data.get(str(app_id), {})

        if not game_data.get("success"):
            return {}

        info = game_data.get("data", {})

        genres = [
            g.get("description", "")
            for g in info.get("genres", [])
        ]

        categories = [
            c.get("description", "")
            for c in info.get("categories", [])
        ]

        return {
            "genres": ", ".join(genres),
            "categories": ", ".join(categories)
        }

    except Exception as e:
        print("Detail Error:", e)
        return {}
@app.route("/")
def index():
    search_name = request.args.get("search_name", "").strip()
    max_price = request.args.get("max_price", "").strip()
    sort_price = request.args.get("sort_price", "").strip()
    category_key = request.args.get("category", "").strip().lower()
    if category_key not in CATEGORY_PROFILES:
        category_key = detect_category_profile(search_name) or ""
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    is_new_search = (request.args.get("page") is None or page == 1)
    # เพิ่มค่าสุ่มแบบ Random Salt ลงใน Query Key เพื่อบังคับให้เซสชันเปลี่ยนค่าและสุ่มข้อมูลใหม่ทุกครั้งที่กดค้นหาคำเดิม
    random_salt = random.randint(1, 100000) if is_new_search else session.get("current_salt", 1)
    if is_new_search:
        session["current_salt"] = random_salt
    current_query_key = f"{search_name}_{category_key}_{max_price}_{sort_price}_{random_salt if is_new_search else session.get('current_salt', 1)}"
    cached_query_key = session.get("query_key", "")
    if (
    is_new_search
    or current_query_key != GAME_CACHE["query"]
    or not GAME_CACHE["ids"]
):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        all_games_map = {}
        try:
            if category_key:
                profile = CATEGORY_PROFILES[category_key]
                # Strict category search: no random pools and no text-only fallback.
                all_games_map.update(
                    fetch_games_by_steam_tags(
                        profile["tag_sets"],
                        headers,
                        pages_per_set=2
                    )
                )
            elif search_name:
                search_term = parse_free_text_search(search_name)
                if search_term:
                    fetched = fetch_raw_games_from_steam(search_term, headers, count=100)
                    all_games_map.update(fetched)
                raw_lower = search_name.lower()
                for th_word, en_word in sorted(
                    TH_TO_EN_MAP.items(),
                    key=lambda x: len(x[0]),
                    reverse=True
                ):
                    if th_word in raw_lower and en_word != search_term:
                        extra_fetched = fetch_raw_games_from_steam(
                            en_word,
                            headers,
                            count=50
                        )
                        all_games_map.update(extra_fetched)
            else:
                discovery_pool = [
                    "action", "rpg", "strategy", "survival", "horror", 
                    "simulation", "indie", "casual", "puzzle", "adventure",
                    "sports", "racing", "sandbox", "open world", "multiplayer",
                    "shooter", "anime", "co-op", "card game", "platformer",
                    "cute", "fashion", "romance", "cozy", "dress up"
                ]
                selected_pools = random.sample(discovery_pool, min(5, len(discovery_pool)))
                for pool in selected_pools:
                    fetched = fetch_raw_games_from_steam(pool, headers, count=50)
                    all_games_map.update(fetched)
            if not all_games_map:
                fetched = fetch_raw_games_from_steam("game", headers, count=100)
                all_games_map.update(fetched)
        except Exception as e:
            print("Discovery/Fetch Error:", e)
        raw_games_list = list(all_games_map.values())
        if category_key:
            for game in raw_games_list:
                game["genres"] = CATEGORY_PROFILES[category_key]["label"]
            # Category results are already tag-filtered by Steam. Keep them deterministic
            # and rank by review/meta signals instead of shuffling unrelated games.
            for game in raw_games_list:
                game["ai_score"] = 100
            raw_games_list.sort(
                key=lambda x: (x.get("rating_label") == "Popular", x.get("metascore", 0), x.get("name", "")),
                reverse=True
            )
        elif search_name:
            for game in raw_games_list:
                game["ai_score"] = calculate_similarity(
                    search_name,
                    game
                )
            raw_games_list.sort(
                key=lambda x: x.get("ai_score", 0),
                reverse=True
            )
        else:
            for game in raw_games_list:
                game["ai_score"] = 0
        # กรองเงื่อนไขราคาอย่างแม่นยำ
        lower_search = search_name.lower()
        is_free_query = any(k in lower_search for k in ["ฟรี", "free", "เกมฟรี"])
        is_paid_query = any(k in lower_search for k in ["เสียเงิน", "paid", "ซื้อ"])
        if is_free_query:
            raw_games_list = [g for g in raw_games_list if g["price_usd"] == 0.0]
        elif is_paid_query:
            raw_games_list = [g for g in raw_games_list if g["price_usd"] > 0.0]
        if max_price:
            try:
                max_p = float(max_price)
                raw_games_list = [g for g in raw_games_list if g["price_usd"] <= max_p]
            except ValueError:
                pass
        if category_key:
            # Never shuffle strict category results: users should see the category they chose.
            all_mixed_games = list(raw_games_list)
            mixed_seen_ids = {g["id"] for g in all_mixed_games}
            popular_games = []
            general_games = []
        else:
            popular_games = [g for g in raw_games_list if g.get("rating_label") == "Popular"]
            general_games = [g for g in raw_games_list if g.get("rating_label") == "General"]
            random.shuffle(popular_games)
            random.shuffle(general_games)
            all_mixed_games = []
            mixed_seen_ids = set()
        # ======================================
        # ผสมเกม Popular 1 + General 2 (เฉพาะการค้นหาทั่วไป)
        # ======================================
        while (not category_key) and (popular_games or general_games):
            # เกมยอดนิยม
            if popular_games:
                g = popular_games.pop(0)
                if g["id"] not in mixed_seen_ids:
                    mixed_seen_ids.add(g["id"])
                    all_mixed_games.append(g)
            # เกมทั่วไป 2 เกม
            for _ in range(2):
                if general_games:
                    g = general_games.pop(0)
                    if g["id"] not in mixed_seen_ids:
                        mixed_seen_ids.add(g["id"])
                        all_mixed_games.append(g)
        # ======================================
        # เพิ่มเกมที่เหลือ
        # ======================================
        for g in raw_games_list:
            if g["id"] not in mixed_seen_ids:
                mixed_seen_ids.add(g["id"])
                all_mixed_games.append(g)
        # ======================================
        # Sort ราคา
        # ======================================
        if sort_price == "low_high":
            all_mixed_games.sort(
                key=lambda x: x.get("price_usd", 0)
            )

        elif sort_price == "high_low":
            all_mixed_games.sort(
                key=lambda x: x.get("price_usd", 0),
                reverse=True
            )


        # ======================================
        # Save Cache
        # ======================================
        GAME_CACHE["ids"] = [
            g["id"] for g in all_mixed_games
        ]

        GAME_CACHE["data"] = {
            str(g["id"]): g
            for g in all_mixed_games
        }

        GAME_CACHE["query"] = current_query_key
    cached_ids = GAME_CACHE["ids"]
    games_data_map = GAME_CACHE["data"]
    total_games_virtual = len(cached_ids)
    per_page = 20
    total_pages = math.ceil(total_games_virtual / per_page) if total_games_virtual > 0 else 1
    if page > total_pages:
        page = total_pages if total_pages > 0 else 1
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_page_ids = cached_ids[start_idx:end_idx]
    paginated_games = []
    for gid in current_page_ids:
        g_data = games_data_map.get(str(gid))
        if g_data:
            paginated_games.append(g_data)
    return render_template(
        "index.html",
        games=paginated_games,
        page=page,
        total_pages=total_pages,
        total_games=total_games_virtual,
        search_name=search_name,
        max_price=max_price,
        sort_price=sort_price,
        category_key=category_key,
        category_label=CATEGORY_PROFILES.get(category_key, {}).get("label", ""),
    )
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")
if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=True)