#!/usr/bin/env python3
"""
Web MUD Multiplayer Server (server.py)
Features:
- Real-time WebSocket multiplayer loop
- Live MySQL persistence (auto-falls back to in-memory mode if MySQL is offline)
- Original Lexicon: Ranks, Recovery timers, Attune / Unleash, Strike, Focus Absorption
- All 7 Classes with Berserker Lifesteal & Battle Mage / Ranger Active Pet Combat Loops
- Real-time ASCII Animation event triggers
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
    "database": os.environ.get("MUD_DB_NAME", "web_mud"),
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

# Active world creatures
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
# DATABASE PERSISTENCE LAYER
# ============================================================================
def get_db_connection():
    if not MYSQL_AVAILABLE:
        return None
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Exception:
        return None


def load_or_create_character(name: str, guild_key: str) -> dict:
    guild = GUILDS.get(guild_key, GUILDS["sorcerer"])
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM characters WHERE name = %s", (name,))
            row = cur.fetchone()
            if row:
                cur.close()
                conn.close()
                return {
                    "name": row["name"],
                    "guild": row["guild_id"],
                    "rank": row["rank"],
                    "hp": row["current_hp"],
                    "max_hp": row["max_hp"],
                    "res": row["current_resource"],
                    "max_res": row["max_resource"],
                    "room": row["room_id"],
                    "kronars": row["kronars"],
                    "focus_pool": row["focus_pool"],
                    "attuned": None,
                    "recovery_until": 0.0,
                    "buff_atk": 0,
                    "buff_def": 0,
                    "pet": None,
                }
            cur.execute(
                """INSERT INTO characters (name, guild_id, rank, current_hp, max_hp, current_resource, max_resource, room_id, kronars, focus_pool)
                   VALUES (%s, %s, 1, %s, %s, %s, %s, %s, 50, 0)""",
                (name, guild_key, guild["hp"], guild["hp"], guild["res"], guild["res"], guild["start"]),
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass

    return {
        "name": name,
        "guild": guild_key,
        "rank": 1,
        "hp": guild["hp"],
        "max_hp": guild["hp"],
        "res": guild["res"],
        "max_res": guild["res"],
        "room": guild["start"],
        "kronars": 50,
        "focus_pool": 0,
        "attuned": None,
        "recovery_until": 0.0,
        "buff_atk": 0,
        "buff_def": 0,
        "pet": None,  # {"name": str, "power": int, "expires": float}
    }


def save_character(player: dict):
    conn = get_db_connection()
    if not conn:
        return
    try:
        cur = conn.cursor()
        cur.execute(
            """UPDATE characters
               SET rank = %s, current_hp = %s, current_resource = %s, room_id = %s, kronars = %s, focus_pool = %s
               WHERE name = %s""",
            (player["rank"], player["hp"], player["res"], player["room"], player["kronars"], player["focus_pool"], player["name"]),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception:
        pass


# ============================================================================
# MESSAGING & ROOM BROADCAST HELPERS
# ============================================================================
async def send_msg(ws, text: str, tag: str = "normal"):
    await ws.send(json.dumps({"type": "text", "text": text, "tag": tag}))


async def send_anim(ws, effect: str):
    await ws.send(json.dumps({"type": "anim", "effect": effect}))


async def broadcast_room(room_id: str, text: str, exclude_ws=None, anim: str = None):
    for ws, p in list(CONNECTED_PLAYERS.items()):
        if p["room"] == room_id and ws != exclude_ws:
            await send_msg(ws, text)
            if anim:
                await send_anim(ws, anim)


def format_room(player: dict) -> str:
    room = ROOMS[player["room"]]
    others = [p["name"] for p in CONNECTED_PLAYERS.values() if p["room"] == player["room"] and p["name"] != player["name"]]
    pets = [f"{p['name']}'s {p['pet']['name']}" for p in CONNECTED_PLAYERS.values() if p["room"] == player["room"] and p["pet"]]
    creatures = [c["name"] for c in ACTIVE_CREATURES.get(player["room"], []) if c["hp"] > 0]

    entities = others + pets + creatures
    also_line = f"You also see {', '.join(entities)}.\n" if entities else ""
    exits_line = ", ".join(room["exits"].keys()) if room["exits"] else "none"
    return f"[{room['title']}]\n{room['desc']}\n{also_line}Obvious paths: {exits_line}."


# ============================================================================
# BACKGROUND LOOPS: PET COMBAT, FOCUS ABSORPTION & CREATURE RESPAWN
# ============================================================================
async def world_tick_loop():
    while True:
        await asyncio.sleep(4.0)
        now = time.time()

        # 1. Active Pet Combat Loop (Battle Mage & Ranger) & Focus Absorption
        for ws, p in list(CONNECTED_PLAYERS.items()):
            # Focus Absorption (converts focus pool into Rank progress)
            if p["focus_pool"] > 0:
                absorbed = min(5, p["focus_pool"])
                p["focus_pool"] -= absorbed

            # Regenerate a trickle of HP & Resource
            p["hp"] = min(p["max_hp"], p["hp"] + 2)
            p["res"] = min(p["max_res"], p["res"] + 3)

            # Pet Combat Tick
            if p["pet"]:
                if now >= p["pet"]["expires"]:
                    pet_name = p["pet"]["name"]
                    p["pet"] = None
                    await send_msg(ws, f"Your bond fades, and {pet_name} dissolves back into the ether.", "system")
                    continue

                room_foes = [c for c in ACTIVE_CREATURES.get(p["room"], []) if c["hp"] > 0]
                if room_foes:
                    target = room_foes[0]
                    dmg = random.randint(max(2, p["pet"]["power"] - 3), p["pet"]["power"] + 4)
                    target["hp"] -= dmg
                    await send_msg(ws, f"Your {p['pet']['name']} lunges at {target['name']} for {dmg} damage!", "combat")
                    await send_anim(ws, "pet_bite")
                    if target["hp"] <= 0:
                        await handle_creature_defeat(ws, p, target)

        # 2. Creature Counterattack & Respawn Loop
        for room_id, foes in ACTIVE_CREATURES.items():
            players_here = [(w, pl) for w, pl in CONNECTED_PLAYERS.items() if pl["room"] == room_id]
            for foe in foes:
                if foe["hp"] <= 0:
                    if now >= foe.get("respawn_at", 0):
                        foe["hp"] = foe["max_hp"]
                        for w, _ in players_here:
                            await send_msg(w, f"{foe['name'].capitalize()} emerges from the shadows.", "ambient")
                elif players_here and now >= foe["stun_until"]:
                    target_ws, target_p = random.choice(players_here)
                    dmg = max(1, foe["atk"] - target_p["buff_def"] + random.randint(-2, 2))
                    target_p["hp"] = max(1, target_p["hp"] - dmg)
                    await send_msg(target_ws, f"{foe['name'].capitalize()} strikes you for {dmg} damage! (HP: {target_p['hp']}/{target_p['max_hp']})", "danger")


async def handle_creature_defeat(ws, player: dict, target: dict):
    target["hp"] = 0
    target["respawn_at"] = time.time() + 25
    player["kronars"] += target["kronars"]
    player["focus_pool"] += target["xp"]
    await send_msg(ws, f"{target['name'].capitalize()} collapses! You gather {target['kronars']} Kronars and absorb {target['xp']} Focus.", "reward")
    await send_anim(ws, "victory_spark")

    # Rank advancement check
    needed = player["rank"] * 100
    if player["focus_pool"] >= needed:
        player["rank"] += 1
        player["max_hp"] += 12
        player["max_res"] += 10
        player["hp"] = player["max_hp"]
        player["res"] = player["max_res"]
        await send_msg(ws, f"*** CONGRATULATIONS! You have ascended to Rank {player['rank']}! ***", "reward")
    save_character(player)


# ============================================================================
# COMMAND PARSER
# ============================================================================
DIR_ALIASES = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "ne": "northeast", "nw": "northwest", "se": "southeast", "sw": "southwest",
    "u": "up", "d": "down"
}


async def process_command(ws, player: dict, raw: str):
    cmd_line = raw.strip()
    if not cmd_line:
        return

    parts = cmd_line.split()
    verb = parts[0].lower()
    args = " ".join(parts[1:]).lower()

    # Check Recovery Timer (blocks combat & movement)
    now = time.time()
    if verb in ("north", "south", "east", "west", "northeast", "northwest", "southeast", "southwest", "up", "down",
                "n", "s", "e", "w", "ne", "nw", "se", "sw", "u", "d", "strike", "unleash"):
        if now < player["recovery_until"]:
            rem = round(player["recovery_until"] - now, 1)
            await send_msg(ws, f"...wait {rem} seconds (Recovery).", "system")
            return

    # Movement
    direction = DIR_ALIASES.get(verb, verb)
    if direction in ROOMS[player["room"]]["exits"]:
        old_room = player["room"]
        new_room = ROOMS[old_room]["exits"][direction]
        await broadcast_room(old_room, f"{player['name']} heads {direction}.", exclude_ws=ws)
        player["room"] = new_room
        player["recovery_until"] = now + 1.0
        await broadcast_room(new_room, f"{player['name']} arrives.", exclude_ws=ws)
        await send_msg(ws, format_room(player))
        await send_anim(ws, ROOMS[new_room]["ambient"])
        save_character(player)
        return

    if verb == "look":
        await send_msg(ws, format_room(player))
        return

    if verb == "status" or verb == "score":
        g_info = GUILDS[player["guild"]]
        pet_str = player["pet"]["name"] if player["pet"] else "None"
        await send_msg(
            ws,
            f"Name: {player['name']} | Guild: {g_info['name']} | Rank: {player['rank']}\n"
            f"HP: {player['hp']}/{player['max_hp']} | {g_info['resource']}: {player['res']}/{player['max_res']} | Kronars: {player['kronars']}\n"
            f"Focus Pool: {player['focus_pool']} | Active Companion: {pet_str}",
            "system",
        )
        return

    if verb == "abilities":
        known = [ABILITIES[a]["name"] for a in GUILDS[player["guild"]]["abilities"]]
        await send_msg(ws, f"Known Abilities: {', '.join(known)}", "system")
        return

    if verb == "say":
        await send_msg(ws, f"You say, \"{' '.join(parts[1:])}\"")
        await broadcast_room(player["room"], f"{player['name']} says, \"{' '.join(parts[1:])}\"", exclude_ws=ws)
        return

    if verb == "who":
        roster = [f"{p['name']} (Rank {p['rank']} {GUILDS[p['guild']]['name']})" for p in CONNECTED_PLAYERS.values()]
        await send_msg(ws, "Adventurers Online:\n  " + "\n  ".join(roster), "system")
        return

    # Melee Attack: STRIKE <target>
    if verb == "strike":
        foes = [c for c in ACTIVE_CREATURES.get(player["room"], []) if c["hp"] > 0]
        if not foes:
            await send_msg(ws, "There is nothing here to strike.", "system")
            return
        target = next((f for f in foes if args in f["name"].lower()), foes[0])
        dmg = random.randint(8, 15) + player["buff_atk"]
        target["hp"] -= dmg
        player["recovery_until"] = now + 3.0

        # Berserker Lifesteal Mechanic
        lifesteal_pct = GUILDS[player["guild"]]["lifesteal"]
        if lifesteal_pct > 0:
            healed = max(1, int(dmg * lifesteal_pct))
            player["hp"] = min(player["max_hp"], player["hp"] + healed)
            await send_msg(ws, f"You strike {target['name']} for {dmg} damage and siphon {healed} HP!", "combat")
            await send_anim(ws, "lifesteal_cleave")
        else:
            await send_msg(ws, f"You strike {target['name']} for {dmg} physical damage!", "combat")
            await send_anim(ws, "melee_slash")

        if target["hp"] <= 0:
            await handle_creature_defeat(ws, player, target)
        return

    # Attune Ability: ATTUNE <ability name>
    if verb == "attune":
        guild_abs = GUILDS[player["guild"]]["abilities"]
        match = next((a for a in guild_abs if args in a.replace("_", " ") or args in ABILITIES[a]["name"].lower()), None)
        if not match:
            await send_msg(ws, "You do not know an ability by that name. Type ABILITIES to view your list.", "system")
            return
        player["attuned"] = match
        await send_msg(ws, f"You begin attuning your energy to {ABILITIES[match]['name']}...", "magic")
        return

    # Unleash Ability: UNLEASH [target]
    if verb == "unleash":
        if not player["attuned"]:
            await send_msg(ws, "You have not attuned an ability yet. Use ATTUNE <ability> first.", "system")
            return
        ab = ABILITIES[player["attuned"]]
        player["attuned"] = None

        if player["res"] < ab["cost"]:
            await send_msg(ws, f"Insufficient {GUILDS[player['guild']]['resource']} to unleash {ab['name']}.", "system")
            return

        player["res"] -= ab["cost"]
        player["recovery_until"] = now + ab["rec"]
        await send_anim(ws, ab["anim"])
        await broadcast_room(player["room"], f"{player['name']} unleashes {ab['name']}!", exclude_ws=ws, anim=ab["anim"])

        etype = ab["type"]
        if etype in ("damage", "damage_lifesteal"):
            foes = [c for c in ACTIVE_CREATURES.get(player["room"], []) if c["hp"] > 0]
            if not foes:
                await send_msg(ws, f"You unleash {ab['name']} into the empty air.", "magic")
                return
            target = next((f for f in foes if args in f["name"].lower()), foes[0])
            dmg = ab["power"] + random.randint(-3, 5) + player["buff_atk"]
            target["hp"] -= dmg
            if etype == "damage_lifesteal":
                healed = max(2, int(dmg * 0.35))
                player["hp"] = min(player["max_hp"], player["hp"] + healed)
                await send_msg(ws, f"Your {ab['name']} tears into {target['name']} for {dmg} damage, restoring {healed} HP!", "combat")
            else:
                await send_msg(ws, f"Your {ab['name']} blasts {target['name']} for {dmg} damage!", "magic")
            if target["hp"] <= 0:
                await handle_creature_defeat(ws, player, target)

        elif etype == "heal":
            healed = ab["power"] + random.randint(0, 6)
            player["hp"] = min(player["max_hp"], player["hp"] + healed)
            await send_msg(ws, f"{ab['name']} washes over you, restoring {healed} HP! ({player['hp']}/{player['max_hp']})", "magic")

        elif etype == "buff_armor":
            player["buff_def"] += 3
            await send_msg(ws, f"{ab['name']} fortifies your defenses (+3 Armor).", "magic")

        elif etype == "buff_evasion":
            player["buff_def"] += 4
            await send_msg(ws, f"{ab['name']} shrouds your form in shifting concealment (+4 Evasion).", "magic")

        elif etype == "buff_damage":
            player["buff_atk"] += 4
            await send_msg(ws, f"{ab['name']} empowers your strikes (+4 Attack Power).", "magic")

        elif etype == "debuff_recovery":
            foes = [c for c in ACTIVE_CREATURES.get(player["room"], []) if c["hp"] > 0]
            if foes:
                target = foes[0]
                target["stun_until"] = now + 8.0
                await send_msg(ws, f"{ab['name']} ensnares {target['name']}, locking it in Recovery for 8 seconds!", "magic")

        elif etype == "summon_pet":
            player["pet"] = {"name": ab["pet_name"], "power": ab["power"], "expires": now + 90.0}
            await send_msg(ws, f"You summon {ab['pet_name']} to fight alongside you for 90 seconds!", "magic")
        return

    await send_msg(ws, "Unrecognized command. Try: LOOK, NORTH/SOUTH/EAST/WEST/UP/DOWN, STRIKE, ATTUNE <ability>, UNLEASH, ABILITIES, STATUS, SAY, WHO.", "system")


# ============================================================================
# WEBSOCKET CONNECTION HANDLER
# ============================================================================
async def client_handler(websocket):
    player = None
    try:
        await send_msg(websocket, "=== WELCOME TO THE REALMS ===\nEnter your character name:", "system")
        raw_name = await websocket.recv()
        char_name = json.loads(raw_name).get("command", "Traveler").strip()[:18] or "Traveler"

        await send_msg(
            websocket,
            "Choose your Guild (sorcerer, battle_mage, berserker, cleric, ranger, paladin, thief):",
            "system",
        )
        raw_guild = await websocket.recv()
        guild_choice = json.loads(raw_guild).get("command", "sorcerer").strip().lower().replace(" ", "_")
        if guild_choice not in GUILDS:
            guild_choice = "sorcerer"

        player = load_or_create_character(char_name, guild_choice)
        CONNECTED_PLAYERS[websocket] = player

        await send_msg(websocket, f"Welcome, {player['name']} of the {GUILDS[guild_choice]['name']} Guild!\n", "reward")
        await send_msg(websocket, format_room(player))
        await send_anim(websocket, ROOMS[player["room"]]["ambient"])
        await broadcast_room(player["room"], f"{player['name']} steps into the realm.", exclude_ws=websocket)

        async for message in websocket:
            data = json.loads(message)
            if "command" in data:
                await process_command(websocket, player, data["command"])
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if websocket in CONNECTED_PLAYERS:
            departed = CONNECTED_PLAYERS.pop(websocket)
            save_character(departed)
            await broadcast_room(departed["room"], f"{departed['name']} vanishes from the realm.")


async def main():
    asyncio.create_task(world_tick_loop())
    print("Web MUD Server listening on ws://0.0.0.0:8765")
    async with websockets.serve(client_handler, "0.0.0.0", 8765):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
