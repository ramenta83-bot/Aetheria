/* Lightweight ASCII ambience and combat effects for the Aetheria browser client. */
class AsciiStagePlayer {
  constructor(stageId, ambientId) {
    this.stageEl = document.getElementById(stageId);
    this.ambientEl = document.getElementById(ambientId);
    this.ambientTimer = null;
    this.animTimer = null;
    this.clearTimer = null;
    this.ambients = {
      marsh: [
        "~ . ~      THE WHISPERING FEN   ~ * ~\n (o)     mist drifts across black water...",
        " ~ * ~       THE WHISPERING FEN   ~ . ~\n   (o) mist drifts across black water..."
      ],
      sanctuary: [
        "[*]=== AETHERIA GUILD SANCTUARY ===[*]\n  | Safe Zone: Type 'train' or 'shop' |",
        "[+]=== AETHERIA GUILD SANCTUARY ===[+]\n  | Safe Zone: Type 'train' or 'shop' |"
      ]
    };
    this.effects = {
      chaos_bolt: ["   ( * ) -->", "           ==> ( @ ) -->", "                     ===> [ *BOOM* ]", "                               . * + ."],
      melee_slash: ["      \\", "       \\ /", "        ><    *CLANG!*", "       / \\"],
      companion: ["   /\\_/\\    Companion lunges forward!", " ( >.< ) ==> *CHOMP!*"]
    };
  }
  startAmbient(key) {
    clearInterval(this.ambientTimer);
    const frames = this.ambients[key] || this.ambients.marsh;
    let idx = 0;
    if (this.ambientEl) this.ambientEl.textContent = frames[0];
    this.ambientTimer = setInterval(() => {
      idx = (idx + 1) % frames.length;
      if (this.ambientEl) this.ambientEl.textContent = frames[idx];
    }, 1200);
  }
  play(effectName, speed = 110) {
    clearInterval(this.animTimer);
    clearTimeout(this.clearTimer);
    const frames = this.effects[effectName] || this.effects.melee_slash;
    let idx = 0;
    if (this.stageEl) this.stageEl.textContent = frames[0];
    this.animTimer = setInterval(() => {
      idx += 1;
      if (idx >= frames.length) {
        clearInterval(this.animTimer);
        this.clearTimer = setTimeout(() => {
          if (this.stageEl) this.stageEl.textContent = "";
        }, 600);
      } else if (this.stageEl) {
        this.stageEl.textContent = frames[idx];
      }
    }, Math.max(30, Number(speed) || 110));
  }
}
