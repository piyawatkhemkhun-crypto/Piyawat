import math
import random
import re
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
    "สร้างเมือง":"City Builder"
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
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    is_new_search = (request.args.get("page") is None or page == 1)
    # เพิ่มค่าสุ่มแบบ Random Salt ลงใน Query Key เพื่อบังคับให้เซสชันเปลี่ยนค่าและสุ่มข้อมูลใหม่ทุกครั้งที่กดค้นหาคำเดิม
    random_salt = random.randint(1, 100000) if is_new_search else session.get("current_salt", 1)
    if is_new_search:
        session["current_salt"] = random_salt
    current_query_key = f"{search_name}_{max_price}_{sort_price}_{random_salt if is_new_search else session.get('current_salt', 1)}"
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
            if search_name:
                search_term = parse_free_text_search(search_name)
                if search_term:
                    fetched = fetch_raw_games_from_steam(search_term, headers, count=100)
                    all_games_map.update(fetched)
                # หากคำค้นหามีความเฉพาะเจาะจง ให้ค้นหาคำหลักเดิมแบบตรงตัวเพิ่มด้วยเพื่อความแม่นยำสูงสุด
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
                extra_pools = ["indie", "casual", "adventure", "puzzle", "strategy"]
                for pool in random.sample(extra_pools, min(2, len(extra_pools))):
                    extra_fetched = fetch_raw_games_from_steam(pool, headers, count=30)
                    all_games_map.update(extra_fetched)
            else:
                discovery_pool = [
                    "action", "rpg", "strategy", "survival", "horror", 
                    "simulation", "indie", "casual", "puzzle", "adventure",
                    "sports", "racing", "sandbox", "open world", "multiplayer",
                    "shooter", "anime", "co-op", "card game", "platformer"
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
        if search_name:
            for game in raw_games_list:
                game["ai_score"] = calculate_similarity(
                    search_name,
                    game
                )
        else:
            for game in raw_games_list:
                game["ai_score"] = 0
        # เรียงตามคะแนน AI จากมากไปน้อย
        raw_games_list.sort(
            key=lambda x: x.get("ai_score", 0),
            reverse=True
        )
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
        popular_games = [g for g in raw_games_list if g.get("rating_label") == "Popular"]
        general_games = [g for g in raw_games_list if g.get("rating_label") == "General"]
        random.shuffle(popular_games)
        random.shuffle(general_games)
        all_mixed_games = []
        mixed_seen_ids = set()
        # ======================================
        # ผสมเกม Popular 1 + General 2
        # ======================================
        while popular_games or general_games:
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
    )
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")
if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app.run(debug=True)