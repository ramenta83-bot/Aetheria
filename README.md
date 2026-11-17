# Aetheria: Real-Time Multiplayer Web MUD

A data-driven, browser-based Multi-User Dungeon (MUD) engine built with Python WebSockets, MySQL, and vanilla HTML5/CSS3/JavaScript featuring real-time ASCII animations and seven distinct playable classes.

## Playable Classes (7-Class Roster)
* **Sorcerer:** Arcane & Chaos magic specialist utilizing `Attune` / `Unleash` mechanics.
* **Battle Mage:** Hybrid elemental caster and combat pet summoner.
* **Berserker:** Rage-fueled melee bruiser with physical damage lifesteal.
* **Cleric:** Divine healer, ward weaver, and undead banisher.
* **Ranger:** Wilderness tracker, trapper, and animal companion handler.
* **Paladin:** Armored radiant warrior with protective party auras.
* **Thief:** Stealth ambush specialist using poisons, evasion, and lockpicking.

## Directory Structure
```text
aetheria-web-mud/
├── database/
│   ├── schema.sql          # Relational MySQL table definitions
│   └── seed_world.sql      # 7 classes, 16 skills, rooms, abilities, and starter gear
├── backend/
│   ├── server.py           # Async Python WebSocket game loop, pet ticks, and MySQL sync
│   └── requirements.txt    # Python dependencies (websockets, mysql-connector-python)
├── frontend/
│   ├── index.html          # Browser terminal shell & Vitals HUD
│   ├── style.css           # External dark-mode monospace stylesheet
│   ├── client.js           # WebSocket client, Recovery timer, and command parser
│   └── animations.js       # Client-side multi-frame ASCII stage player
└── deploy/
    ├── web-mud.conf        # Nginx reverse proxy configuration for WSS
    └── web-mud.service     # Linux systemd unit for 24/7 background hosting
```

## Quick Local Setup
1. **Import Database:** Open `phpMyAdmin`, create a database named `aetheria_mud`, and import `database/schema.sql` followed by `database/seed_world.sql`.
2. **Start Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python server.py
   ```
3. **Launch Client:** Open `frontend/index.html` in your browser (or serve via XAMPP/Apache) and log in with your character name.
