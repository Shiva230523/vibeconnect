let socket;

let partnerNickname = null;
let partnerUserId = null;

let msgCount = 0;
let iClicked = false;
let partnerClicked = false;

const messages = document.getElementById("messages");
const statusEl = document.getElementById("status");
const partnerInfo = document.getElementById("partnerInfo");

const msgInput = document.getElementById("msgInput");
const sendBtn = document.getElementById("sendBtn");

const skipBtn = document.getElementById("skipBtn");
const interestedBtn = document.getElementById("interestedBtn");

const saveForm = document.getElementById("saveForm");
const saveUserId = document.getElementById("saveUserId");
const saveNick = document.getElementById("saveNick");

function addMessage(name, text) {
  const div = document.createElement("div");
  div.className = "msg";
  div.innerHTML = `<b>${name}:</b> ${text}`;
  messages.appendChild(div);

  // ✅ keep last 5 visible
  while (messages.children.length > 5) {
    messages.removeChild(messages.firstChild);
  }

  messages.scrollTop = messages.scrollHeight;
}

function systemMessage(text) {
  addMessage("System", text);
}

function resetChatUI() {
  msgCount = 0;
  iClicked = false;
  partnerClicked = false;

  if (!window.IS_GUEST && interestedBtn) {
    interestedBtn.disabled = true;
    interestedBtn.textContent = "Interested (unlock after 5 messages)";
  }
}

function saveConnection() {
  if (!saveForm || !saveUserId || !saveNick) return;
  if (!partnerUserId || !partnerNickname) return;

  saveUserId.value = partnerUserId;
  saveNick.value = partnerNickname;
  saveForm.submit();
}

function connectSocket() {
  // socket = new WebSocket(`ws://${window.location.host}/ws/chat/`);
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  socket = new WebSocket(`${protocol}://${window.location.host}/ws/chat/`);

  socket.onopen = () => {
    statusEl.textContent = "Connected ✅";
    partnerInfo.textContent = "Finding match...";
  };

  socket.onmessage = (event) => {
    const raw = (event.data || "").toString();
    const parts = raw.split("|");
    const type = (parts[0] || "").trim();

    if (type === "SYS") {
      systemMessage(parts.slice(1).join("|"));
      return;
    }

    if (type === "MATCH") {
      resetChatUI();
      messages.innerHTML = "";

      partnerNickname = parts[1] || "Unknown";
      partnerUserId = parts[2] || "";

      partnerInfo.textContent = `Matched with: ${partnerNickname}`;
      systemMessage(`You are chatting with ${partnerNickname}.`);
      return;
    }

    if (type === "MSG") {
      const nickname = parts[1] || "Unknown";
      const message = parts.slice(2).join("|");

      addMessage(nickname, message);

      msgCount++;

      if (!window.IS_GUEST && interestedBtn && msgCount >= 5) {
        interestedBtn.disabled = false;
        interestedBtn.textContent = "Interested";
      }
      return;
    }

    if (type === "PINTEREST") {
      partnerClicked = true;
      systemMessage("Partner clicked Interested.");

      if (!window.IS_GUEST && iClicked && partnerClicked) {
        systemMessage("✅ Mutual Interested! Saving connection...");
        saveConnection();
      }
      return;
    }
  };

  socket.onclose = () => {
    statusEl.textContent = "Disconnected ❌ (refresh page)";
    partnerInfo.textContent = "";
  };
}

// Send message
sendBtn.addEventListener("click", () => {
  const msg = msgInput.value.trim();
  if (!msg) return;

  socket.send(`MSG|${msg}`);
  msgInput.value = "";
});

msgInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendBtn.click();
});

// Skip / Next
skipBtn.addEventListener("click", () => {
  // ✅ if I skip after interested: end chat
  resetChatUI();
  messages.innerHTML = "";
  partnerInfo.textContent = "Finding match...";
  socket.send("NEXT|");
});

if (interestedBtn) {
  interestedBtn.addEventListener("click", () => {
    if (msgCount < 5) return;

    iClicked = true;
    interestedBtn.disabled = true;
    interestedBtn.textContent = "Interested ✓";

    socket.send("INTEREST|");

    // if other already clicked
    if (partnerClicked) {
      systemMessage("✅ Mutual Interested! Saving connection...");
      saveConnection();
    }
  });
}

connectSocket();
