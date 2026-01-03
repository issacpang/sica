let lastAssessment = null;
let lastAssessmentSaved = false;

const FIELDS = [
  "approaches",
  "columns",
  "joints_hinges",
  "abutments_wingwalls_shearkeys",
];

const state = Object.fromEntries(FIELDS.map(k => [k, []]));

function $(id){ return document.getElementById(id); }

function setCount(key){
  const el = $(`count-${key}`);
  if (!el) return;
  const n = state[key]?.length || 0;
  el.textContent = `${n} selected`;
}

function renderPreviewInDropzone(key){
  const dz = document.querySelector(`[data-dropzone="${key}"]`);
  const area = $(`prev-${key}`);
  if (!dz || !area) return;

  const files = state[key] || [];
  area.innerHTML = "";

  if (files.length === 0) {
    dz.classList.remove("has-files");
    return;
  }

  dz.classList.add("has-files");

  const show = files.slice(0, 8);
  show.forEach((file, idx) => {
    const url = URL.createObjectURL(file);
    const d = document.createElement("div");
    d.className = "thumb";

    // If there are more than 8 files, overlay a +N badge on the last visible thumb.
    if (idx === show.length - 1 && files.length > show.length) {
      d.classList.add("moreBadge");
      d.setAttribute("data-more", `+${files.length - show.length}`);
    }

    const img = document.createElement("img");
    img.src = url;
    img.alt = "preview";
    img.onload = () => URL.revokeObjectURL(url);
    d.appendChild(img);

    area.appendChild(d);
  });
}

function updateUploadUI(key){
  setCount(key);
  renderPreviewInDropzone(key);
}

function showError(msg){
  const err = $("err");
  if (!err) return;
  if (!msg) {
    err.classList.add("hidden");
    err.textContent = "";
    return;
  }
  err.classList.remove("hidden");
  err.textContent = msg;
}

// Busy state for Run button
const runBtn = $("runBtn");
const runText = $("runText");
const spinner = $("spinner");

function setBusy(on){
  if (!runBtn) return;
  runBtn.disabled = on;
  runBtn.classList.toggle("is-busy", on);
  runBtn.setAttribute("aria-busy", String(on));
  if (runText) runText.textContent = on ? "Running..." : "Run Assessment";
  if (spinner) spinner.style.display = on ? "inline-block" : "none";
}

// Wire inputs + dropzones
FIELDS.forEach(key => {
  const input = $(`file-${key}`);
  const dz = document.querySelector(`[data-dropzone="${key}"]`);
  const clearBtn = document.querySelector(`[data-clear="${key}"]`);

  if (dz && input) {
    const openPicker = () => input.click();

    dz.addEventListener("click", (e) => {
      // Ignore clicks on the clear button
      if (e.target && (e.target.closest?.("button") || e.target.tagName === "BUTTON")) return;
      openPicker();
    });

    dz.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        openPicker();
      }
    });

    dz.addEventListener("dragover", (e) => {
      e.preventDefault();
      dz.classList.add("drag");
    });

    dz.addEventListener("dragleave", () => dz.classList.remove("drag"));

    dz.addEventListener("drop", (e) => {
      e.preventDefault();
      dz.classList.remove("drag");
      const dropped = Array.from(e.dataTransfer.files || [])
        .filter(f => f.type && f.type.startsWith("image/"));

      if (dropped.length) {
        state[key] = dropped;
        updateUploadUI(key);
      }
    });

    input.addEventListener("change", () => {
      state[key] = Array.from(input.files || [])
        .filter(f => f.type && f.type.startsWith("image/"));
      updateUploadUI(key);
    });
  }

  if (clearBtn) {
    clearBtn.addEventListener("click", (e) => {
      e.stopPropagation(); // don't trigger upload
      state[key] = [];
      if (input) input.value = "";
      updateUploadUI(key);
    });
  }

  updateUploadUI(key);
});

// Clear all
$("clearAll")?.addEventListener("click", () => {
  FIELDS.forEach(key => {
    state[key] = [];
    const input = $(`file-${key}`);
    if (input) input.value = "";
    updateUploadUI(key);
  });
  showError("");
});

// Issac: Modal page setting.

const COMPONENT_LABELS = {
  approaches: "Approaches",
  columns: "Columns",
  joints_hinges: "Joints & Hinges",
  abutments_wingwalls_shearkeys: "Abutments & Shear Keys",
};

function escapeHtml(str){
  return String(str ?? "").replace(/[&<>"']/g, (c) => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  }[c]));
}

function normalizeRState(raw){
  const s = String(raw ?? "").toUpperCase();
  if (s.includes("R1")) return "R1";
  if (s.includes("R2")) return "R2";
  if (s.includes("R3")) return "R3";
  if (s.includes("R4")) return "R4";
  if (s.includes("GREEN") || s.includes("SAFE")) return "R1";
  if (s.includes("YELLOW") || s.includes("CAUTION") || s.includes("INSPECT")) return "R2";
  if (s.includes("RED") || s.includes("CRITICAL")) return "R3";
  return "UNKNOWN";
}

const R_STATE_INFO = {
  R1: { cls: "r1", title: "R1 · Open" },
  R2: { cls: "r2", title: "R2 · Open (Inspection)" },
  R3: { cls: "r3", title: "R3 · Close (Inspection)" },
  R4: { cls: "r4", title: "R4 · Close Immediately" },
  UNKNOWN: { cls: "unk", title: "Unknown" },
};

function badgeHTML(raw){
  const key = normalizeRState(raw);
  const meta = R_STATE_INFO[key] || R_STATE_INFO.UNKNOWN;
  return `<span class="badge ${meta.cls}"><span class="dot ${meta.cls}"></span>${meta.title}</span>`;
}

// Issac: show thumbnails in report if backend "photo" matches uploaded filename.
let reportObjectUrls = [];
function clearReportThumbs(){
  reportObjectUrls.forEach(u => URL.revokeObjectURL(u));
  reportObjectUrls = [];
}
function thumbHTML(componentKey, photoName){
  if (!photoName) return "";
  const f = (state[componentKey] || []).find(x => x.name === photoName);
  if (!f) return "";
  const url = URL.createObjectURL(f);
  reportObjectUrls.push(url);
  return `<div class="repThumbWrap"><img class="repThumb" src="${url}" alt="photo"/></div>`;
}

function renderReport(data){
  const overall = data?.overall_r_state ?? "UNKNOWN";
  const kpis = data?.kpis || {};
  const comps = data?.components || {};

  const order = ["approaches","columns","joints_hinges","abutments_wingwalls_shearkeys"];

  const sections = order
    .filter(k => comps[k])
    .map((key) => {
      const comp = comps[key];
      const items = comp.items || [];

      const rows = items.map((it, idx) => {
        const photo = it.photo || `Photo ${idx + 1}`;
        const reason = it.reason || "No reason provided.";
        const thumb = thumbHTML(key, photo) || `<div class="repThumbFallback"></div>`;

        return `
          <div class="repItem">
            <div class="repPhotoLine">
              ${thumb}
              <div class="repPhotoMeta">
                <div class="repPhotoName">${escapeHtml(photo)}</div>
                <div class="repPhotoState">${badgeHTML(it.r_state)}</div>
              </div>
            </div>
            <div class="repReason">${escapeHtml(reason)}</div>
          </div>
        `;
      }).join("");

      return `
        <section class="repSection">
          <div class="repSectionTop">
            <div class="repSectionTitle">
              <span>${escapeHtml(COMPONENT_LABELS[key] || key)}</span>
              <span class="repCount">${items.length} photo${items.length === 1 ? "" : "s"}</span>
            </div>
            <div>${badgeHTML(comp.overall_r_state)}</div>
          </div>
          <div class="repItems">${rows || `<div class="repEmpty">No items.</div>`}</div>
        </section>
      `;
    }).join("");

  const html = `
    <div class="reportHeader">
      <div>
        <div class="reportMeta">
          Components assessed: <b>${kpis.components_assessed ?? "-"}</b>
          · Photos analyzed: <b>${kpis.photos_analyzed ?? "-"}</b>
        </div>
      </div>
      <div class="reportOverall">${badgeHTML(overall)}</div>
    </div>

    <div class="reportLegend">
      ${badgeHTML("R1")}
      ${badgeHTML("R2")}
      ${badgeHTML("R3")}
      ${badgeHTML("R4")}
    </div>

    ${sections}
  `;

  const el = $("report");
  if (el) el.innerHTML = html;
}

// Optional modal
const overlay = $("overlay");
const closeModalBtn = $("closeModal");

function openModal(){
  overlay?.classList.add("open");
  overlay?.setAttribute("aria-hidden", "false");
  closeModalBtn?.focus?.();
}

async function closeModal() {
  try {
    const btn = document.getElementById("closeModal");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Saving…";
    }

    await saveAssessmentIfNeeded();
  } catch (e) {
    console.warn("Save error:", e);
  } finally {
    const btn = document.getElementById("closeModal");
    if (btn) {
      btn.disabled = false;
      btn.textContent = "✕ Close";
    }
  }

  overlay?.classList.remove("open");
  overlay?.setAttribute("aria-hidden", "true");
}


async function saveAssessmentIfNeeded() {
  if (!lastAssessment || lastAssessmentSaved) return;

  const res = await fetch("/api/save_result", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(lastAssessment),
  });

  if (!res.ok) {
    console.warn("Failed to save assessment JSON");
    return;
  }

  const out = await res.json();
  lastAssessmentSaved = true;
  console.log("Saved assessment:", out.filename);
}


closeModalBtn?.addEventListener("click", closeModal);
overlay?.addEventListener("click", (e) => { if (e.target === overlay) closeModal(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeModal(); });


// Run (calls backend if available)
$("runBtn")?.addEventListener("click", async () => {
  showError("");
  const total = FIELDS.reduce((n, k) => n + (state[k]?.length || 0), 0);
  if (total === 0) {
    showError("Upload at least one image before running assessment.");
    return;
  }

  setBusy(true);
  try {
    const fd = new FormData();
    for (const key of FIELDS) {
      for (const f of (state[key] || [])) fd.append(key, f, f.name);
    }

    const res = await fetch("/api/assess", { method: "POST", body: fd });
    const data = await res.json();

    if (!res.ok) {
      showError(data?.error || "Assessment failed.");
      return;
    }

    clearReportThumbs();

    lastAssessment = data;    
    lastAssessmentSaved = false;
    renderReport(data);
    openModal();

  } catch (e) {
    showError("Network/server error. Check console + server logs.");
  } finally {
    setBusy(false);
  }
}


);
