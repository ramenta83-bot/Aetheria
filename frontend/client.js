(() => {
  const $ = (id) => document.getElementById(id);
  const connection = $("connection");
  const authPanel = $("authPanel");
  const charPanel = $("charPanel");
  const game = $("game");
  const logBox = $("log");
  let socket = null, character = "", stage = null, authMode = "login";

  function socketUrl() {
    if (["localhost", "127.0.0.1"].includes(location.hostname)) return `ws://${location.hostname}:8765`;
    return `${location.protocol === "https:" ? "wss:" : "ws:"}//${location.host}/ws`;
  }

  function setConnection(ok, message) {
    connection.textContent = ok ? "● CONNECTED" : "● DISCONNECTED";
    connection.className = `connection ${ok ? "connected" : "disconnected"}`;
    if (message) addLog(message, ok ? "system" : "error");
  }

  function addLog(message, style = "") {
    const p = document.createElement("p");
    if (["system", "combat", "error"].includes(style)) p.className = style;
    p.textContent = String(message ?? "");
    logBox.appendChild(p);
    logBox.scrollTop = logBox.scrollHeight;
  }

  function sendPayload(obj) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      $("authError").textContent = "Not connected to server. Refresh the page.";
      return;
    }
    socket.send(JSON.stringify(obj));
  }

  function updateVitals(data) {
    if (data.name) character = data.name;
    $("statName").textContent = character || "—";
    $("statGuild").textContent = data.guild ?? "—";
    $("statRank").textContent = data.rank ?? "—";
    const hp = Number(data.hp) || 0, maxHp = Math.max(1, Number(data.max_hp) || 1);
    const res = Number(data.resource) || 0, maxRes = Math.max(1, Number(data.max_resource) || 1);
    $("statHp").textContent = `${hp} / ${maxHp}`;
    $("hpBar").style.width = `${Math.max(0, Math.min(100, (hp / maxHp) * 100))}%`;
    $("statResource").textContent = `${res} / ${maxRes}`;
    $("resourceBar").style.width = `${Math.max(0, Math.min(100, (res / maxRes) * 100))}%`;
    $("statKronars").textContent = data.kronars ?? 0;
  }

  function renderCharacterList(characters) {
    const list = $("charList");
    list.innerHTML = "";
    if (!characters || !characters.length) {
      list.innerHTML = `<p>No characters found on this account. Create one below to enter Aetheria.</p>`;
      return;
    }
    characters.forEach((c) => {
      const row = document.createElement("div");
      row.className = "char-row";
      row.innerHTML = `<div><strong>${c.name}</strong><div class="small">${c.guild_name || c.guild_id} · Rank ${c.rank}</div></div><button type="button">Play</button>`;
      row.querySelector("button").addEventListener("click", () => sendPayload({ action: "select_character", name: c.name }));
      list.appendChild(row);
    });
  }

  function handleMessage(raw) {
    let data;
    try { data = JSON.parse(raw); } catch { addLog(raw); return; }
    switch (data.type) {
      case "auth_error": $("authError").textContent = data.message || "Authentication failed."; break;
      case "auth_ok":
        $("authError").textContent = "";
        authPanel.hidden = true;
        charPanel.hidden = false;
        $("accountBanner").textContent = data.username || "Adventurer";
        renderCharacterList(data.characters);
        break;
      case "char_error": $("charError").textContent = data.message || "Character error."; break;
      case "char_list": $("charError").textContent = ""; renderCharacterList(data.characters); break;
      case "char_select":
        game.hidden = true;
        charPanel.hidden = false;
        logBox.innerHTML = "";
        renderCharacterList(data.characters);
        break;
      case "enter_world":
        character = data.character || character;
        charPanel.hidden = true;
        game.hidden = false;
        if (!stage && typeof AsciiStagePlayer !== "undefined") stage = new AsciiStagePlayer("animation", "ambient");
        $("command").focus();
        break;
      case "text": addLog(data.text, data.style); break;
      case "vitals": updateVitals(data); break;
      case "room":
        $("roomTitle").textContent = data.title || "Unknown location";
        $("roomDescription").textContent = data.description || "";
        $("entities").textContent = data.entities || "";
        $("roomExits").textContent = data.exits || "none";
        if (stage) stage.startAmbient(data.ambient || "marsh");
        break;
      case "anim": if (stage) stage.play(data.effect, data.speed); break;
    }
  }

  socket = new WebSocket(socketUrl());
  socket.addEventListener("open", () => setConnection(true));
  socket.addEventListener("message", (e) => handleMessage(e.data));
  socket.addEventListener("error", () => setConnection(false));
  socket.addEventListener("close", () => setConnection(false, "Connection closed. Refresh to reconnect."));

  $("tabLogin").addEventListener("click", () => {
    authMode = "login";
    $("tabLogin").classList.add("active");
    $("tabRegister").classList.remove("active");
    $("authSubmitBtn").textContent = "Log In";
    $("authError").textContent = "";
  });

  $("tabRegister").addEventListener("click", () => {
    authMode = "register";
    $("tabRegister").classList.add("active");
    $("tabLogin").classList.remove("active");
    $("authSubmitBtn").textContent = "Create Account";
    $("authError").textContent = "";
  });

  $("authForm").addEventListener("submit", (e) => {
    e.preventDefault();
    $("authError").textContent = "";
    sendPayload({ action: authMode, username: $("authUsername").value.trim(), password: $("authPassword").value });
  });

  $("createCharForm").addEventListener("submit", (e) => {
    e.preventDefault();
    $("charError").textContent = "";
    sendPayload({ action: "create_character", name: $("newCharName").value.trim(), guild: $("newCharGuild").value });
    $("newCharName").value = "";
  });

  $("commandForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const field = $("command"), command = field.value.trim();
    if (!command) return;
    addLog(`> ${command}`);
    sendPayload({ command });
    field.value = "";
    field.focus();
  });
})();
