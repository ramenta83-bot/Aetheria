#!/usr/bin/env python3
"""
Aetheria Web MUD Multiplayer Server (server.py)
Features:
- Account registration, login (bcrypt), and multi-character selection/creation
- Real-time WebSocket multiplayer loop
- Live MySQL/MariaDB persistence aligned with players & accounts tables
- Full Vitals HUD & Recovery countdown synchronization with frontend/client.js
- Original Lexicon: Ranks, Recovery timers, Attune / Unleash, Strike, Focus Absorption
- All 7 Classes with Berserker Lifesteal & Battle Mage / Ranger Active Pet Combat Loops
- Guild Sanctuary progression commands (train, shop, buy, use) & help command
- Real-time ASCII Animation & Ambient stage triggers
"""

import asyncio
import json
import os
import random
import time
import bcrypt
import websockets

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER", "aetheria"),
    "password": os.environ.get("DB_PASS", "Aetheriadb"),
    "database": os.environ.get("DB_NAME", "aetheria_mud"),
}


# ============================================================================
# WORLD & CLASS DEFINITIONS
# ============================================================================
GUILDS = {
    "sorcerer": {
        "name": "Sorcerer", "resource": "Arcane", "hp": 80, "res": 120,
        "start": "astral_sanctum_hall", "lifesteal": 0.0,
        "abilities": ["chaos_bolt", "astral_veil", "entropy_shackle"],
    },
    "battle_mage": {
        "name": "Battle Mage", "resource": "Elemental", "hp": 110, "res": 90,
        "start": "elemental_forge_court", "lifesteal": 0.0,
        "abilities": ["flame_arc", "summon_ember_hound", "frost_aegis"],
    },
    "berserker": {
        "name": "Berserker", "resource": "Rage", "hp": 145, "res": 100,
        "start": "bloodstone_pit", "lifesteal": 0.25,
        "abilities": ["savage_cleave", "blood_howl"],
    },
    "cleric": {
        "name": "Cleric", "resource": "Devotion", "hp": 100, "res": 110,
        "start": "sanctuary_nave", "lifesteal": 0.0,
        "abilities": ["radiant_mend", "smite_blight", "sacred_ward"],
    },
    "ranger": {
        "name": "Ranger", "resource": "Focus", "hp": 115, "res": 95,
        "start": "whispering_canopy_lodge", "lifesteal": 0.0,
        "abilities": ["piercing_shot", "call_timber_wolf", "briar_snare"],
    },
    "paladin": {
        "name": "Paladin", "resource": "Zeal", "hp": 130, "res": 85,
        "start": "bastion_chapel", "lifesteal": 0.0,
        "abilities": ["sunfire_strike", "aura_of_resolve", "lay_hands"],
    },
    "thief": {
        "name": "Thief", "resource": "Guile", "hp": 95, "res": 100,
        "start": "shadow_alley_den", "lifesteal": 0.0,
        "abilities": ["viper_ambush", "smoke_screen", "venom_coat"],
    },
}

GUILD_SANCTUARY_ROOMS = {g["start"] for g in GUILDS.values()}

SHOP_CATALOG = {
    "iron-shod staff": {"price": 40, "atk_bonus": 2, "def_bonus": 0, "heal": 0},
    "reinforced leather tunic": {"price": 45, "atk_bonus": 0, "def_bonus": 2, "heal": 0},
    "minor healing draught": {"price": 25, "atk_bonus": 0, "def_bonus": 0, "heal": 35},
}

ABILITIES = {
    "chaos_bolt": {"name": "Chaos Bolt", "guild": "sorcerer", "cost": 10, "rec": 3, "type": "damage", "power": 18, "anim": "chaos_bolt"},
    "astral_veil": {"name": "Astral Veil", "guild": "sorcerer", "cost": 12, "rec": 3, "type": "buff_evasion", "power": 15, "anim": "astral_veil"},
    "entropy_shackle": {"name": "Entropy Shackle", "guild": "sorcerer", "cost": 14, "rec": 4, "type": "debuff_recovery", "power": 3, "anim": "entropy_shackle"},
    "flame_arc": {"name": "Flame Arc", "guild": "battle_mage", "cost": 10, "rec": 3, "type": "damage", "power": 16, "anim": "flame_arc"},
    "summon_ember_hound": {"name": "Summon Ember Hound", "guild": "battle_mage", "cost": 20, "rec": 4, "type": "summon_pet", "power": 12, "pet_name": "a blazing ember hound", "anim": "summon_ember_hound"},
    "frost_aegis": {"name": "Frost Aegis", "guild": "battle_mage", "cost": 12, "rec": 3, "type": "buff_armor", "power": 14, "anim": "frost_aegis"},
    "savage_cleave": {"name": "Savage Cleave", "guild": "berserker", "cost": 15, "rec": 3, "type": "damage_lifesteal", "power": 20, "anim": "lifesteal_cleave"},
    "blood_howl": {"name": "Blood Howl", "guild": "berserker", "cost": 10, "rec": 2, "type": "buff_damage", "power": 15, "anim": "blood_howl"},
    "radiant_mend": {"name": "Radiant Mend", "guild": "cleric", "cost": 12, "rec": 3, "type": "heal", "power": 24, "anim": "radiant_mend"},
    "smite_blight": {"name": "Smite Blight", "guild": "cleric", "cost": 10, "rec": 3, "type": "damage", "power": 16, "anim": "smite_blight"},
    "sacred_ward": {"name": "Sacred Ward", "guild": "cleric", "cost": 14, "rec": 3, "type": "buff_armor", "power": 16, "anim": "sacred_ward"},
    "piercing_shot": {"name": "Piercing Shot", "guild": "ranger", "cost": 10, "rec": 3, "type": "damage", "power": 17, "anim": "piercing_shot"},
    "call_timber_wolf": {"name": "Call Timber Wolf", "guild": "ranger", "cost": 18, "rec": 4, "type": "summon_pet", "power": 11, "pet_name": "a fierce timber wolf", "anim": "call_timber_wolf"},
    "briar_snare": {"name": "Briar Snare", "guild": "ranger", "cost": 12, "rec": 3, "type": "debuff_recovery", "power": 3, "anim": "briar_snare"},
    "sunfire_strike": {"name": "Sunfire Strike", "guild": "paladin", "cost": 12, "rec": 3, "type": "damage", "power": 19, "anim": "sunfire_strike"},
    "aura_of_resolve": {"name": "Aura of Resolve", "guild": "paladin", "cost": 15, "rec": 3, "type": "buff_armor", "power": 18, "anim": "aura_of_resolve"},
    "lay_hands": {"name": "Lay Hands", "guild": "paladin", "cost": 18, "rec": 4, "type": "heal", "power": 22, "anim": "radiant_mend"},
    "viper_ambush": {"name": "Viper Ambush", "guild": "thief", "cost": 12, "rec": 3, "type": "damage", "power": 21, "anim": "viper_ambush"},
    "smoke_screen": {"name": "Smoke Screen", "guild": "thief", "cost": 10, "rec": 2, "type": "buff_evasion", "power": 20, "anim": "smoke_screen"},
    "venom_coat": {"name": "Venom Coat", "guild": "thief", "cost": 12, "rec": 2, "type": "buff_damage", "power": 14, "anim": "venom_coat"},
}

ROOMS = {
    "crossroads_plaza": {
        "title": "Oakhaven, Crossroads Plaza",
        "desc": "Wide cobblestones worn smooth by generations of travelers radiate outward from a weathered marble fountain at the heart of town. Lanterns of wrought iron cast warm pools of amber light across timber-framed storefronts and guild banners.",
        "exits": {
            "north": "bastion_chapel", "northeast": "sanctuary_nave", "east": "elemental_forge_court",
            "southeast": "shadow_alley_den", "south": "whispering_fen_verge", "southwest": "bloodstone_pit",
            "west": "whispering_canopy_lodge", "up": "astral_sanctum_hall",
        },
        "ambient": "sanctuary",
    },
    "astral_sanctum_hall": {
        "title": "The Sorcerer's Sanctum, Hall of Mirrors",
        "desc": "High vaulted ceilings of dark basalt soar overhead, inlaid with silver filigree tracing the paths of the three moons. Polished obsidian mirrors stand in a wide circle around a sunken marble dais.",
        "exits": {"east": "astral_sanctum_terrace", "down": "crossroads_plaza"},
        "ambient": "sanctuary",
    },
    "astral_sanctum_terrace": {
        "title": "The Sorcerer's Sanctum, Astral Terrace",
        "desc": "Open to the night sky, this wide flagstone balcony juts out from the tower's eastern wall, offering an unobstructed view of the heavens and the mist-shrouded marshlands below.",
        "exits": {"west": "astral_sanctum_hall"},
        "ambient": "sanctuary",
    },
    "elemental_forge_court": {
        "title": "The Elemental Conclave, Runed Courtyard",
        "desc": "Basalt pillars etched with glowing red and cerulean glyphs surround an open-air sparring yard paved with scorched granite.",
        "exits": {"west": "crossroads_plaza"},
        "ambient": "sanctuary",
    },
    "bloodstone_pit": {
        "title": "The Bloodstone Arena, Hall of Scars",
        "desc": "Rough-hewn timber beams and iron-banded stone walls enclose a sunken sand pit stained dark from countless duels.",
        "exits": {"northeast": "crossroads_plaza"},
        "ambient": "sanctuary",
    },
    "sanctuary_nave": {
        "title": "Cathedral of Dawn, Sunlit Nave",
        "desc": "Sunlight streams through towering stained-glass lancets, painting vibrant mosaics across white limestone flagstones.",
        "exits": {"southwest": "crossroads_plaza"},
        "ambient": "sanctuary",
    },
    "whispering_canopy_lodge": {
        "title": "Timberwatch, Whispering Canopy Lodge",
        "desc": "Built around the trunk of an ancient ironwood tree, this elevated timber hall smells of cedar resin, oiled leather, and damp pine needles.",
        "exits": {"east": "crossroads_plaza"},
        "ambient": "sanctuary",
    },
    "bastion_chapel": {
        "title": "The Silver Bastion, Vigil Hall",
        "desc": "Polished shields bearing sunburst crests hang along thick granite walls lit by tall beeswax candles.",
        "exits": {"south": "crossroads_plaza"},
        "ambient": "sanctuary",
    },
    "shadow_alley_den": {
        "title": "The Velvet Coin, Backroom Den",
        "desc": "Behind a false wine cask lies a low-ceilinged cellar thick with pipe smoke and whispered bargains.",
        "exits": {"northwest": "crossroads_plaza"},
        "ambient": "sanctuary",
    },
    "whispering_fen_verge": {
        "title": "The Whispering Fen, Muddy Verge",
        "desc": "Solid cobblestones end abruptly at a squishy, peat-heavy bank where firm ground gives way to stagnant black waters. Stunted willow trees droop over the murky shallows.",
        "exits": {"north": "crossroads_plaza", "south": "whispering_fen_causeway"},
        "ambient": "marsh",
    },
    "whispering_fen_causeway": {
        "title": "The Whispering Fen, Sunken Causeway",
        "desc": "Half-submerged flagstones of pale limestone form a treacherous path through the black waters of the bog. Faint marsh-gas wisps flicker beneath the surface.",
        "exits": {"north": "whispering_fen_verge"},
        "ambient": "marsh",
    },
}

ACTIVE_CREATURES = {
    "whispering_fen_verge": [
        {"uid": 101, "name": "a juvenile bog rat", "rank": 1, "hp": 35, "max_hp": 35, "atk": 6, "xp": 25, "kronars": 8, "stun_until": 0},
        {"uid": 102, "name": "a bloated marsh toad", "rank": 1, "hp": 42, "max_hp": 42, "atk": 7, "xp": 30, "kronars": 10, "stun_until": 0},
    ],
    "whispering_fen_causeway": [
        {"uid": 103, "name": "a spiny fen-crawler", "rank": 2, "hp": 60, "max_hp": 60, "atk": 11, "xp": 45, "kronars": 18, "stun_until": 0},
    ],
}

CONNECTED_SESSIONS = {}  # websocket -> {"account_id": int|None, "username": str|None}
CONNECTED_PLAYERS = {}   # websocket -> player_dict


# ============================================================================
# DATABASE PERSISTENCE & AUTH LAYER
# ============================================================================
def get_db_connection():
    if not MYSQL_AVAILABLE:
        return None
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception as e:
        print(f"[DB Connection Error] {e}")
        return None


def fetch_account_characters(account_id: int) -> list:
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            """SELECT name, guild_id, `rank`, hp, max_hp, resource, max_resource, kronars, room_id
               FROM players WHERE account_id = %s ORDER BY name ASC""",
            (account_id,),
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        for r in rows:
            g = GUILDS.get(r["guild_id"])
            r["guild_name"] = g["name"] if g else r["guild_id"].title()
        return rows
    except Exception as e:
        print(f"[DB Fetch Chars Error] {e}")
        return []


def hydrate_player_dict(ws, row: dict) -> dict:
    inv = json.loads(row["inventory_json"]) if row.get("inventory_json") else []
    guild_key = row["guild_id"] if row["guild_id"] in GUILDS else "sorcerer"
    return {
        "ws": ws,
        "account_id": row["account_id"],
        "name": row["name"],
        "guild": guild_key,
        "rank": row["rank"],
        "hp": row["hp"],
        "max_hp": row["max_hp"],
        "resource": row["resource"],
        "max_resource": row["max_resource"],
        "room": row["room_id"] if row["room_id"] in ROOMS else GUILDS[guild_key]["start"],
        "kronars": row["kronars"],
        "focus_pool": row.get("xp", 0),
        "inventory": inv,
        "attuned": None,
        "recovery_until": 0.0,
        "buff_atk": 0,
        "buff_def": 0,
        "pet": None,
    }


async def save_player(player: dict):
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            """UPDATE players
               SET `rank` = %s, xp = %s, hp = %s, max_hp = %s, resource = %s, max_resource = %s,
                   room_id = %s, kronars = %s, inventory_json = %s
               WHERE name = %s AND account_id = %s""",
            (
                player["rank"],
                player["focus_pool"],
                player["hp"],
                player["max_hp"],
                player["resource"],
                player["max_resource"],
                player["room"],
                player["kronars"],
                json.dumps(player.get("inventory", [])),
                player["name"],
                player["account_id"],
            ),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"[DB Save Error] {e}")


# ============================================================================
# MESSAGING, VITALS HUD & ROOM BROADCAST HELPERS
# ============================================================================
async def send_json(ws, payload: dict):
    await ws.send(json.dumps(payload))


async def send_text(ws, text: str, style: str = ""):
    payload = {"type": "text", "text": text}
    if style:
        payload["style"] = style
    await send_json(ws, payload)


async def send_anim(ws, effect: str, speed: int = 110):
    await send_json(ws, {"type": "anim", "effect": effect, "speed": speed})


async def send_vitals(player: dict, recovery_sec: float = None):
    payload = {
        "type": "vitals",
        "name": player["name"],
        "guild": GUILDS[player["guild"]]["name"],
        "rank": player["rank"],
        "hp": player["hp"],
        "max_hp": player["max_hp"],
        "resource": player["resource"],
        "max_resource": player["max_resource"],
        "kronars": player["kronars"],
    }
    if recovery_sec is not None:
        payload["recovery"] = recovery_sec
    await send_json(player["ws"], payload)


async def send_room(player: dict):
    room = ROOMS[player["room"]]
    others = [p["name"] for p in CONNECTED_PLAYERS.values() if p["room"] == player["room"] and p["name"] != player["name"]]
    pets = [f"{p['name']}'s {p['pet']['name']}" for p in CONNECTED_PLAYERS.values() if p["room"] == player["room"] and p["pet"]]
    creatures = [c["name"] for c in ACTIVE_CREATURES.get(player["room"], []) if c["hp"] > 0]

    entities = others + pets + creatures
    entities_line = f"You also see {', '.join(entities)}." if entities else ""
    exits_line = ", ".join(room["exits"].keys()) if room["exits"] else "none"

    payload = {
        "type": "room",
        "title": room["title"],
        "description": room["desc"],
        "entities": entities_line,
        "exits": exits_line,
        "ambient": room["ambient"],
    }
    await send_json(player["ws"], payload)


async def broadcast_room(room_id: str, text: str, exclude_ws=None, anim: str = None, style: str = ""):
    for ws, p in list(CONNECTED_PLAYERS.items()):
        if p["room"] == room_id and ws != exclude_ws:
            await send_text(ws, text, style=style)
            if anim:
                await send_anim(ws, anim)


# ============================================================================
# AUTH & CHARACTER SELECTION HANDLER
# ============================================================================
async def handle_auth_action(ws, data: dict):
    action = data.get("action")
    session = CONNECTED_SESSIONS[ws]

    if action == "register":
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        if len(username) < 3 or len(username) > 20 or not username.isalnum():
            return await send_json(ws, {"type": "auth_error", "message": "Username must be 3-20 letters/numbers."})
        if len(password) < 6:
            return await send_json(ws, {"type": "auth_error", "message": "Password must be at least 6 characters."})

        conn = get_db_connection()
        if not conn:
            return await send_json(ws, {"type": "auth_error", "message": "Database offline. Try again shortly."})

        pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO accounts (username, password_hash) VALUES (%s, %s)", (username, pw_hash))
            conn.commit()
            session["account_id"] = cur.lastrowid
            session["username"] = username
            cur.close()
            conn.close()
            await send_json(ws, {"type": "auth_ok", "username": username, "characters": []})
        except mysql.connector.IntegrityError:
            await send_json(ws, {"type": "auth_error", "message": "That account username is already taken."})
        except Exception as e:
            await send_json(ws, {"type": "auth_error", "message": f"Registration error: {e}"})

    elif action == "login":
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").encode("utf-8")

        conn = get_db_connection()
        if not conn:
            return await send_json(ws, {"type": "auth_error", "message": "Database offline. Try again shortly."})

        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT id, username, password_hash FROM accounts WHERE username = %s", (username,))
            acct = cur.fetchone()
            cur.close()
            conn.close()
        except Exception as e:
            return await send_json(ws, {"type": "auth_error", "message": f"Login error: {e}"})

        if not acct or not bcrypt.checkpw(password, acct["password_hash"].encode("utf-8")):
            return await send_json(ws, {"type": "auth_error", "message": "Invalid username or password."})

        session["account_id"] = acct["id"]
        session["username"] = acct["username"]
        chars = fetch_account_characters(acct["id"])
        await send_json(ws, {"type": "auth_ok", "username": acct["username"], "characters": chars})

    elif action == "create_character":
        account_id = session.get("account_id")
        if not account_id:
            return await send_json(ws, {"type": "auth_error", "message": "You must log in first."})

        char_name = (data.get("name") or "").strip()[:20].title()
        guild_key = (data.get("guild") or "sorcerer").strip().lower().replace(" ", "_")
        if guild_key not in GUILDS:
            guild_key = "sorcerer"

        if len(char_name) < 3 or not char_name.isalpha():
            return await send_json(ws, {"type": "char_error", "message": "Character name must be 3-20 letters only."})

        guild = GUILDS[guild_key]
        conn = get_db_connection()
        if not conn:
            return await send_json(ws, {"type": "char_error", "message": "Database offline."})

        try:
            cur = conn.cursor()
            cur.execute(
                """INSERT INTO players (account_id, name, guild_id, `rank`, xp, hp, max_hp, resource, max_resource, kronars, room_id, inventory_json)
                   VALUES (%s, %s, %s, 1, 0, %s, %s, %s, %s, 50, %s, %s)""",
                (account_id, char_name, guild_key, guild["hp"], guild["hp"], guild["res"], guild["res"], guild["start"], json.dumps([])),
            )
            conn.commit()
            cur.close()
            conn.close()
            chars = fetch_account_characters(account_id)
            await send_json(ws, {"type": "char_list", "characters": chars})
        except mysql.connector.IntegrityError:
            await send_json(ws, {"type": "char_error", "message": "That character name is already taken."})
        except Exception as e:
            await send_json(ws, {"type": "char_error", "message": f"Could not create character: {e}"})

    elif action == "select_character":
        account_id = session.get("account_id")
        char_name = (data.get("name") or "").strip()
        if not account_id or not char_name:
            return await send_json(ws, {"type": "char_error", "message": "Invalid character selection."})

        for existing_ws, existing_p in list(CONNECTED_PLAYERS.items()):
            if existing_p["name"].lower() == char_name.lower() and existing_ws != ws:
                await send_text(existing_ws, "You logged in from another window.", "error")
                await existing_ws.close()

        conn = get_db_connection()
        if not conn:
            return await send_json(ws, {"type": "char_error", "message": "Database offline."})

        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM players WHERE name = %s AND account_id = %s", (char_name, account_id))
        row = cur.fetchone()
        cur.close()
        conn.close()

        if not row:
            return await send_json(ws, {"type": "char_error", "message": "Character not found on your account."})

        player = hydrate_player_dict(ws, row)
        CONNECTED_PLAYERS[ws] = player

        await send_json(ws, {"type": "enter_world", "character": player["name"]})
        await send_text(ws, f"Welcome to Aetheria, {player['name']} ({GUILDS[player['guild']]['name']})! Type HELP for commands.", "system")
        await send_vitals(player)
        await send_room(player)
        await broadcast_room(player["room"], f"{player['name']} materializes in the realm.", exclude_ws=ws, style="system")


# ============================================================================
# BACKGROUND LOOPS: PET COMBAT, FOCUS ABSORPTION & CREATURE RESPAWN
# ============================================================================
async def handle_player_death(player: dict, killer_name: str):
    """Respawn a defeated player in their guild's starting sanctuary."""
    ws = player["ws"]
    old_room = player["room"]
    start_room = GUILDS[player["guild"]]["start"]

    await broadcast_room(
        old_room,
        f"{player['name']} has fallen to {killer_name}!",
        exclude_ws=ws,
        style="combat",
    )
    await send_text(
        ws,
        f"You have been defeated by {killer_name}. The guild restores you at your sanctuary.",
        "error",
    )

    # Restore core stats without changing rank, XP, currency, or inventory.
    player["hp"] = player["max_hp"]
    player["resource"] = player["max_resource"]
    player["room"] = start_room

    # Clear temporary combat state so death is a clean reset.
    player["attuned"] = None
    player["recovery_until"] = 0.0
    player["buff_atk"] = 0
    player["buff_def"] = 0
    player["pet"] = None

    await save_player(player)
    await send_text(ws, "You awaken safely in your guild's starting sanctuary.", "system")
    await send_vitals(player)
    await send_room(player)
    await broadcast_room(
        start_room,
        f"{player['name']} returns to the realm.",
        exclude_ws=ws,
        style="system",
    )


async def world_tick_loop():
    while True:
        await asyncio.sleep(4.0)
        now = time.time()

        # Passive regeneration and companion actions.
        for ws, p in list(CONNECTED_PLAYERS.items()):
            vitals_changed = False

            if p["hp"] > 0 and p["hp"] < p["max_hp"]:
                p["hp"] = min(p["max_hp"], p["hp"] + 2)
                vitals_changed = True
            if p["resource"] < p["max_resource"]:
                p["resource"] = min(p["max_resource"], p["resource"] + 3)
                vitals_changed = True

            if p["pet"]:
                if now >= p["pet"]["expires"]:
                    pet_name = p["pet"]["name"]
                    p["pet"] = None
                    await send_text(ws, f"Your bond fades, and {pet_name} dissolves back into the ether.", "system")
                else:
                    room_foes = [c for c in ACTIVE_CREATURES.get(p["room"], []) if c["hp"] > 0]
                    if room_foes:
                        target = room_foes[0]
                        dmg = random.randint(max(2, p["pet"]["power"] - 3), p["pet"]["power"] + 4)
                        target["hp"] -= dmg
                        await send_text(ws, f"Your {p['pet']['name']} lunges at {target['name']} for {dmg} damage!", "combat")
                        await send_anim(ws, "companion")
                        if target["hp"] <= 0:
                            await handle_creature_defeat(p, target)

            if vitals_changed:
                try:
                    await send_vitals(p)
                except Exception:
                    pass

        # Creature respawns and attacks.
        for room_id, foes in ACTIVE_CREATURES.items():
            players_here = [
                (w, pl) for w, pl in list(CONNECTED_PLAYERS.items())
                if pl["room"] == room_id and pl["hp"] > 0
            ]
            for foe in foes:
                if foe["hp"] <= 0:
                    if now >= foe.get("respawn_at", 0):
                        foe["hp"] = foe["max_hp"]
                        for w, _ in players_here:
                            await send_text(w, f"{foe['name'].capitalize()} emerges from the shadows.", "system")
                elif players_here and now >= foe["stun_until"]:
                    living_players = [(w, pl) for w, pl in players_here if pl["hp"] > 0]
                    if not living_players:
                        continue
                    target_ws, target_p = random.choice(living_players)
                    dmg = max(1, foe["atk"] - target_p["buff_def"] + random.randint(-2, 2))
                    target_p["hp"] = max(0, target_p["hp"] - dmg)
                    await send_text(
                        target_ws,
                        f"{foe['name'].capitalize()} strikes you for {dmg} damage! (HP: {target_p['hp']}/{target_p['max_hp']})",
                        "combat",
                    )
                    await send_vitals(target_p)
                    if target_p["hp"] <= 0:
                        await handle_player_death(target_p, foe["name"])
                        # The player has moved to their sanctuary; don't let
                        # another foe in this room attack them during this tick.
                        players_here = [(w, pl) for w, pl in players_here if w != target_ws]


async def handle_creature_defeat(player: dict, target: dict):
    ws = player["ws"]
    target["hp"] = 0
    target["respawn_at"] = time.time() + 25
    player["kronars"] += target["kronars"]
    player["focus_pool"] += target["xp"]
    await send_text(ws, f"{target['name'].capitalize()} collapses! You gather {target['kronars']} Kronars and absorb {target['xp']} Focus.", "system")
    await send_anim(ws, "victory_spark")

    needed = player["rank"] * 100
    if player["focus_pool"] >= needed:
        player["focus_pool"] -= needed
        player["rank"] += 1
        player["max_hp"] += 15
        player["max_resource"] += 10
        player["hp"] = player["max_hp"]
        player["resource"] = player["max_resource"]
        await send_text(ws, f"*** FOCUS ABSORPTION COMPLETE! You ascend to Rank {player['rank']}! ***", "system")

    await send_vitals(player)
    await save_player(player)


# ============================================================================
# COMMAND PARSER
# ============================================================================
DIR_ALIASES = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
    "u": "up", "d": "down",
}


async def handle_command(player: dict, raw: str):
    ws = player["ws"]
    cmd_line = raw.strip()
    if not cmd_line:
        return

    parts = cmd_line.split()
    cmd = parts[0].lower()
    args = parts[1:]
    arg_str = " ".join(args).lower()

    now = time.time()
    if cmd in ("north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down",
               "n", "s", "e", "w", "ne", "nw", "se", "sw", "u", "d", "strike", "unleash"):
        if now < player["recovery_until"]:
            rem = round(player["recovery_until"] - now, 1)
            await send_text(ws, f"...wait {rem} seconds (Recovery).", "system")
            return

    if cmd == "help":
        await send_text(
            ws,
            "=== AETHERIA COMMANDS ===\n"
            "Movement:  LOOK, NORTH (N), SOUTH (S), EAST (E), WEST (W), NE, NW, SE, SW, UP (U), DOWN (D)\n"
            "Combat:    STRIKE [target], ATTUNE <ability>, UNLEASH [target], ABILITIES\n"
            "Guild:     TRAIN (advance Rank in your guild sanctuary), SHOP, BUY <item>, USE <item>\n"
            "Social:    STATUS, INVENTORY, SAY <message>, WHO, LOGOUT",
            "system",
        )
        return

    if cmd == "logout":
        await save_player(player)
        CONNECTED_PLAYERS.pop(ws, None)
        await broadcast_room(player["room"], f"{player['name']} fades into the mist.", style="system")
        chars = fetch_account_characters(player["account_id"])
        await send_json(ws, {"type": "char_select", "characters": chars})
        return

    direction = DIR_ALIASES.get(cmd, cmd)
    if direction in ROOMS[player["room"]]["exits"]:
        old_room = player["room"]
        new_room = ROOMS[old_room]["exits"][direction]
        await broadcast_room(old_room, f"{player['name']} heads {direction}.", exclude_ws=ws, style="system")
        player["room"] = new_room
        player["recovery_until"] = now + 1.0
        await broadcast_room(new_room, f"{player['name']} arrives.", exclude_ws=ws, style="system")
        await send_room(player)
        await send_vitals(player, recovery_sec=1.0)
        await save_player(player)
        return

    if cmd == "look":
        await send_room(player)
        return

    if cmd in ("status", "score"):
        g_info = GUILDS[player["guild"]]
        pet_str = player["pet"]["name"] if player["pet"] else "None"
        await send_text(
            ws,
            f"Name: {player['name']} | Guild: {g_info['name']} | Rank: {player['rank']}\n"
            f"HP: {player['hp']}/{player['max_hp']} | {g_info['resource']}: {player['resource']}/{player['max_resource']} | Kronars: {player['kronars']}\n"
            f"Focus Pool: {player['focus_pool']}/{player['rank'] * 100} | Active Companion: {pet_str}",
            "system",
        )
        return

    if cmd in ("inventory", "inv", "i"):
        items = ", ".join(player["inventory"]) if player["inventory"] else "Nothing"
        await send_text(ws, f"Inventory: {items}", "system")
        return

    if cmd == "abilities":
        known = [ABILITIES[a]["name"] for a in GUILDS[player["guild"]]["abilities"]]
        await send_text(ws, f"Known Rank 1 Abilities: {', '.join(known)}", "system")
        return

    if cmd == "say":
        speech = " ".join(args)
        await send_text(ws, f'You say, "{speech}"')
        await broadcast_room(player["room"], f'{player["name"]} says, "{speech}"', exclude_ws=ws)
        return

    if cmd == "who":
        roster = [f"{p['name']} (Rank {p['rank']} {GUILDS[p['guild']]['name']})" for p in CONNECTED_PLAYERS.values()]
        await send_text(ws, "Adventurers Online:\n  " + "\n  ".join(roster), "system")
        return

    if cmd == "train":
        if player["room"] not in GUILD_SANCTUARY_ROOMS:
            await send_text(ws, "You must visit a Guild Sanctuary to train your Rank.", "system")
            return
        cost = player["rank"] * 100
        if player["kronars"] < cost:
            await send_text(ws, f"Training to Rank {player['rank'] + 1} requires {cost} Kronars.", "system")
            return
        player["kronars"] -= cost
        player["rank"] += 1
        player["max_hp"] += 15
        player["hp"] = player["max_hp"]
        player["max_resource"] += 10
        player["resource"] = player["max_resource"]
        await save_player(player)
        await send_vitals(player)
        await send_text(ws, f"You complete rigorous guild drills and advance to Rank {player['rank']}!", "system")
        return

    if cmd == "shop":
        await send_text(
            ws,
            "Guild Quartermaster Stock:\n"
            "  1. Iron-Shod Staff (40 Kronars)\n"
            "  2. Reinforced Leather Tunic (45 Kronars)\n"
            "  3. Minor Healing Draught (25 Kronars)\n"
            "Type 'buy <item name>' to purchase.",
            "system",
        )
        return

    if cmd == "buy":
        if arg_str not in SHOP_CATALOG:
            await send_text(ws, "That item is not sold here. Type 'shop' to view stock.", "system")
            return
        item_info = SHOP_CATALOG[arg_str]
        price = item_info["price"]
        if player["kronars"] < price:
            await send_text(ws, f"You need {price} Kronars to buy {arg_str}.", "system")
            return
        player["kronars"] -= price
        player["inventory"].append(arg_str)
        player["buff_atk"] += item_info["atk_bonus"]
        player["buff_def"] += item_info["def_bonus"]
        await save_player(player)
        await send_vitals(player)
        await send_text(ws, f"You purchase {arg_str} for {price} Kronars.", "system")
        return

    if cmd == "use":
        if arg_str not in player["inventory"]:
            await send_text(ws, "You do not carry that item.", "system")
            return
        if arg_str == "minor healing draught":
            player["inventory"].remove(arg_str)
            player["hp"] = min(player["max_hp"], player["hp"] + 35)
            await send_vitals(player)
            await save_player(player)
            await send_text(ws, f"You drink the minor healing draught and recover 35 HP! ({player['hp']}/{player['max_hp']})", "system")
        else:
            await send_text(ws, f"Your {arg_str} is already equipped passively.", "system")
        return

    if cmd == "strike":
        foes = [c for c in ACTIVE_CREATURES.get(player["room"], []) if c["hp"] > 0]
        if not foes:
            await send_text(ws, "There is nothing here to strike.", "system")
            return
        target = next((f for f in foes if arg_str in f["name"].lower()), foes[0])
        dmg = random.randint(8, 15) + player["buff_atk"]
        target["hp"] -= dmg
        player["recovery_until"] = now + 3.0

        lifesteal_pct = GUILDS[player["guild"]]["lifesteal"]
        if lifesteal_pct > 0:
            healed = max(1, int(dmg * lifesteal_pct))
            player["hp"] = min(player["max_hp"], player["hp"] + healed)
            await send_text(ws, f"You strike {target['name']} for {dmg} damage and siphon {healed} HP!", "combat")
            await send_anim(ws, "lifesteal_cleave")
        else:
            await send_text(ws, f"You strike {target['name']} for {dmg} physical damage!", "combat")
            await send_anim(ws, "melee_slash")

        await send_vitals(player, recovery_sec=3.0)
        if target["hp"] <= 0:
            await handle_creature_defeat(player, target)
        return

    if cmd == "attune":
        guild_abs = GUILDS[player["guild"]]["abilities"]
        match = next((a for a in guild_abs if arg_str and (arg_str in a.replace("_", " ") or arg_str in ABILITIES[a]["name"].lower())), None)
        if not match:
            await send_text(ws, "You do not know an ability by that name. Type ABILITIES to view your list.", "system")
            return
        player["attuned"] = match
        await send_text(ws, f"You begin attuning your energy to {ABILITIES[match]['name']}...", "system")
        return

    if cmd == "unleash":
        if not player["attuned"]:
            await send_text(ws, "You have not attuned an ability yet. Use ATTUNE <ability> first.", "system")
            return
        ab = ABILITIES[player["attuned"]]
        player["attuned"] = None

        if player["resource"] < ab["cost"]:
            await send_text(ws, f"Insufficient {GUILDS[player['guild']]['resource']} to unleash {ab['name']}.", "system")
            return

        player["resource"] -= ab["cost"]
        player["recovery_until"] = now + ab["rec"]
        await send_anim(ws, ab["anim"])
        await send_vitals(player, recovery_sec=ab["rec"])
        await broadcast_room(player["room"], f"{player['name']} unleashes {ab['name']}!", exclude_ws=ws, anim=ab["anim"], style="combat")

        etype = ab["type"]
        if etype in ("damage", "damage_lifesteal"):
            foes = [c for c in ACTIVE_CREATURES.get(player["room"], []) if c["hp"] > 0]
            if not foes:
                await send_text(ws, f"You unleash {ab['name']} into the empty air.", "system")
                return
            target = next((f for f in foes if arg_str in f["name"].lower()), foes[0])
            dmg = ab["power"] + (player["rank"] * 2) + player["buff_atk"]
            target["hp"] -= dmg
            msg = f"You unleash {ab['name']} at {target['name']} for {dmg} damage!"
            if etype == "damage_lifesteal":
                healed = max(1, int(dmg * 0.25))
                player["hp"] = min(player["max_hp"], player["hp"] + healed)
                msg += f" (Siphoned +{healed} HP)"
            await send_text(ws, msg, "combat")
            await send_vitals(player)
            if target["hp"] <= 0:
                await handle_creature_defeat(player, target)

        elif etype == "heal":
            healed = ab["power"] + (player["rank"] * 3)
            player["hp"] = min(player["max_hp"], player["hp"] + healed)
            await send_text(ws, f"You channel {ab['name']} and restore {healed} HP! ({player['hp']}/{player['max_hp']})", "system")
            await send_vitals(player)

        elif etype == "summon_pet":
            player["pet"] = {
                "name": ab["pet_name"],
                "power": ab["power"] + player["rank"],
                "expires": now + 60.0,
            }
            await send_text(ws, f"You summon {ab['pet_name']} to fight by your side!", "system")

        elif etype in ("buff_armor", "buff_evasion"):
            player["buff_def"] += max(1, ab["power"] // 5)
            await send_text(ws, f"{ab['name']} surrounds you, bolstering your defenses!", "system")

        elif etype == "buff_damage":
            player["buff_atk"] += max(1, ab["power"] // 4)
            await send_text(ws, f"{ab['name']} empowers your strikes with lethal force!", "system")

        elif etype == "debuff_recovery":
            foes = [c for c in ACTIVE_CREATURES.get(player["room"], []) if c["hp"] > 0]
            if not foes:
                await send_text(ws, f"You cast {ab['name']}, but there is no target to ensnare.", "system")
                return
            target = next((f for f in foes if arg_str in f["name"].lower()), foes[0])
            target["stun_until"] = now + (ab["power"] * 2.0)
            await send_text(ws, f"{ab['name']} binds {target['name']}, delaying its recovery!", "combat")

        await save_player(player)
        return

    await send_text(ws, "Unknown command. Type HELP for a list of commands.", "system")


# ============================================================================
# WEBSOCKET CONNECTION HANDLER & ENTRY POINT
# ============================================================================
async def client_handler(ws):
    CONNECTED_SESSIONS[ws] = {"account_id": None, "username": None}
    try:
        async for raw_msg in ws:
            try:
                data = json.loads(raw_msg)
            except json.JSONDecodeError:
                continue

            if "action" in data:
                await handle_auth_action(ws, data)
            elif "command" in data:
                player = CONNECTED_PLAYERS.get(ws)
                if not player:
                    await send_json(ws, {"type": "auth_error", "message": "Please log in and select a character first."})
                else:
                    await handle_command(player, data["command"])

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        CONNECTED_SESSIONS.pop(ws, None)
        if ws in CONNECTED_PLAYERS:
            departed = CONNECTED_PLAYERS.pop(ws)
            await save_player(departed)
            await broadcast_room(departed["room"], f"{departed['name']} fades into the mist.", style="system")


async def main():
    asyncio.create_task(world_tick_loop())
    print("Aetheria MUD Server running on ws://0.0.0.0:8765 ...")
    async with websockets.serve(client_handler, "0.0.0.0", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
