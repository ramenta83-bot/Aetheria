/* Browser client for the JSON message protocol in the supplied Aetheria server.py guide. */
(() => {
  const $ = (id) => document.getElementById(id);
  const connection = $("connection");
  const loginPanel = $("loginPanel");
  const game = $("game");
  const loginForm = $("loginForm");
  const commandForm = $("commandForm");
  const logBox = $("log");
  let socket = null;
  let character = "";
  let stage = null;

  function socketUrl() {
    const local = ["localhost", "127.0.0.1"].includes(location.hostname);
    if (local) return `ws://${location.hostname}:8765`;
    const scheme = location.protocol === "https:" ? "wss:" : "ws:";
    return `${scheme}//${location.host}/ws`;
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
  function sendCommand(command) {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      addLog("Not connected. Refresh the page and try again.", "error");
      return;
    }
    socket.send(JSON.stringify({ command }));
  }
  function updateVitals(data) {
    $("statName").textContent = character || "—";
    $("statGuild").textContent = data.guild ?? "—";
    $("statRank").textContent = data.rank ?? "—";
    const hp = Number(data.hp) || 0, maxHp = Math.max(1, Number(data.max_hp) || 1);
    const resource = Number(data.resource) || 0, maxResource = Math.max(1, Number(data.max_resource) || 1);
    $("statHp").textContent = `${hp} / ${maxHp}`;
    $("hpBar").style.width = `${Math.max(0, Math.min(100, hp / maxHp * 100))}%`;
    $("statResource").textContent = `${resource} / ${maxResource}`;
    $("resourceBar").style.width = `${Math.max(0, Math.min(100, resource / maxResource * 100))}%`;
    $("statKronars").textContent = data.kronars ?? 0;
  }
  function handleMessage(raw) {
    let data;
    try { data = JSON.parse(raw); } catch { addLog(raw); return; }
    switch (data.type) {
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
      default: addLog(`Unrecognized server message: ${raw}`);
    }
  }
  function connect(name) {
    character = name.trim().slice(0, 20);
    if (!character) return;
    try { socket = new WebSocket(socketUrl()); }
    catch (err) { setConnection(false, `Could not create WebSocket: ${err.message}`); return; }
    socket.addEventListener("open", () => {
      setConnection(true, "Connection established. Entering the realm…");
      loginPanel.hidden = true;
      game.hidden = false;
      stage = new AsciiStagePlayer("animation", "ambient");
      sendCommand(character);
      $("command").focus();
    });
    socket.addEventListener("message", (event) => handleMessage(event.data));
    socket.addEventListener("error", () => setConnection(false, "WebSocket connection error."));
    socket.addEventListener("close", () => setConnection(false, "Connection closed. Refresh to reconnect."));
  }
  loginForm.addEventListener("submit", (event) => {
    event.preventDefault();
    connect($("characterName").value);
  });
  commandForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const field = $("command");
    const command = field.value.trim();
    if (!command) return;
    addLog(`> ${command}`);
    sendCommand(command);
    field.value = "";
    field.focus();
  });
})();
