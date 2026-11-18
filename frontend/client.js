(function () {
  const outputEl = document.getElementById("terminal-output");
  const formEl = document.getElementById("command-form");
  const inputEl = document.getElementById("command-input");
  const statusEl = document.getElementById("conn-status");

  const hudClass = document.getElementById("hud-class");
  const hudRank = document.getElementById("hud-rank");
  const hudHp = document.getElementById("hud-hp");
  const hudRes = document.getElementById("hud-res");
  const hudGold = document.getElementById("hud-gold");
  const hudRt = document.getElementById("hud-rt");

  const stagePlayer = typeof AsciiStagePlayer !== "undefined"
    ? new AsciiStagePlayer("ascii-stage", "ambient-stage")
    : null;

  const isLocal = ["localhost", "127.0.0.1", ""].includes(window.location.hostname);
  const wsUrl = isLocal
    ? "ws://localhost:8765"
    : `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws`;

  let socket = null;
  let recoveryInterval = null;

  function appendLine(text, className = "log-line") {
    const div = document.createElement("div");
    div.className = className;
    div.textContent = text;
    outputEl.appendChild(div);
    outputEl.scrollTop = outputEl.scrollHeight;
  }

  function startRecoveryCountdown(seconds) {
    clearInterval(recoveryInterval);
    let remaining = Math.ceil(seconds);
    if (remaining <= 0) {
      hudRt.textContent = "READY";
      hudRt.className = "vital-value ready";
      return;
    }
    hudRt.textContent = `${remaining}s`;
    hudRt.className = "vital-value locked";

    recoveryInterval = setInterval(() => {
      remaining -= 1;
      if (remaining <= 0) {
        clearInterval(recoveryInterval);
        hudRt.textContent = "READY";
        hudRt.className = "vital-value ready";
      } else {
        hudRt.textContent = `${remaining}s`;
      }
    }, 1000);
  }

  function updateVitals(data) {
    if (data.guild) hudClass.textContent = data.guild.toUpperCase();
    if (data.rank !== undefined) hudRank.textContent = data.rank;
    if (data.hp !== undefined && data.max_hp !== undefined) {
      hudHp.textContent = `${data.hp}/${data.max_hp}`;
    }
    if (data.resource !== undefined && data.max_resource !== undefined) {
      hudRes.textContent = `${data.resource}/${data.max_resource}`;
    }
    if (data.kronars !== undefined) hudGold.textContent = data.kronars;
    if (data.recovery !== undefined) startRecoveryCountdown(data.recovery);
  }

  function connect() {
    appendLine("Connecting to Aetheria Web MUD server...", "log-system");
    socket = new WebSocket(wsUrl);

    socket.addEventListener("open", () => {
      statusEl.textContent = "CONNECTED";
      statusEl.className = "conn-badge connected";
      appendLine("Connection established. Type a character name or 'help' to begin.", "log-system");
    });

    socket.addEventListener("message", (event) => {
      let payload;
      try {
        payload = JSON.parse(event.data);
      } catch {
        appendLine(event.data);
        return;
      }

      if (payload.type === "text") {
        const style = payload.style ? `log-line log-${payload.style}` : "log-line";
        appendLine(payload.text, style);
      } else if (payload.type === "room") {
        appendLine(`
[${payload.title}]`, "log-room-title");
        appendLine(payload.description, "log-line");
        if (payload.entities) appendLine(payload.entities, "log-line");
        if (payload.exits) appendLine(`Obvious paths: ${payload.exits}`, "log-line");
        if (payload.ambient && stagePlayer) {
          stagePlayer.startAmbient(payload.ambient);
        }
      } else if (payload.type === "anim" && stagePlayer) {
        stagePlayer.play(payload.effect, payload.speed || 110);
      } else if (payload.type === "vitals") {
        updateVitals(payload);
      }
    });

    socket.addEventListener("close", () => {
      statusEl.textContent = "DISCONNECTED";
      statusEl.className = "conn-badge disconnected";
      appendLine("Disconnected from server. Refresh the page to reconnect.", "log-system");
    });
  }

  formEl.addEventListener("submit", (e) => {
    e.preventDefault();
    const cmd = inputEl.value.trim();
    if (!cmd) return;
    appendLine(`> ${cmd}`, "log-echo");
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ command: cmd }));
    } else {
      appendLine("Not connected to server.", "log-system");
    }
    inputEl.value = "";
  });

  connect();
})();
