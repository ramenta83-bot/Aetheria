const wsProto = location.protocol === "https:" ? "wss" : "ws";
const ws = new WebSocket(`${wsProto}://${location.host}/ws`);

let authMode = "login";

const statusText = document.getElementById("status-text");
const statusDot = document.getElementById("status-dot");
const authPanel = document.getElementById("auth-panel");
const charPanel = document.getElementById("char-select-panel");
const gamePanel = document.getElementById("game-panel");

ws.onopen = () => {
  statusText.textContent = "CONNECTED";
  statusDot.style.color = "#4ade80";
};

ws.onclose = () => {
  statusText.textContent = "DISCONNECTED";
  statusDot.style.color = "#f87171";
};

document.getElementById("tab-login").onclick = () => {
  authMode = "login";
  document.getElementById("tab-login").classList.add("active");
  document.getElementById("tab-register").classList.remove("active");
  document.getElementById("auth-submit").textContent = "Log In";
  document.getElementById("auth-error").textContent = "";
};

document.getElementById("tab-register").onclick = () => {
  authMode = "register";
  document.getElementById("tab-register").classList.add("active");
  document.getElementById("tab-login").classList.remove("active");
  document.getElementById("auth-submit").textContent = "Create Account";
  document.getElementById("auth-error").textContent = "";
};

document.getElementById("auth-form").onsubmit = (e) => {
  e.preventDefault();
  ws.send(JSON.stringify({
    action: authMode,
    username: document.getElementById("auth-user").value,
    password: document.getElementById("auth-pass").value,
  }));
};

document.getElementById("create-char-form").onsubmit = (e) => {
  e.preventDefault();
  const input = document.getElementById("new-char-name");
  ws.send(JSON.stringify({ action: "create_character", name: input.value }));
  input.value = "";
};

document.getElementById("cmd-form").onsubmit = (e) => {
  e.preventDefault();
  const input = document.getElementById("cmd-input");
  if (!input.value.trim()) return;
  ws.send(JSON.stringify({ command: input.value }));
  input.value = "";
};

function renderCharacterList(characters) {
  const list = document.getElementById("char-list");
  list.innerHTML = "";
  if (!characters.length) {
    list.innerHTML = `<p class="muted">No characters yet. Create one below to begin.</p>`;
    return;
  }
  characters.forEach((c) => {
    const row = document.createElement("div");
    row.className = "char-row";
    row.innerHTML = `
      <div>
        <strong>${c.name}</strong>
        <span class="muted"> — ${c.guild_id || "Unguilded"} (Rank ${c.rank})</span>
      </div>
      <button type="button">Enter Aetheria</button>
    `;
    row.querySelector("button").onclick = () => {
      ws.send(JSON.stringify({ action: "select_character", name: c.name }));
    };
    list.appendChild(row);
  });
}

function appendLog(text, style = "system") {
  const log = document.getElementById("chronicle");
  const line = document.createElement("div");
  line.className = `log-line log-${style}`;
  line.textContent = text;
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);

  if (msg.type === "auth_error") {
    document.getElementById("auth-error").textContent = msg.message;
  } else if (msg.type === "auth_ok") {
    authPanel.classList.add("hidden");
    charPanel.classList.remove("hidden");
    document.getElementById("logged-in-user").textContent = msg.username;
    renderCharacterList(msg.characters);
  } else if (msg.type === "char_error") {
    document.getElementById("char-error").textContent = msg.message;
  } else if (msg.type === "char_list") {
    document.getElementById("char-error").textContent = "";
    renderCharacterList(msg.characters);
  } else if (msg.type === "enter_world") {
    charPanel.classList.add("hidden");
    gamePanel.classList.remove("hidden");
  } else if (msg.type === "state") {
    document.getElementById("hud-name").textContent = msg.player.name;
    document.getElementById("hud-guild").textContent = msg.player.guild;
    document.getElementById("hud-rank").textContent = msg.player.rank;
    document.getElementById("hud-hp").textContent = `${msg.player.hp} / ${msg.player.max_hp}`;
    document.getElementById("hud-res").textContent = `${msg.player.resource} / ${msg.player.max_resource}`;
    document.getElementById("hud-kronars").textContent = msg.player.kronars;

    document.getElementById("room-name").textContent = msg.room.name;
    document.getElementById("room-desc").textContent = msg.room.description;
    document.getElementById("room-exits").textContent = msg.room.exits;
  } else if (msg.type === "log") {
    appendLog(msg.text, msg.style);
  }
};
