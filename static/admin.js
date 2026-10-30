// © 2026 Bryan Gil — github.com/Bryanhackz — br4yangil006@gmail.com
const $ = (sel) => document.querySelector(sel);
let adminKey = "";

async function refresh() {
  const tbody = $("#queues tbody");
  if (!tbody) return;
  try {
    const res = await fetch("/admin/stats", {
      headers: { "X-API-Key": adminKey }
    });
    if (res.status === 401 || res.status === 403) {
      tbody.replaceChildren();
      return;
    }
    const data = await res.json();
    tbody.replaceChildren();
    for (const [node, count] of Object.entries(data.nodes || {})) {
      const tr = document.createElement("tr");
      const td1 = document.createElement("td");
      const td2 = document.createElement("td");
      td1.textContent = node;
      td2.textContent = String(count);
      tr.append(td1, td2);
      tbody.append(tr);
    }
  } catch {}
}

document.addEventListener("DOMContentLoaded", () => {
  adminKey = prompt("Enter Admin API Key:") || "";
  refresh();
  setInterval(refresh, 2000);
});