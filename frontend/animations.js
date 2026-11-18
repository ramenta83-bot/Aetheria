/**
 * Real-Time ASCII Animation Pack (animations.js)
 * Includes:
 * - All 7 Class Combat & Utility Animations
 * - Active Companion Attack Effects
 * - Boss Encounter & Loot Chest Sequences
 * - Weather Cycles & Ambient Room Banners
 */

const ASCII_ANIMATIONS = {
  // --- AMBIENT ROOM & WEATHER LOOPS ---
  astral_twinkle: [
    "  *    .      (   )      .    *   [The Astral Sanctum]",
    "    .    *    ( O )    *    .     [The Astral Sanctum]",
    "  *    .      (   )      .    *   [The Astral Sanctum]"
  ],
  swamp_mist: [
    "  ~  _.._   ~    ~  _.._   ~      [The Whispering Fen]",
    "   ~  _.._   ~    ~  _.._   ~     [The Whispering Fen]",
    "    ~  _.._   ~    ~  _.._   ~    [The Whispering Fen]"
  ],
  town_lanterns: [
    "  [i]=====[i]   Oakhaven Crossroads   [i]=====[i]",
    "  [*]=====[*]   Oakhaven Crossroads   [*]=====[*]"
  ],
  forge_sparks: [
    "  (Flame)  .  *    Elemental Conclave    *  .  (Frost)",
    "  (Flame)    *  .  Elemental Conclave  .  *    (Frost)"
  ],
  arena_dust: [
    "  /\\  --==[ Bloodstone Arena ]==--  /\\",
    "  \\/  --==[ Bloodstone Arena ]==--  \\/"
  ],
  radiant_motes: [
    "  +  .  *  Sanctified Grounds  *  .  +",
    "  .  *  +  Sanctified Grounds  +  *  ."
  ],
  forest_breeze: [
    "  ) ) )  Whispering Canopy  ( ( (",
    "   ) ) ) Whispering Canopy ( ( ("
  ],
  candle_flicker: [
    "  (,)  The Velvet Coin  (,)",
    "  (*)  The Velvet Coin  (*)"
  ],

  // --- WEATHER CYCLES ---
  weather_rain: [
    "  /  /  /  /  /  /  /  /  /  /  /  /",
    "   /  /  /  /  /  /  /  /  /  /  /  ",
    "    /  /  /  /  /  /  /  /  /  /  / "
  ],
  weather_lightning: [
    "        _/                 ",
    "       _/   \\_             ",
    "      _/      \\_   *CRACK* ",
    "                 \\_        "
  ],

  // --- 7 CLASS COMBAT & UTILITY ANIMATIONS ---
  chaos_bolt: [
    "  (o) *~                      [Target]",
    "  (o)   *~#~                  [Target]",
    "  (o)       *~#@#~*           [Target]",
    "  (o)               \\*BOOM*/  [Target]"
  ],
  astral_veil: [
    "   .  (o)  .   ",
    "  * : (o) : *  ",
    "  ~ # (o) # ~  (Shrouded in Starlight)"
  ],
  entropy_shackle: [
    "  [Target]  . . . ",
    "  [Target] (=====)",
    "  [Target] [#===#] (Locked in Recovery!)"
  ],
  flame_arc: [
    "  (o)==/    )           [Target]",
    "  (o)==---  )) ))       [Target]",
    "  (o)==\\     ))) *SEAR* [Target]"
  ],
  summon_ember_hound: [
    "        ( )         ",
    "       ( { )        ",
    "      /^^\\_  *GRRR* (Ember Hound Bound!)"
  ],
  frost_aegis: [
    "   *  (o)  *  ",
    "  <*> (o) <*> ",
    "  [=] (o) [=] (Frost Aegis Active)"
  ],
  lifesteal_cleave: [
    "  [You]   /           [Foe]",
    "  [You]  ---===>>>    [Foe]",
    "  [You]  <++ + ++     [Foe] (Vitality Siphoned!)"
  ],
  blood_howl: [
    "  (o)  !        ",
    "  (o)  !)) )))  ",
    "  (o)  !))) *ROAR* (+Attack Power)"
  ],
  radiant_mend: [
    "      \\ | /     ",
    "    -- (o) --   ",
    "      / | \\  (+Health Restored)"
  ],
  smite_blight: [
    "         |      [Target]",
    "         |      [Target]",
    "       \\*|*/    [Target] (*PURIFIED*)"
  ],
  sacred_ward: [
    "     .-----.    ",
    "    /  (o)  \\   ",
    "   |   (o)   |  (Sacred Ward Erected)"
  ],
  piercing_shot: [
    "  (o)D  -->             [Target]",
    "  (o)D        -->       [Target]",
    "  (o)D              -->*[Target] (*CRIT*)"
  ],
  call_timber_wolf: [
    "     . . .          ",
    "    /\\_/\\  *HOWL*   ",
    "   ( o.o )> (Timber Wolf Joins You!)"
  ],
  briar_snare: [
    "  [Target]  ,,,     ",
    "  [Target] \\|//    ",
    "  [Target] {#|#|} (Entangled!)"
  ],
  sunfire_strike: [
    "  (o)==|      [Target]",
    "  (o)==*===>  [Target]",
    "  (o)==|    \\*BLAZE*/ [Target]"
  ],
  aura_of_resolve: [
    "   .  (o)  .  ",
    "  ( * (o) * ) ",
    " (( * (o) * )) (Aura of Resolve)"
  ],
  viper_ambush: [
    "  ...         [Target]",
    "      (o)-/   [Target]",
    "          (o)X[Target] (*BACKSTAB*)"
  ],
  smoke_screen: [
    "     ( * )    ",
    "   ( ~ ~ ~ )  ",
    "  ( ~ ~ ~ ~ ) (Vanished in Smoke)"
  ],
  venom_coat: [
    "  --===>  .   ",
    "  --===>  o   ",
    "  --===> ~*~  (Blade Envenomed)"
  ],

  // --- COMPANION, BOSS & LOOT EFFECTS ---
  melee_slash: [
    "  [You]   /       [Foe]",
    "  [You]  ---===X  [Foe]"
  ],
  pet_bite: [
    "  [Companion]  ~>     [Foe]",
    "  [Companion]    *SNAP*[Foe]"
  ],
  victory_spark: [
    "    .  *  .   ",
    "  *  \o/  *  (Foe Defeated!)",
    "    .  *  .   "
  ],
  boss_roar: [
    "  [=== BOG BEHEMOTH ===]   !       ",
    "  [=== BOG BEHEMOTH ===]   !)) ))) ",
    "  [=== BOG BEHEMOTH ===]   !))) *EARTHQUAKE*"
  ],
  loot_chest_open: [
    "     _______     ",
    "    /      /|    ",
    "   +------+ |    ",
    "   |  ==  | /    ",
    "   +------+/     ",
    "     _______     ",
    "    /  * * /|    ",
    "   +------+ |  *TREASURE UNLOCKED!*",
    "   | * $$ | /    ",
    "   +------+/     "
  ]
};

class AsciiStagePlayer {
  constructor(stageElementId) {
    this.stage = document.getElementById(stageElementId);
    this.timer = null;
    this.ambientFrames = null;
    this.ambientIndex = 0;
  }

  play(effectName, speedMs = 110) {
    const frames = ASCII_ANIMATIONS[effectName];
    if (!frames || !this.stage) return;

    // If effect is an ambient room loop, store it as the idle background banner
    if (effectName.startsWith("astral_") || effectName.startsWith("swamp_") ||
        effectName.startsWith("town_") || effectName.startsWith("forge_") ||
        effectName.startsWith("arena_") || effectName.startsWith("radiant_") ||
        effectName.startsWith("forest_") || effectName.startsWith("candle_")) {
      this.ambientFrames = frames;
      this.ambientIndex = 0;
    }

    clearInterval(this.timer);
    let idx = 0;
    this.stage.textContent = frames[0];

    this.timer = setInterval(() => {
      idx++;
      if (idx < frames.length) {
        this.stage.textContent = frames[idx];
      } else if (this.ambientFrames) {
        this.ambientIndex = (this.ambientIndex + 1) % this.ambientFrames.length;
        this.stage.textContent = this.ambientFrames[this.ambientIndex];
      } else {
        clearInterval(this.timer);
      }
    }, speedMs);
  }
}

window.AsciiStagePlayer = AsciiStagePlayer;
window.ASCII_ANIMATIONS = ASCII_ANIMATIONS;
