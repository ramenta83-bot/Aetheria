#!/usr/bin/env python3
"""
Aetheria Web MUD Multiplayer Server (server.py)
Features:
- Real-time WebSocket multiplayer loop
- Live MySQL persistence aligned with aetheria_mud.players (auto-falls back to in-memory mode if MySQL is offline)
- Full Vitals HUD & Recovery countdown synchronization with frontend/client.js
- Original Lexicon: Ranks, Recovery timers, Attune / Unleash, Strike, Focus Absorption
- All 7 Classes with Berserker Lifesteal & Battle Mage / Ranger Active Pet Combat Loops
- Guild Sanctuary progression commands (train, shop, buy) & help command
- Real-time ASCII Animation & Ambient stage triggers
"""

import asyncio
import json
import os
import random
import time
import websockets

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

DB_CONFIG = {
    "host": os.environ.get("MUD_DB_HOST", "localhost"),
    "user": os.environ.get("MUD_DB_USER", "root"),
    "password": os.environ.get("MUD_DB_PASS", ""),
    "database": os.environ.get("MUD_DB_NAME", "aetheria_mud"),
}

# ============================================================================
# WORLD & CLASS DEFINITIONS (Mirrors seed_world.sql for zero-config startup)
# ============================================================================
GUILDS = {
    "sorcerer": {"name": "Sorcerer", "resource": "Arcane", "hp": 80, "res": 120, "start": "astral_sanctum_hall", "lifesteal": 0.0,
                 "abilities": ["chaos_bolt", "astral_veil", "entropy_shackle"]},
    "battle_mage": {"name": "Battle Mage", "resource": "Elemental", "hp": 110, "res": 90, "start": "elemental_forge_court", "lifesteal": 0.0,
                    "abilities": ["flame_arc", "summon_ember_hound", "frost_aegis"]},
    "berserker": {"name": "Berserker", "resource": "Rage", "hp": 145, "res": 100, "start": "bloodstone_pit", "lifesteal": 0.25,
                  "abilities": ["savage_cleave", "blood_howl"]},
    "cleric": {"name": "Cleric", "resource": "Devotion", "hp": 100, "res": 110, "start": "sanctuary_nave", "lifesteal": 0.0,
               "abilities": ["radiant_mend", "smite_blight", "sacred_ward"]},
    "ranger": {"name": "Ranger", "resource": "Focus", "hp": 115, "res": 95, "start": "whispering_canopy_lodge", "lifesteal": 0.0,
               "abilities": ["piercing_shot", "call_timber_wolf", "briar_snare"]},
    "paladin": {"name": "Paladin", "resource": "Zeal", "hp": 130, "res": 85, "start": "bastion_chapel", "lifesteal": 0.0,
                "abilities": ["sunfire_strike", "aura_of_resolve", "lay_hands"]},
    "thief": {"name": "Thief", "resource": "Guile", "hp": 95, "res": 100, "start": "shadow_alley_den", "lifesteal": 0.0,
              "abilities": ["viper_ambush", "smoke_screen", "venom_coat"]},
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
        "exits": {"north": "bastion_chapel", "northeast": "sanctuary_nave", "east": "elemental_forge_court",
                  "southeast": "shadow_alley_den", "south": "whispering_fen_verge", "southwest": "bloodstone_pit",
                  "west": "whispering_canopy_lodge", "up": "astral_sanctum_hall"},
        "ambient": "town_lanterns",
    },
    "astral_sanctum_hall": {
        "title": "The Sorcerer's Sanctum, Hall of Mirrors",
        "desc": "High vaulted ceilings of dark basalt soar overhead, inlaid with silver filigree tracing the paths of the three moons. Polished obsidian mirrors stand in a wide circle around a sunken marble dais.",
        "exits": {"east": "astral_sanctum_terrace", "down": "crossroads_plaza"},
        "ambient": "astral_twinkle",
    },
    "astral_sanctum_terrace": {
        "title": "The Sorcerer's Sanctum, Astral Terrace",
        "desc": "Open to the night sky, this wide flagstone balcony juts out from the tower's eastern wall, offering an unobstructed view of the heavens and the mist-shrouded marshlands below.",
        "exits": {"west": "astral_sanctum_hall"},
        "ambient": "astral_twinkle",
    },
    "elemental_forge_court": {
        "title": "The Elemental Conclave, Runed Courtyard",
        "desc": "Basalt pillars etched with glowing red and cerulean glyphs surround an open-air sparring yard paved with scorched granite.",
        "exits": {"west": "crossroads_plaza"},
        "ambient": "forge_sparks",
    },
    "bloodstone_pit": {
        "title": "The Bloodstone Arena, Hall of Scars",
        "desc": "Rough-hewn timber beams and iron-banded stone walls enclose a sunken sand pit stained dark from countless duels.",
        "exits": {"northeast": "crossroads_plaza"},
        "ambient": "arena_dust",
    },
    "sanctuary_nave": {
        "title": "Cathedral of Dawn, Sunlit Nave",
        "desc": "Sunlight streams through towering stained-glass lancets, painting vibrant mosaics across white limestone flagstones.",
        "exits": {"southwest": "crossroads_plaza"},
        "ambient": "radiant_motes",
    },
    "whispering_canopy_lodge": {
        "title": "Timberwatch, Whispering Canopy Lodge",
        "desc": "Built around the trunk of an ancient ironwood tree, this elevated timber hall smells of cedar resin, oiled leather, and damp pine needles.",
        "exits": {"east": "crossroads_plaza"},
        "ambient": "forest_breeze",
    },
    "bastion_chapel": {
        "title": "The Silver Bastion, Vigil Hall",
        "desc": "Polished shields bearing sunburst crests hang along thick granite walls lit by tall beeswax candles.",
        "exits": {"south": "crossroads_plaza"},
        "ambient": "radiant_motes",
    },
    "shadow_alley_den": {
        "title": "The Velvet Coin, Backroom Den",
        "desc": "Behind a false wine cask lies a low-ceilinged cellar thick with pipe smoke and whispered bargains.",
        "exits": {"northwest": "crossroads_plaza"},
        "ambient": "candle_flicker",
    },
    "whispering_fen_verge": {
        "title": "The Whispering Fen, Muddy Verge",
        "desc": "Solid cobblestones end abruptly at a squishy, peat-heavy bank where firm ground gives way to stagnant black waters. Stunted willow trees droop over the murky shallows.",
        "exits": {"north": "crossroads_plaza", "south": "whispering_fen_causeway"},
        "ambient": "swamp_mist",
    },
    "whispering_fen_causeway": {
        "title": "The Whispering Fen, Sunken Causeway",
        "desc": "Half-submerged flagstones of pale limestone form a treacherous path through the black waters of the bog. Faint marsh-gas wisps flicker beneath the surface.",
        "exits": {"north": "whispering_fen_verge"},
        "ambient": "swamp_mist",
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

CONNECTED_PLAYERS = {}  # websocket -> player_dict


# ============================================================================
# DATABASE PERSISTENCE LAYER (Aligned with aetheria_mud.players)
# ============================================================================
def get_db_connection():
    if not MYSQL_AVAILABLE:
        return None
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception:
        return None


def load_or_create_character(ws, name: str, guild_key: str) -> dict:
    guild = GUILDS.get(guild_key, GUILDS["sorcerer"])
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM players WHERE name = %s", (name,))
            row = cur.fetchone()
            if row:
                cur.close()
                conn.close()
                inv = json.loads(row["inventory_json"]) if row.get("inventory_json") else []
                return {
                    "ws": ws,
                    "name": row["name"],
                    "guild": row["guild_id"],
                    "rank": row["rank"],
                    "hp": row["hp"],
                    "max_hp": row["max_hp"],
                    "resource": row["resource"],
                    "max_resource": row["max_resource"],
                    "room": row["room_id"],
                    "kronars": row["kronars"],
                    "focus_pool": row.get("xp", 0),
                    "inventory": inv,
                    "attuned": None,
                    "recovery_until": 0.0,
                    "buff_atk": 0,
                    "buff_def": 0,
                    "pet": None,
                }
            cur.execute(
                """INSERT INTO players (name, guild_id, rank, xp, hp, max_hp, resource, max_resource, kronars, room_id, inventory_json)
                   VALUES (%s, %s, 1, 0, %s, %s, %s, %s, 50, %s, %s)""",
                (name, guild_key, guild["hp"], guild["hp"], guild["res"], guild["res"], guild["start"], json.dumps([])),
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            print(f"[DB Warning] Falling back to memory mode: {e}")

    return {
        "ws": ws,
        "name": name,
        "guild": guild_key,
        "rank": 1,
        "hp": guild["hp"],
        "max_hp": guild["hp"],
        "resource": guild["res"],
        "max_resource": guild["res"],
        "room": guild["start"],
        "kronars": 50,
        "focus_pool": 0,
        "inventory": [],
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
               SET rank = %s, xp = %s, hp = %s, max_hp = %s, resource = %s, max_resource = %s,
                   room_id = %s, kronars = %s, inventory_json = %s
               WHERE name = %s""",
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
async def send_text(ws, text: str, style: str = ""):
    payload = {"type": "text", "text": text}
    if style:
        payload["style"] = style
    await ws.send(json.dumps(payload))


async def send_anim(ws, effect: str, speed: int = 110):
    await ws.send(json.dumps({"type": "anim", "effect": effect, "speed": speed}))


async def send_vitals(player: dict, recovery_sec: float = None):
    payload = {
        "type": "vitals",
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
    await player["ws"].send(json.dumps(payload))


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
    await player["ws"].send(json.dumps(payload))


async def broadcast_room(room_id: str, text: str, exclude_ws=None, anim: str = None, style: str = ""):
    for ws, p in list(CONNECTED_PLAYERS.items()):
        if p["room"] == room_id and ws != exclude_ws:
            await send_text(ws, text, style=style)
            if anim:
                await send_anim(ws, anim)


# ============================================================================
# BACKGROUND LOOPS: PET COMBAT, FOCUS ABSORPTION & CREATURE RESPAWN
# ============================================================================
async def world_tick_loop():
    while True:
        await asyncio.sleep(4.0)
        now = time.time()

        for ws, p in list(CONNECTED_PLAYERS.items()):
            vitals_changed = False

            # Passive regeneration
            if p["hp"] < p["max_hp"]:
                p["hp"] = min(p["max_hp"], p["hp"] + 2)
                vitals_changed = True
            if p["resource"] < p["max_resource"]:
                p["resource"] = min(p["max_resource"], p["resource"] + 3)
                vitals_changed = True

            # Active Pet Combat Loop (Battle Mage & Ranger)
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
                        await send_anim(ws, "pet_bite")
                        if target["hp"] <= 0:
                            await handle_creature_defeat(p, target)

            if vitals_changed:
                try:
                    await send_vitals(p)
                except Exception:
                    pass

        # Creature Counterattack & Respawn Loop
        for room_id, foes in ACTIVE_CREATURES.items():
            players_here = [(w, pl) for w, pl in CONNECTED_PLAYERS.items() if pl["room"] == room_id]
            for foe in foes:
                if foe["hp"] <= 0:
                    if now >= foe.get("respawn_at", 0):
                        foe["hp"] = foe["max_hp"]
                        for w, _ in players_here:
                            await send_text(w, f"{foe['name'].capitalize()} emerges from the shadows.", "system")
                elif players_here and now >= foe["stun_until"]:
                    target_ws, target_p = random.choice(players_here)
                    dmg = max(1, foe["atk"] - target_p["buff_def"] + random.randint(-2, 2))
                    target_p["hp"] = max(1, target_p["hp"] - dmg)
                    await send_text(target_ws, f"{foe['name'].capitalize()} strikes you for {dmg} damage! (HP: {target_p['hp']}/{target_p['max_hp']})", "combat")
                    await send_vitals(target_p)


async def handle_creature_defeat(player: dict, target: dict):
    ws = player["ws"]
    target["hp"] = 0
    target["respawn_at"] = time.time() + 25
    player["kronars"] += target["kronars"]
    player["focus_pool"] += target["xp"]
    await send_text(ws, f"{target['name'].capitalize()} collapses! You gather {target['kronars']} Kronars and absorb {target['xp']} Focus.", "echo")
    await send_anim(ws, "victory_spark")

    needed = player["rank"] * 100
    if player["focus_pool"] >= needed:
        player["focus_pool"] -= needed
        player["rank"] += 1
        player["max_hp"] += 15
        player["max_resource"] += 10
        player["hp"] = player["max_hp"]
        player["resource"] = player["max_resource"]
        await send_text(ws, f"*** FOCUS ABSORPTION COMPLETE! You ascend to Rank {player['rank']}! ***", "echo")

    await send_vitals(player)
    await save_player(player)


# ============================================================================
# COMMAND PARSER
# ============================================================================
DIR_ALIASES = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
    "u": "up", "d": "down"
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

    # Check Recovery Timer (blocks combat & movement)
    now = time.time()
    if cmd in ("north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down",
               "n", "s", "e", "w", "ne", "nw", "se", "sw", "u", "d", "strike", "unleash"):
        if now < player["recovery_until"]:
            rem = round(player["recovery_until"] - now, 1)
            await send_text(ws, f"...wait {rem} seconds (Recovery).", "system")
            return

    # Help Command
    if cmd == "help":
        await send_text(
            ws,
            "=== AETHERIA COMMANDS ===
"
            "Movement: LOOK, NORTH (N), SOUTH (S), EAST (E), WEST (W), NE, NW, SE, SW, UP (U), DOWN (D)
"
            "Combat:   STRIKE [target], ATTUNE <ability>, UNLEASH [target], ABILITIES
"
            "Guild:    TRAIN (advance Rank in your guild sanctuary), SHOP, BUY <item>, USE <item>
"
            "Social:   STATUS, INVENTORY, SAY <message>, WHO",
            "system",
        )
        return

    # Movement
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
            f"Name: {player['name']} | Guild: {g_info['name']} | Rank: {player['rank']}
"
            f"HP: {player['hp']}/{player['max_hp']} | {g_info['resource']}: {player['resource']}/{player['max_resource']} | Kronars: {player['kronars']}
"
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
        await send_text(ws, "Adventurers Online:
  " + "
  ".join(roster), "system")
        return

    # Guild Sanctuary Progression Commands (Handbook Section 3)
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
        await send_text(ws, f"You complete rigorous guild drills and advance to Rank {player['rank']}!", "echo")
        return

    if cmd == "shop":
        await send_text(
            ws,
            "Guild Quartermaster Stock:
"
            "  1. Iron-Shod Staff (40 Kronars)
"
            "  2. Reinforced Leather Tunic (45 Kronars)
"
            "  3. Minor Healing Draught (25 Kronars)
"
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
        await send_text(ws, f"You purchase {arg_str} for {price} Kronars.", "echo")
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
            await send_text(ws, f"You drink the minor healing draught and recover 35 HP! ({player['hp']}/{player['max_hp']})", "echo")
        else:
            await send_text(ws, f"Your {arg_str} is already equipped passively.", "system")
        return

    # Melee Attack: STRIKE <target>
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

    # Attune Ability: ATTUNE <ability name>
    if cmd == "attune":
        guild_abs = GUILDS[player["guild"]]["abilities"]
        match = next((a for a in guild_abs if arg_str and (arg_str in a.replace("_", " ") or arg_str in ABILITIES[a]["name"].lower())), None)
        if not match:
            await send_text(ws, "You do not know an ability by that name. Type ABILITIES to view your list.", "system")
            return
        player["attuned"] = match
        await send_text(ws, f"You begin attuning your energy to {ABILITIES[match]['name']}...", "system")
        return

    # Unleash Ability: UNLEASH [target]
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
            dmg = ab["power"] + random.randint(-3, 5) + player["buff_atk"]
            target["hp"] -= dmg
            if etype == "damage_lifesteal":
                healed = max(2, int(dmg * 0.25))
                player["hp"] = min(player["max_hp"], player["hp"] + healed)
                await send_text(ws, f"Your {ab['name']} tears into {target['name']} for {dmg} damage, restoring {healed} HP!", "combat")
                await send_vitals(player)
            else:
                await send_text(ws, f"Your {ab['name']} blasts {target['name']} for {dmg} damage!", "combat")
            if target["hp"] <= 0:
                await handle_creature_defeat(player, target)

        elif etype == "heal":
            healed = ab["power"] + random.randint(0, 6)
            player["hp"] = min(player["max_hp"], player["hp"] + healed)
            await send_vitals(player)
            await send_text(ws, f"{ab['name']} washes over you, restoring {healed} HP! ({player['hp']}/{player['max_hp']})", "echo")

        elif etype == "buff_armor":
            player["buff_def"] += 3
            await send_text(ws, f"{ab['name']} fortifies your defenses (+3 Armor).", "echo")

        elif etype == "buff_evasion":
            player["buff_def"] += 4
            await send_text(ws, f"{ab['name']} shrouds your form in shifting concealment (+4 Evasion).", "echo")

        elif etype == "buff_damage":
            player["buff_atk"] += 4
            await send_text(ws, f"{ab['name']} empowers your strikes (+4 Attack Power).", "echo")

        elif etype == "debuff_recovery":
            foes = [c for c in ACTIVE_CREATURES.get(player["room"], []) if c["hp"] > 0]
            if foes:
                target = foes[0]
                target["stun_until"] = now + 8.0
                await send_text(ws, f"{ab['name']} ensnares {target['name']}, locking it in Recovery for 8 seconds!", "combat")

        elif etype == "summon_pet":
            player["pet"] = {"name": ab["pet_name"], "power": ab["power"], "expires": now + 90.0}
            await send_text(ws, f"You summon {ab['pet_name']} to fight alongside you for 90 seconds!", "echo")
        return

    await send_text(ws, "Unrecognized command. Type HELP for a list of commands.", "system")


# ============================================================================
# WEBSOCKET CONNECTION HANDLER
# ============================================================================
async def client_handler(websocket):
    player = None
    try:
        await send_text(websocket, "=== WELCOME TO AETHERIA ===\nEnter your character name:", "system")
        raw_name = await websocket.recv()
        char_name = json.loads(raw_name).get("command", "Traveler").strip()[:18] or "Traveler"

        await send_text(
            websocket,
            "Choose your Guild (sorcerer, battle_mage, berserker, cleric, ranger, paladin, thief):",
            "system",
        )
        raw_guild = await websocket.recv()
        guild_choice = json.loads(raw_guild).get("command", "sorcerer").strip().lower().replace(" ", "_")
        if guild_choice not in GUILDS:
            guild_choice = "sorcerer"

        player = load_or_create_character(websocket, char_name, guild_choice)
        CONNECTED_PLAYERS[websocket] = player

        await send_text(websocket, f"Welcome, {player['name']} of the {GUILDS[player['guild']]['name']} Guild!", "echo")
        await send_vitals(player)
        await send_room(player)
        await broadcast_room(player["room"], f"{player['name']} steps into the realm.", exclude_ws=websocket, style="system")

        async for message in websocket:
            data = json.loads(message)
            if "command" in data:
                await handle_command(player, data["command"])
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if websocket in CONNECTED_PLAYERS:
            departed = CONNECTED_PLAYERS.pop(websocket)
            await save_player(departed)
            await broadcast_room(departed["room"], f"{departed['name']} vanishes from the realm.", style="system")


async def main():
    asyncio.create_task(world_tick_loop())
    print("Aetheria Web MUD Server listening on ws://0.0.0.0:8765")
    async with websockets.serve(client_handler, "0.0.0.0", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
