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
    "  *  \\o/  *  (Foe Defeated!)",
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
  constructor(stageElementId, ambientElementId) {
    this.stage = document.getElementById(stageElementId);
    this.ambientStage = document.getElementById(ambientElementId);
    this.timer = null;
    this.ambientTimer = null;
  }

  startAmbient(effectName, speedMs = 900) {
    const frames = ASCII_ANIMATIONS[effectName];
    if (!frames || !this.ambientStage) return;

    clearInterval(this.ambientTimer);
    let idx = 0;
    this.ambientStage.textContent = frames[0];

    if (frames.length > 1) {
      this.ambientTimer = setInterval(() => {
        idx = (idx + 1) % frames.length;
        this.ambientStage.textContent = frames[idx];
      }, speedMs);
    }
  }

  play(effectName, speedMs = 110) {
    const frames = ASCII_ANIMATIONS[effectName];
    if (!frames || !this.stage) return;

    clearInterval(this.timer);
    let idx = 0;
    this.stage.textContent = frames[0];

    this.timer = setInterval(() => {
      idx++;
      if (idx < frames.length) {
        this.stage.textContent = frames[idx];
      } else {
        clearInterval(this.timer);
        setTimeout(() => {
          if (this.stage) this.stage.textContent = "";
        }, 600);
      }
    }, speedMs);
  }
}

window.AsciiStagePlayer = AsciiStagePlayer;
window.ASCII_ANIMATIONS = ASCII_ANIMATIONS;
