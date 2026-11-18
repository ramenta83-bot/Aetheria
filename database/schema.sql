-- Aetheria Web MUD - Modular 8-Table MySQL Schema (web_mud)
-- Matches the current phpMyAdmin database structure for modular expansion.

CREATE DATABASE IF NOT EXISTS web_mud CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE web_mud;

-- 1. Seven-Class Registry
CREATE TABLE IF NOT EXISTS classes (
    class_id VARCHAR(32) PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    resource_name VARCHAR(32) NOT NULL,
    base_hp INT NOT NULL DEFAULT 100,
    base_resource INT NOT NULL DEFAULT 50,
    lifesteal_pct DECIMAL(4,2) NOT NULL DEFAULT 0.00,
    can_summon_pet BOOLEAN NOT NULL DEFAULT FALSE,
    starting_room_id VARCHAR(64) NOT NULL,
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. World Zones & Rooms
CREATE TABLE IF NOT EXISTS rooms (
    room_id VARCHAR(64) PRIMARY KEY,
    zone_name VARCHAR(64) NOT NULL,
    title VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    ambient_anim VARCHAR(32) DEFAULT NULL,
    exits_json JSON NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Player Characters
CREATE TABLE IF NOT EXISTS characters (
    char_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    char_name VARCHAR(64) UNIQUE NOT NULL,
    class_id VARCHAR(32) NOT NULL,
    current_rank INT NOT NULL DEFAULT 1,
    current_hp INT NOT NULL DEFAULT 100,
    max_hp INT NOT NULL DEFAULT 100,
    current_resource INT NOT NULL DEFAULT 50,
    max_resource INT NOT NULL DEFAULT 50,
    kronars INT NOT NULL DEFAULT 50,
    room_id VARCHAR(64) NOT NULL,
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (room_id) REFERENCES rooms(room_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Skills & Focus Absorption Pools
CREATE TABLE IF NOT EXISTS character_skills (
    char_id INT NOT NULL,
    skill_name VARCHAR(64) NOT NULL,
    skill_rank INT NOT NULL DEFAULT 1,
    focus_pool INT NOT NULL DEFAULT 0, -- 0 (Clear) to 34 (Saturated)
    PRIMARY KEY (char_id, skill_name),
    FOREIGN KEY (char_id) REFERENCES characters(char_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Modular Abilities, Spells & ASCII Triggers
CREATE TABLE IF NOT EXISTS abilities (
    ability_id VARCHAR(64) PRIMARY KEY,
    class_id VARCHAR(32) NOT NULL,
    min_rank INT NOT NULL DEFAULT 1,
    name VARCHAR(64) NOT NULL,
    command_verb VARCHAR(32) NOT NULL, -- 'unleash', 'strike', 'command'
    resource_cost INT NOT NULL DEFAULT 4,
    recovery_sec INT NOT NULL DEFAULT 3,
    skill_used VARCHAR(64) NOT NULL,
    effect_type ENUM('damage', 'heal', 'buff', 'debuff', 'summon', 'utility') NOT NULL,
    base_power INT NOT NULL DEFAULT 10,
    anim_effect VARCHAR(32) DEFAULT NULL,
    anim_color VARCHAR(16) DEFAULT '#7ee787',
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Pet & Companion Templates (Battle Mage & Ranger)
CREATE TABLE IF NOT EXISTS pet_templates (
    pet_id VARCHAR(64) PRIMARY KEY,
    class_id VARCHAR(32) NOT NULL,
    name VARCHAR(64) NOT NULL,
    base_hp INT NOT NULL DEFAULT 45,
    attack_damage INT NOT NULL DEFAULT 8,
    anim_effect VARCHAR(32) DEFAULT 'summon_hound',
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Items & Character Inventory
CREATE TABLE IF NOT EXISTS items (
    item_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(128) NOT NULL,
    slot ENUM('weapon', 'armor', 'worn', 'held', 'container') NOT NULL,
    damage_bonus INT NOT NULL DEFAULT 0,
    defense_bonus INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS character_inventory (
    inv_id INT AUTO_INCREMENT PRIMARY KEY,
    char_id INT NOT NULL,
    item_id VARCHAR(64) NOT NULL,
    is_equipped BOOLEAN NOT NULL DEFAULT FALSE,
    quantity INT NOT NULL DEFAULT 1,
    FOREIGN KEY (char_id) REFERENCES characters(char_id) ON DELETE CASCADE,
    FOREIGN KEY (item_id) REFERENCES items(item_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
