-- ============================================================================
-- Aetheria Web MUD: Complete Database Schema & World Seed (seed_world.sql)
-- Compatible with MySQL 8.0+ / MariaDB (XAMPP / phpMyAdmin / Command Line)
-- ============================================================================

CREATE DATABASE IF NOT EXISTS aetheria_mud CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE aetheria_mud;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ============================================================================
-- PART 1: TABLE DEFINITIONS (SCHEMA)
-- ============================================================================

-- 1. Guilds / Classes
CREATE TABLE IF NOT EXISTS guilds (
    guild_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    base_hp INT NOT NULL DEFAULT 100,
    base_resource INT NOT NULL DEFAULT 100,
    starting_room_id VARCHAR(100) NOT NULL,
    lifesteal_pct DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Universal Skills
CREATE TABLE IF NOT EXISTS skills (
    skill_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Zones & Rooms
CREATE TABLE IF NOT EXISTS rooms (
    room_id VARCHAR(100) PRIMARY KEY,
    zone_name VARCHAR(100) NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    exits_json JSON NOT NULL,
    ambient_anim VARCHAR(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Abilities & Spells
CREATE TABLE IF NOT EXISTS abilities (
    ability_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    guild_id VARCHAR(50) NOT NULL,
    rank_required INT NOT NULL DEFAULT 1,
    resource_cost INT NOT NULL DEFAULT 10,
    recovery_sec INT NOT NULL DEFAULT 3,
    skill_id VARCHAR(50) NOT NULL,
    effect_type VARCHAR(50) NOT NULL,
    base_power INT NOT NULL DEFAULT 10,
    anim_trigger VARCHAR(50) DEFAULT NULL,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Items & Equipment
CREATE TABLE IF NOT EXISTS items (
    item_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    slot VARCHAR(50) NOT NULL,
    power_bonus INT NOT NULL DEFAULT 0,
    defense_bonus INT NOT NULL DEFAULT 0,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Creatures & Mobs
CREATE TABLE IF NOT EXISTS creatures (
    creature_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    rank INT NOT NULL DEFAULT 1,
    max_hp INT NOT NULL DEFAULT 30,
    attack_power INT NOT NULL DEFAULT 5,
    defense INT NOT NULL DEFAULT 2,
    room_id VARCHAR(100) NOT NULL,
    respawn_sec INT NOT NULL DEFAULT 30,
    xp_reward INT NOT NULL DEFAULT 20,
    loot_kronars INT NOT NULL DEFAULT 5
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Player Characters (Persistent Saves)
CREATE TABLE IF NOT EXISTS players (
    name VARCHAR(50) PRIMARY KEY,
    guild_id VARCHAR(50) NOT NULL,
    rank INT NOT NULL DEFAULT 1,
    xp INT NOT NULL DEFAULT 0,
    hp INT NOT NULL DEFAULT 100,
    max_hp INT NOT NULL DEFAULT 100,
    resource INT NOT NULL DEFAULT 100,
    max_resource INT NOT NULL DEFAULT 100,
    kronars INT NOT NULL DEFAULT 50,
    room_id VARCHAR(100) NOT NULL DEFAULT 'crossroads_plaza',
    inventory_json JSON DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Player Skill Progression (Tracks ranks per skill via Focus Absorption)
CREATE TABLE IF NOT EXISTS player_skills (
    player_name VARCHAR(50) NOT NULL,
    skill_id VARCHAR(50) NOT NULL,
    skill_rank INT NOT NULL DEFAULT 1,
    absorption_pool INT NOT NULL DEFAULT 0,
    PRIMARY KEY (player_name, skill_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ============================================================================
-- PART 2: WORLD & CLASS SEED DATA
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. GUILDS / CLASSES (7 Classes)
-- ----------------------------------------------------------------------------
INSERT INTO guilds (guild_id, name, resource_type, base_hp, base_resource, starting_room_id, lifesteal_pct, description) VALUES
('sorcerer', 'Sorcerer', 'Arcane', 80, 120, 'astral_sanctum_hall', 0.00, 'Wielders of volatile arcane and chaos magic who manipulate astral currents and raw entropy.'),
('battle_mage', 'Battle Mage', 'Elemental', 110, 90, 'elemental_forge_court', 0.00, 'Armored elementalists who weave primal fire and frost with steel while commanding bound elemental familiars.'),
('berserker', 'Berserker', 'Rage', 145, 100, 'bloodstone_pit', 0.25, 'Fierce frontline warriors who channel combat fury and siphon vitality through physical strikes.'),
('cleric', 'Cleric', 'Devotion', 100, 110, 'sanctuary_nave', 0.00, 'Devoted conduits of divine grace who mend wounds, erect sacred wards, and banish corruption.'),
('ranger', 'Ranger', 'Focus', 115, 95, 'whispering_canopy_lodge', 0.00, 'Master trackers and wilderness scouts who command loyal animal companions and lethal ambushes.'),
('paladin', 'Paladin', 'Zeal', 130, 85, 'bastion_chapel', 0.00, 'Oath-bound champions clad in heavy plate who project protective auras and deliver radiant judgment.'),
('thief', 'Thief', 'Guile', 95, 100, 'shadow_alley_den', 0.00, 'Elusive operatives skilled in stealth, vital strikes, alchemy-laced blades, and trap disarming.')
ON DUPLICATE KEY UPDATE name=VALUES(name), resource_type=VALUES(resource_type), base_hp=VALUES(base_hp), base_resource=VALUES(base_resource), starting_room_id=VALUES(starting_room_id), lifesteal_pct=VALUES(lifesteal_pct), description=VALUES(description);

-- ----------------------------------------------------------------------------
-- 2. UNIVERSAL SKILLS (16 Skills)
-- ----------------------------------------------------------------------------
INSERT INTO skills (skill_id, name, category, description) VALUES
('arcane_lore', 'Arcane Lore', 'Magic', 'Governs raw magical potency and chaos manipulation.'),
('elemental_craft', 'Elemental Craft', 'Magic', 'Controls fire, frost, and lightning manifestations.'),
('divine_channeling', 'Divine Channeling', 'Magic', 'Focuses sacred healing, wards, and radiant blasts.'),
('nature_attunement', 'Nature Attunement', 'Magic', 'Harmonizes with primal spirits, weather, and beasts.'),
('targeted_projection', 'Targeted Projection', 'Magic', 'Determines accuracy when unleashing ranged spells.'),
('summoning_bond', 'Summoning Bond', 'Magic', 'Strengthens summoned familiars and animal companions.'),
('heavy_blades', 'Heavy Blades', 'Combat', 'Proficiency with greatswords, battleaxes, and cleavers.'),
('light_blades', 'Light Blades', 'Combat', 'Proficiency with daggers, stilettos, and rapiers.'),
('staves_blunt', 'Staves & Blunt', 'Combat', 'Proficiency with quarterstaves, maces, and warhammers.'),
('marksmanship', 'Marksmanship', 'Combat', 'Precision with longbows, shortbows, and crossbows.'),
('evasion', 'Evasion', 'Defense', 'Ability to dodge incoming physical blows and projectiles.'),
('parry_ward', 'Parry & Ward', 'Defense', 'Deflecting attacks using weapons, shields, or force.'),
('armor_mastery', 'Armor Mastery', 'Defense', 'Reduces stamina drain and movement penalties in armor.'),
('stealth', 'Stealth', 'Subterfuge', 'Moving unseen through shadows and dense terrain.'),
('perception', 'Perception', 'Survival', 'Spotting hidden foes, traps, and rare forageables.'),
('foraging', 'Foraging', 'Survival', 'Harvesting herbs, reagents, and pelts from the wild.')
ON DUPLICATE KEY UPDATE name=VALUES(name), category=VALUES(category), description=VALUES(description);

-- ----------------------------------------------------------------------------
-- 3. ZONES & ROOMS (Central Hub, 7 Guild Sanctuaries, Whispering Fen)
-- ----------------------------------------------------------------------------
INSERT INTO rooms (room_id, zone_name, title, description, exits_json, ambient_anim) VALUES
('crossroads_plaza', 'Oakhaven Town', 'Oakhaven, Crossroads Plaza',
 'Wide cobblestones worn smooth by generations of travelers radiate outward from a weathered marble fountain at the heart of town. Lanterns of wrought iron cast warm pools of amber light across timber-framed storefronts and guild banners fluttering in the evening breeze.',
 '{"north": "bastion_chapel", "northeast": "sanctuary_nave", "east": "elemental_forge_court", "southeast": "shadow_alley_den", "south": "whispering_fen_verge", "southwest": "bloodstone_pit", "west": "whispering_canopy_lodge", "up": "astral_sanctum_hall"}',
 'town_lanterns'),

('astral_sanctum_hall', 'The Astral Sanctum', 'The Sorcerer''s Sanctum, Hall of Mirrors',
 'High vaulted ceilings of dark basalt soar overhead, inlaid with silver filigree tracing the paths of the three moons. Tall, arched windows let in the cool twilight air, illuminating polished obsidian mirrors arranged in a wide circle around a sunken marble dais. A faint scent of ozone lingers in the shadows.',
 '{"east": "astral_sanctum_terrace", "down": "crossroads_plaza"}',
 'astral_twinkle'),

('astral_sanctum_terrace', 'The Astral Sanctum', 'The Sorcerer''s Sanctum, Astral Terrace',
 'Open to the night sky, this wide flagstone balcony juts out from the tower''s eastern wall, offering an unobstructed view of the heavens and the mist-shrouded marshlands far below. Brass astrolabes and mounted spyglasses line the low stone balustrade.',
 '{"west": "astral_sanctum_hall"}',
 'astral_twinkle'),

('elemental_forge_court', 'Elemental Conclave', 'The Elemental Conclave, Runed Courtyard',
 'Basalt pillars etched with glowing red and cerulean glyphs surround an open-air sparring yard paved with scorched granite. Braziers of eternal flame crackle beside frost-rimed training dummies, filling the air with sparks and swirling vapor.',
 '{"west": "crossroads_plaza"}',
 'forge_sparks'),

('bloodstone_pit', 'The Bloodstone Arena', 'The Bloodstone Arena, Hall of Scars',
 'Rough-hewn timber beams and iron-banded stone walls enclose a sunken sand pit stained dark from countless duels. Racks of notched greataxes and heavy mauls line the perimeter beneath tattered war banners.',
 '{"northeast": "crossroads_plaza"}',
 'arena_dust'),

('sanctuary_nave', 'Cathedral of Dawn', 'Cathedral of Dawn, Sunlit Nave',
 'Sunlight streams through towering stained-glass lancets, painting vibrant mosaics across white limestone flagstones. Quiet hymns echo softly beneath ribbed arches, and a shallow font of crystal-clear water rests before the altar.',
 '{"southwest": "crossroads_plaza"}',
 'radiant_motes'),

('whispering_canopy_lodge', 'Timberwatch', 'Timberwatch, Whispering Canopy Lodge',
 'Built around the trunk of an ancient ironwood tree, this elevated timber hall smells of cedar resin, oiled leather, and damp pine needles. Longbows and fletching benches line the open railings overlooking the western treeline.',
 '{"east": "crossroads_plaza"}',
 'forest_breeze'),

('bastion_chapel', 'The Silver Bastion', 'The Silver Bastion, Vigil Hall',
 'Polished shields bearing sunburst crests hang along thick granite walls lit by tall beeswax candles. Rows of heavy plate armor stand at attention beside an anvil blessed for consecrated steel.',
 '{"south": "crossroads_plaza"}',
 'radiant_motes'),

('shadow_alley_den', 'The Underbelly', 'The Velvet Coin, Backroom Den',
 'Behind a false wine cask lies a low-ceilinged cellar thick with pipe smoke and whispered bargains. Lockpicking tumblers, vials of murky distillates, and maps of city rooftops clutter scarred oak tables.',
 '{"northwest": "crossroads_plaza"}',
 'candle_flicker'),

('whispering_fen_verge', 'The Whispering Fen', 'The Whispering Fen, Muddy Verge',
 'Solid cobblestones end abruptly at a squishy, peat-heavy bank where firm ground gives way to the stagnant, black waters of the marsh. Stunted willow trees droop over the murky shallows, their trailing branches thick with pale, silvery moss.',
 '{"north": "crossroads_plaza", "south": "whispering_fen_causeway"}',
 'swamp_mist'),

('whispering_fen_causeway', 'The Whispering Fen', 'The Whispering Fen, Sunken Causeway',
 'Half-submerged flagstones of pale limestone form a treacherous path through the black waters of the bog. Faint marsh-gas wisps flicker just beneath the murky surface, casting an eerie pale green glow across the slick stone.',
 '{"north": "whispering_fen_verge"}',
 'swamp_mist')
ON DUPLICATE KEY UPDATE zone_name=VALUES(zone_name), title=VALUES(title), description=VALUES(description), exits_json=VALUES(exits_json), ambient_anim=VALUES(ambient_anim);

-- ----------------------------------------------------------------------------
-- 4. RANK 1 ABILITIES & PET SUMMONS (All 7 Classes)
-- ----------------------------------------------------------------------------
INSERT INTO abilities (ability_id, name, guild_id, rank_required, resource_cost, recovery_sec, skill_id, effect_type, base_power, anim_trigger, description) VALUES
-- Sorcerer
('chaos_bolt', 'Chaos Bolt', 'sorcerer', 1, 10, 3, 'arcane_lore', 'damage', 18, 'chaos_bolt', 'Hurls a jagged lance of unstable violet entropy at a single foe.'),
('astral_veil', 'Astral Veil', 'sorcerer', 1, 12, 3, 'arcane_lore', 'buff_evasion', 15, 'astral_veil', 'Bends ambient starlight around your form, distorting your silhouette.'),
('entropy_shackle', 'Entropy Shackle', 'sorcerer', 1, 14, 4, 'arcane_lore', 'debuff_recovery', 3, 'entropy_shackle', 'Binds a target in crackling gravity bands, extending their Recovery.'),

-- Battle Mage
('flame_arc', 'Flame Arc', 'battle_mage', 1, 10, 3, 'elemental_craft', 'damage', 16, 'flame_arc', 'Sweeps a crescent of searing fire across close-range enemies.'),
('summon_ember_hound', 'Summon Ember Hound', 'battle_mage', 1, 20, 4, 'summoning_bond', 'summon_pet', 12, 'summon_ember_hound', 'Manifests a fierce hound of living magma and soot to fight at your side.'),
('frost_aegis', 'Frost Aegis', 'battle_mage', 1, 12, 3, 'elemental_craft', 'buff_armor', 14, 'frost_aegis', 'Coats your armor in hardened rime ice that absorbs physical impact.'),

-- Berserker
('savage_cleave', 'Savage Cleave', 'berserker', 1, 15, 3, 'heavy_blades', 'damage_lifesteal', 20, 'lifesteal_cleave', 'A brutal overhead chop that deals heavy damage and siphons life force.'),
('blood_howl', 'Blood Howl', 'berserker', 1, 10, 2, 'heavy_blades', 'buff_damage', 15, 'blood_howl', 'Unleashes a primal roar that increases melee power and bolsters vitality.'),

-- Cleric
('radiant_mend', 'Radiant Mend', 'cleric', 1, 12, 3, 'divine_channeling', 'heal', 24, 'radiant_mend', 'Channels warm golden light to knit torn flesh and restore stamina.'),
('smite_blight', 'Smite Blight', 'cleric', 1, 10, 3, 'divine_channeling', 'damage', 16, 'smite_blight', 'Calls down a pillar of purifying light upon corrupted foes.'),
('sacred_ward', 'Sacred Ward', 'cleric', 1, 14, 3, 'divine_channeling', 'buff_armor', 16, 'sacred_ward', 'Surrounds an ally in a shimmering dome of consecrated force.'),

-- Ranger
('piercing_shot', 'Piercing Shot', 'ranger', 1, 10, 3, 'marksmanship', 'damage', 17, 'piercing_shot', 'Looses a high-velocity arrow aimed squarely at an enemy''s weak point.'),
('call_timber_wolf', 'Call Timber Wolf', 'ranger', 1, 18, 4, 'summoning_bond', 'summon_pet', 11, 'call_timber_wolf', 'Summons a loyal grey wolf companion from the wilds to harry your foes.'),
('briar_snare', 'Briar Snare', 'ranger', 1, 12, 3, 'nature_attunement', 'debuff_recovery', 3, 'briar_snare', 'Causes thorny vines to erupt beneath a foe, slowing their movement.'),

-- Paladin
('sunfire_strike', 'Sunfire Strike', 'paladin', 1, 12, 3, 'heavy_blades', 'damage', 19, 'sunfire_strike', 'Channels blazing solar zeal through your weapon on impact.'),
('aura_of_resolve', 'Aura of Resolve', 'paladin', 1, 15, 3, 'divine_channeling', 'buff_armor', 18, 'aura_of_resolve', 'Radiates an inspiring golden aura that fortifies defenses.'),
('lay_hands', 'Lay Hands', 'paladin', 1, 18, 4, 'divine_channeling', 'heal', 22, 'radiant_mend', 'Transfers sacred vitality through direct touch to heal wounds.'),

-- Thief
('viper_ambush', 'Viper Ambush', 'thief', 1, 12, 3, 'light_blades', 'damage', 21, 'viper_ambush', 'Strikes swiftly from the shadows for high critical precision.'),
('smoke_screen', 'Smoke Screen', 'thief', 1, 10, 2, 'stealth', 'buff_evasion', 20, 'smoke_screen', 'Shatters an alchemical capsule, blanketing the area in concealing smoke.'),
('venom_coat', 'Venom Coat', 'thief', 1, 12, 2, 'light_blades', 'buff_damage', 14, 'venom_coat', 'Applies a stinging marsh-toxin to your blade for extra damage.')
ON DUPLICATE KEY UPDATE name=VALUES(name), guild_id=VALUES(guild_id), rank_required=VALUES(rank_required), resource_cost=VALUES(resource_cost), recovery_sec=VALUES(recovery_sec), skill_id=VALUES(skill_id), effect_type=VALUES(effect_type), base_power=VALUES(base_power), anim_trigger=VALUES(anim_trigger), description=VALUES(description);

-- ----------------------------------------------------------------------------
-- 5. STARTER ITEMS & EQUIPMENT
-- ----------------------------------------------------------------------------
INSERT INTO items (item_id, name, item_type, slot, power_bonus, defense_bonus, description) VALUES
('rowan_staff', 'a gnarled rowanwood staff', 'weapon', 'main_hand', 4, 1, 'A lightweight staff etched with swirling astral runes.'),
('steel_stiletto', 'a thin steel stiletto', 'weapon', 'off_hand', 3, 0, 'A needle-pointed blade suited for quick thrusts and skinning.'),
('runed_broadsword', 'a rune-etched iron broadsword', 'weapon', 'main_hand', 6, 1, 'A balanced blade inlaid with copper conductors for elemental channeling.'),
('notched_greataxe', 'a heavy notched greataxe', 'weapon', 'main_hand', 8, 0, 'A brutal two-handed axe stained with dried battle scars.'),
('oak_mace', 'a brass-bound oak mace', 'weapon', 'main_hand', 5, 1, 'A sturdy ceremonial mace engraved with sunburst motifs.'),
('ash_longbow', 'a recurved ash longbow', 'weapon', 'main_hand', 6, 0, 'A supple hunting bow strung with waxed sinew.'),
('consecrated_claymore', 'a silver-hilted claymore', 'weapon', 'main_hand', 7, 2, 'A gleaming greatsword blessed at the Vigil Hall.'),
('midnight_robe', 'a midnight-blue apprentice robe', 'armor', 'chest', 0, 2, 'Flowing wool vestments woven with silver thread.'),
('scaled_hauberk', 'a scorched scale hauberk', 'armor', 'chest', 0, 5, 'Overlapping iron scales treated against heat and frost.'),
('studded_hide', 'boiled leather and wolf-pelt armor', 'armor', 'chest', 0, 4, 'Supple hide armor reinforced with bronze studs.'),
('steel_breastplate', 'a polished steel breastplate', 'armor', 'chest', 0, 7, 'Heavy plate armor bearing an embossed sunburst.'),
('shadow_jerkin', 'a charcoal-dyed leather jerkin', 'armor', 'chest', 0, 3, 'Silent, close-fitting leather designed for unrestricted movement.'),
('iron-shod staff', 'Iron-Shod Staff', 'weapon', 'main_hand', 5, 1, 'A sturdy quarterstaff reinforced with cold-forged iron caps.'),
('reinforced leather tunic', 'Reinforced Leather Tunic', 'armor', 'chest', 0, 4, 'Hardened leather plates riveted over a padded gambeson.'),
('minor healing draught', 'Minor Healing Draught', 'consumable', 'belt', 25, 0, 'A small glass vial of crimson herbal tonic that restores 25 HP.')
ON DUPLICATE KEY UPDATE name=VALUES(name), item_type=VALUES(item_type), slot=VALUES(slot), power_bonus=VALUES(power_bonus), defense_bonus=VALUES(defense_bonus), description=VALUES(description);

-- ----------------------------------------------------------------------------
-- 6. CREATURE & PET TEMPLATES
-- ----------------------------------------------------------------------------
INSERT INTO creatures (creature_id, name, rank, max_hp, attack_power, defense, room_id, respawn_sec, xp_reward, loot_kronars) VALUES
('juvenile_bog_rat', 'a juvenile bog rat', 1, 35, 6, 4, 'whispering_fen_verge', 25, 25, 8),
('bloated_marsh_toad', 'a bloated marsh toad', 1, 42, 7, 5, 'whispering_fen_verge', 30, 30, 10),
('fen_crawler', 'a spiny fen-crawler', 2, 60, 11, 8, 'whispering_fen_causeway', 35, 45, 18)
ON DUPLICATE KEY UPDATE name=VALUES(name), rank=VALUES(rank), max_hp=VALUES(max_hp), attack_power=VALUES(attack_power), defense=VALUES(defense), room_id=VALUES(room_id), respawn_sec=VALUES(respawn_sec), xp_reward=VALUES(xp_reward), loot_kronars=VALUES(loot_kronars);

SET FOREIGN_KEY_CHECKS = 1;
