const userIdInput = document.querySelector("#userId");
const nicknameInput = document.querySelector("#nickname");
const commandInput = document.querySelector("#commandInput");
const commandForm = document.querySelector("#commandForm");
const textOutput = document.querySelector("#textOutput");
const cardWrap = document.querySelector("#cardWrap");
const summary = document.querySelector("#summary");
let selectedSect = "华山";
let selectedDifficulty = "普通";

userIdInput.value = localStorage.getItem("jy-web-user-id") || userIdInput.value;
nicknameInput.value = localStorage.getItem("jy-web-nickname") || nicknameInput.value;

async function sendCommand(text) {
  localStorage.setItem("jy-web-user-id", userIdInput.value.trim());
  localStorage.setItem("jy-web-nickname", nicknameInput.value.trim());
  const response = await fetch("/api/command", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      userId: userIdInput.value.trim(),
      nickname: nicknameInput.value.trim(),
      text,
    }),
  });
  const data = await response.json();
  renderResult(data);
}

function renderResult(data) {
  cardWrap.innerHTML = "";
  if (data.imageUrl) {
    const image = document.createElement("img");
    image.src = `${data.imageUrl}?t=${Date.now()}`;
    image.alt = "游戏卡片";
    cardWrap.appendChild(image);
    textOutput.hidden = true;
    textOutput.textContent = "";
  } else {
    textOutput.hidden = false;
    textOutput.textContent = data.text || "";
  }
  renderSummary(data.player);
}

function renderSummary(player) {
  if (!player) {
    summary.textContent = "未载入角色";
    return;
  }
  const flags = [];
  if (player.inCombat) flags.push("战斗中");
  if (player.inTrap) flags.push("陷阱中");
  if (player.finished) flags.push("已通关");
  if (player.frozen) flags.push("已冻结");
  if (player.gameOver) flags.push("已结算");
  summary.innerHTML = [
    `<strong>${escapeHtml(player.nickname || "侠客")}</strong>`,
    `${escapeHtml(player.sect || "-")} / ${escapeHtml(player.difficulty || "-")} / Lv${player.level || 1}`,
    `第${player.floor || 1}层，已开门 ${player.openedDoors || 0}`,
    `HP ${player.hp || 0}/${player.maxHp || 0} · MP ${player.mp || 0}/${player.maxMp || 0} · 碎银 ${player.silver || 0} · 护命丹 ${player.reviveElixirs || 0}`,
    flags.length ? flags.join(" · ") : "可行动",
  ].join("<br>");
  renderMetaActions(player.metaUnlockItems || []);
  if (player.finished || player.frozen || player.gameOver) return;
  renderUsableItems(player.usableItems || []);
  renderEquipmentItems(player.equipmentItems || []);
  renderMerchantItems(player.merchantItems || [], player.merchantLeaveCommand || "");
  renderSkillItems(player.skillItems || []);
  renderLearnableSkills(player.learnableSkills || []);
}

function renderMetaActions(unlockItems = []) {
  const existing = summary.querySelector(".quick-meta");
  if (existing) existing.remove();

  const wrap = document.createElement("div");
  wrap.className = "quick-meta";
  const title = document.createElement("div");
  title.className = "quick-meta-title";
  title.textContent = "局外快捷";
  wrap.appendChild(title);

  [
    ["查看", "/金庸局外"],
    ["绝学", "/金庸绝学"],
    ["丹0", "/金庸小还丹 0"],
    ["丹1", "/金庸小还丹 1"],
    ["丹2", "/金庸小还丹 2"],
    ["丹3", "/金庸小还丹 3"],
    ["钓鱼", "/金庸强化 钓鱼"],
    ["背囊", "/金庸强化 背囊"],
    ["盘缠", "/金庸强化 盘缠"],
    ["气血", "/金庸强化 气血"],
    ["丹+", "/金庸强化 小还丹"],
  ].forEach(([label, command]) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.addEventListener("click", () => sendQuickCommand(command));
    wrap.appendChild(button);
  });

  unlockItems.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = `解 ${item.label}`;
    button.addEventListener("click", () => sendQuickCommand(item.command));
    wrap.appendChild(button);
  });

  summary.appendChild(wrap);
}

function renderUsableItems(items) {
  const existing = summary.querySelector(".quick-use");
  if (existing) existing.remove();
  if (!items.length) return;

  const wrap = document.createElement("div");
  wrap.className = "quick-use";
  const title = document.createElement("div");
  title.className = "quick-use-title";
  title.textContent = "物品快捷";
  wrap.appendChild(title);

  items.forEach((item) => {
    const itemWrap = document.createElement("div");
    itemWrap.className = "quick-use-item";

    const label = document.createElement("span");
    label.textContent = `${item.name} x${item.quantity}`;
    itemWrap.appendChild(label);

    if (item.actionCommand) {
      const actionButton = document.createElement("button");
      actionButton.type = "button";
      actionButton.textContent = item.actionLabel || "用";
      actionButton.addEventListener("click", () => sendQuickCommand(item.actionCommand));
      itemWrap.appendChild(actionButton);
    }

    const viewButton = document.createElement("button");
    viewButton.type = "button";
    viewButton.textContent = "看";
    viewButton.addEventListener("click", () => sendQuickCommand(item.viewCommand));
    itemWrap.appendChild(viewButton);

    if (item.sellableQuantity > 0 && item.sellCommand) {
      const sellButton = document.createElement("button");
      sellButton.type = "button";
      sellButton.textContent = "卖";
      sellButton.title = `出售数量：${item.sellableQuantity}`;
      sellButton.addEventListener("click", () => sendQuickCommand(item.sellCommand));
      itemWrap.appendChild(sellButton);
    }

    wrap.appendChild(itemWrap);
  });
  summary.appendChild(wrap);
}

function renderEquipmentItems(items) {
  const existing = summary.querySelector(".quick-equipment");
  if (existing) existing.remove();
  if (!items.length) return;

  const wrap = document.createElement("div");
  wrap.className = "quick-equipment";
  const title = document.createElement("div");
  title.className = "quick-equipment-title";
  title.textContent = "装备快捷";
  wrap.appendChild(title);

  items.forEach((item) => {
    const itemWrap = document.createElement("div");
    itemWrap.className = `quick-equipment-item${item.active ? " is-active" : ""}`;

    const label = document.createElement("span");
    label.textContent = `${item.active ? "★ " : ""}${item.name} x${item.quantity}`;
    itemWrap.appendChild(label);

    const equipButton = document.createElement("button");
    equipButton.type = "button";
    equipButton.textContent = item.active ? "已装" : "装";
    equipButton.addEventListener("click", () => sendQuickCommand(item.equipCommand));
    itemWrap.appendChild(equipButton);

    const viewButton = document.createElement("button");
    viewButton.type = "button";
    viewButton.textContent = "看";
    viewButton.addEventListener("click", () => sendQuickCommand(item.viewCommand));
    itemWrap.appendChild(viewButton);

    if (item.sellableQuantity > 0 && item.sellCommand) {
      const sellButton = document.createElement("button");
      sellButton.type = "button";
      sellButton.textContent = "卖";
      sellButton.title = `只出售未装备数量：${item.sellableQuantity}`;
      sellButton.addEventListener("click", () => sendQuickCommand(item.sellCommand));
      itemWrap.appendChild(sellButton);
    }

    wrap.appendChild(itemWrap);
  });
  summary.appendChild(wrap);
}

function renderMerchantItems(items, leaveCommand) {
  const existing = summary.querySelector(".quick-shop");
  if (existing) existing.remove();
  if (!items.length && !leaveCommand) return;

  const wrap = document.createElement("div");
  wrap.className = "quick-shop";
  const title = document.createElement("div");
  title.className = "quick-shop-title";
  title.textContent = "商店快捷";
  wrap.appendChild(title);

  items.forEach((item) => {
    const buyButton = document.createElement("button");
    buyButton.type = "button";
    buyButton.textContent = `买 ${item.type}·${item.name} ${item.price}两`;
    buyButton.addEventListener("click", () => sendQuickCommand(item.command));
    wrap.appendChild(buyButton);

    if (item.viewCommand) {
      const viewButton = document.createElement("button");
      viewButton.type = "button";
      viewButton.textContent = "看";
      viewButton.addEventListener("click", () => sendQuickCommand(item.viewCommand));
      wrap.appendChild(viewButton);
    }
  });
  if (leaveCommand) {
    const leaveButton = document.createElement("button");
    leaveButton.type = "button";
    leaveButton.textContent = "离开商人";
    leaveButton.addEventListener("click", () => sendQuickCommand(leaveCommand));
    wrap.appendChild(leaveButton);
  }
  summary.appendChild(wrap);
}

function renderSkillItems(items) {
  const existing = summary.querySelector(".quick-skill");
  if (existing) existing.remove();
  if (!items.length) return;

  const wrap = document.createElement("div");
  wrap.className = "quick-skill";
  const title = document.createElement("div");
  title.className = "quick-skill-title";
  title.textContent = "技能快捷";
  wrap.appendChild(title);

  items.forEach((item) => {
    const itemWrap = document.createElement("div");
    itemWrap.className = `quick-skill-item${item.active ? " is-active" : ""}`;

    const label = document.createElement("span");
    label.textContent = item.active ? `★ ${item.name}` : item.name;
    itemWrap.appendChild(label);

    const selectButton = document.createElement("button");
    selectButton.type = "button";
    selectButton.textContent = "选";
    selectButton.addEventListener("click", () => sendQuickCommand(item.selectCommand));
    itemWrap.appendChild(selectButton);

    if (item.viewCommand) {
      const viewButton = document.createElement("button");
      viewButton.type = "button";
      viewButton.textContent = "看";
      viewButton.addEventListener("click", () => sendQuickCommand(item.viewCommand));
      itemWrap.appendChild(viewButton);
    }

    if (item.attackCommand) {
      const attackButton = document.createElement("button");
      attackButton.type = "button";
      attackButton.textContent = "攻";
      attackButton.addEventListener("click", () => sendQuickCommand(item.attackCommand));
      itemWrap.appendChild(attackButton);
    }

    wrap.appendChild(itemWrap);
  });
  summary.appendChild(wrap);
}

function renderLearnableSkills(items) {
  const existing = summary.querySelector(".quick-martial");
  if (existing) existing.remove();
  if (!items.length) return;

  const wrap = document.createElement("div");
  wrap.className = "quick-martial";
  const title = document.createElement("div");
  title.className = "quick-skill-title";
  title.textContent = "武学领悟";
  wrap.appendChild(title);

  items.forEach((item) => {
    const itemWrap = document.createElement("div");
    itemWrap.className = `quick-skill-item${item.status === "可领悟" ? " is-ready" : ""}`;

    const label = document.createElement("span");
    label.textContent = item.cost ? `${item.name}｜${item.status}` : item.name;
    itemWrap.appendChild(label);

    const learnButton = document.createElement("button");
    learnButton.type = "button";
    learnButton.textContent = item.actionLabel || (item.cost ? "悟" : "看");
    learnButton.addEventListener("click", () => sendQuickCommand(item.learnCommand));
    itemWrap.appendChild(learnButton);

    if (item.viewCommand) {
      const viewButton = document.createElement("button");
      viewButton.type = "button";
      viewButton.textContent = "看";
      viewButton.addEventListener("click", () => sendQuickCommand(item.viewCommand));
      itemWrap.appendChild(viewButton);
    }

    wrap.appendChild(itemWrap);
  });
  summary.appendChild(wrap);
}

function sendQuickCommand(command) {
  commandInput.value = command;
  sendCommand(command);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[char]));
}

commandForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = commandInput.value.trim();
  if (!text) return;
  sendCommand(text);
});

document.querySelectorAll("[data-cmd]").forEach((button) => {
  button.addEventListener("click", () => {
    const command = button.dataset.cmd;
    commandInput.value = command;
    sendCommand(command);
  });
});

document.querySelectorAll("[data-start-sect]").forEach((button) => {
  button.addEventListener("click", () => {
    selectedSect = button.dataset.startSect;
    setSelected("[data-start-sect]", button);
    updateStartSubmit();
  });
});

document.querySelectorAll("[data-start-difficulty]").forEach((button) => {
  button.addEventListener("click", () => {
    selectedDifficulty = button.dataset.startDifficulty;
    setSelected("[data-start-difficulty]", button);
    updateStartSubmit();
  });
});

document.querySelector("[data-start-submit]")?.addEventListener("click", () => {
  const command = `/金庸开局 ${selectedSect} ${selectedDifficulty}`;
  commandInput.value = command;
  sendCommand(command);
});

function setSelected(selector, selectedButton) {
  document.querySelectorAll(selector).forEach((button) => {
    button.classList.toggle("is-selected", button === selectedButton);
  });
}

function updateStartSubmit() {
  const button = document.querySelector("[data-start-submit]");
  if (button) button.textContent = `开局：${selectedSect} ${selectedDifficulty}`;
}

sendCommand("/金庸帮助");
