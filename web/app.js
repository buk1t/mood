const mood = document.getElementById("mood");
const moodVal = document.getElementById("moodVal");
const statusEl = document.getElementById("status");
const entriesEl = document.getElementById("entries");

const panicBtn = document.getElementById("panicBtn");
const panicDialog = document.getElementById("panicDialog");
const panicMood = document.getElementById("panicMood");
const panicText = document.getElementById("panicText");
const panicSave = document.getElementById("panicSave");

mood.addEventListener("input", () => moodVal.textContent = mood.value);

async function refreshEntries() {
  const entries = await window.pywebview.api.list_entries();
  entriesEl.innerHTML = "";
  for (const e of entries.slice(0, 14)) {
    const div = document.createElement("div");
    div.className = "item";
    const preview = (e.anything_else || e.panic_text || e.thinking || e.today_facts || "").slice(0, 90);
    div.innerHTML = `
      <div><strong>${e.date}</strong> · mood <strong>${e.mood ?? ""}</strong>${e.panic ? " · <strong>panic</strong>" : ""}</div>
      <div class="small">${preview}${preview.length === 90 ? "…" : ""}</div>
    `;
    entriesEl.appendChild(div);
  }
}

function getBool(id) { return document.getElementById(id).checked; }
function getVal(id) { return document.getElementById(id).value; }

document.getElementById("saveBtn").addEventListener("click", async () => {
  statusEl.textContent = "Saving…";

  const entry = {
    mood: Number(getVal("mood")),
    sleep_hours: getVal("sleepHours") ? Number(getVal("sleepHours")) : null,
    sleep_quality: getVal("sleepQuality") ? Number(getVal("sleepQuality")) : null,
    meds: [{ name: "fluoxetine", dose_mg: 20, taken: getBool("medsTaken") }],
    checks: {
      exercise: getBool("exercise"),
      social: getBool("social"),
      outside: getBool("outside"),
      ate_ok: getBool("ateOk"),
      alcohol: getBool("alcohol"),
      nicotine: getBool("nicotine"),
      weed: getBool("weed")
    },
    today_facts: getVal("todayFacts"),
    thinking: getVal("thinking"),
    feeling: getVal("feeling"),
    why: getVal("why"),
    anything_else: getVal("anythingElse"),
    panic: false,
    tags: []
  };

  const res = await window.pywebview.api.add_entry(entry);
  statusEl.textContent = res.ok ? "Saved." : "Error saving.";

  await refreshEntries();
});

panicBtn.addEventListener("click", () => {
  panicText.value = "";
  panicMood.value = "0";
  panicDialog.showModal();
});

panicSave.addEventListener("click", async (ev) => {
  ev.preventDefault();
  const entry = {
    mood: Number(panicMood.value),
    panic: true,
    panic_text: panicText.value,
    checks: {},
    meds: [{ name: "fluoxetine", dose_mg: 20, taken: null }]
  };
  await window.pywebview.api.add_entry(entry);
  panicDialog.close();
  await refreshEntries();
});

(async function init() {
  moodVal.textContent = mood.value;
  await refreshEntries();
})();