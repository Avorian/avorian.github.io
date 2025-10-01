const STORAGE_KEY = "wwe-universe-tracker";
const data = {
  overview: {
    universeName: "",
    currentWeek: "",
    owner: "",
    notes: ""
  },
  shows: [],
  superstars: [],
  championships: [],
  rivalries: [],
  events: []
};

const state = {
  filterShow: ""
};

const elements = {
  overviewForm: document.getElementById("overviewForm"),
  overviewSummary: document.getElementById("overviewSummary"),
  showForm: document.getElementById("showForm"),
  showsList: document.getElementById("showsList"),
  superstarForm: document.getElementById("superstarForm"),
  superstarList: document.getElementById("superstarList"),
  showFilter: document.getElementById("showFilter"),
  assignedShow: document.getElementById("assignedShow"),
  titleShow: document.getElementById("titleShow"),
  rivalryShow: document.getElementById("rivalryShow"),
  championshipForm: document.getElementById("championshipForm"),
  championshipList: document.getElementById("championshipList"),
  rivalryForm: document.getElementById("rivalryForm"),
  rivalryList: document.getElementById("rivalryList"),
  eventForm: document.getElementById("eventForm"),
  eventList: document.getElementById("eventList"),
  exportBtn: document.getElementById("exportData"),
  importInput: document.getElementById("importData"),
  resetBtn: document.getElementById("resetData"),
  toast: document.getElementById("toast")
};

function loadData() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      renderAll();
      return;
    }
    const parsed = JSON.parse(stored);
    for (const key of Object.keys(data)) {
      if (parsed[key]) {
        data[key] = parsed[key];
      }
    }
    renderAll();
  } catch (error) {
    console.error("Failed to load data", error);
    showToast("Could not load saved data. Starting fresh.");
    renderAll();
  }
}

function saveData() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function renderAll() {
  renderOverview();
  renderShows();
  renderSuperstars();
  renderChampionships();
  renderRivalries();
  renderEvents();
  syncShowOptions();
}

function renderOverview() {
  const { universeName, currentWeek, owner, notes } = data.overview;
  if (!universeName && !currentWeek && !owner && !notes) {
    elements.overviewSummary.innerHTML =
      "<p class=\"muted\">Save an overview to see it here.</p>";
    return;
  }

  elements.overviewSummary.innerHTML = `
    <p><strong>${escapeHtml(universeName || "Unnamed Universe")}</strong></p>
    <p><strong>Week:</strong> ${escapeHtml(currentWeek || "TBD")}</p>
    <p><strong>GM:</strong> ${escapeHtml(owner || "")}</p>
    ${notes ? `<p>${escapeHtml(notes)}</p>` : ""}
  `;
}

function renderShows() {
  if (!data.shows.length) {
    elements.showsList.innerHTML = `<p class="muted">Add your first show to begin tracking rosters.</p>`;
    return;
  }

  elements.showsList.innerHTML = data.shows
    .map(
      (show, index) => `
        <article class="list-card" style="border-top: 5px solid ${show.color};">
          <button type="button" class="delete-btn" data-type="show" data-index="${index}">Remove</button>
          <strong>${escapeHtml(show.name)}</strong>
          <span>${escapeHtml(show.day)} ${show.arena ? `• ${escapeHtml(show.arena)}` : ""}</span>
          ${show.notes ? `<p>${escapeHtml(show.notes)}</p>` : ""}
        </article>
      `
    )
    .join("");
}

function renderSuperstars() {
  const filtered = state.filterShow
    ? data.superstars.filter((star) => star.show === state.filterShow)
    : data.superstars;

  if (!filtered.length) {
    elements.superstarList.innerHTML = `<p class="muted">${
      data.superstars.length
        ? "No superstars for this filter yet."
        : "Add superstars to build your roster."
    }</p>`;
    return;
  }

  elements.superstarList.innerHTML = filtered
    .map((star, index) => {
      const globalIndex = data.superstars.indexOf(star);
      return `
        <article class="list-card" data-show="${escapeHtml(star.show)}">
          <button type="button" class="delete-btn" data-type="superstar" data-index="${globalIndex}">Remove</button>
          <strong>${escapeHtml(star.name)}</strong>
          <span>${escapeHtml(star.show)} • ${escapeHtml(star.alignment)}</span>
          ${star.status ? `<span>Status: ${escapeHtml(star.status)}</span>` : ""}
          ${star.notes ? `<p>${escapeHtml(star.notes)}</p>` : ""}
        </article>
      `;
    })
    .join("");
}

function renderChampionships() {
  if (!data.championships.length) {
    elements.championshipList.innerHTML = `<p class="muted">Add a title to track your champions.</p>`;
    return;
  }

  elements.championshipList.innerHTML = data.championships
    .map(
      (title, index) => `
        <article class="list-card">
          <button type="button" class="delete-btn" data-type="championship" data-index="${index}">Remove</button>
          <strong>${escapeHtml(title.name)}</strong>
          <span>${escapeHtml(title.show)} • Current: ${escapeHtml(title.champion)}</span>
          ${title.notes ? `<p>${escapeHtml(title.notes)}</p>` : ""}
        </article>
      `
    )
    .join("");
}

function renderRivalries() {
  if (!data.rivalries.length) {
    elements.rivalryList.innerHTML = `<p class="muted">Log your first storyline to keep the momentum rolling.</p>`;
    return;
  }

  elements.rivalryList.innerHTML = data.rivalries
    .map(
      (rivalry, index) => `
        <article class="list-card">
          <button type="button" class="delete-btn" data-type="rivalry" data-index="${index}">Remove</button>
          <strong>${escapeHtml(rivalry.participants)}</strong>
          <span>${escapeHtml(rivalry.show)} • ${escapeHtml(rivalry.status)}</span>
          ${rivalry.start ? `<span>Started: ${escapeHtml(rivalry.start)}</span>` : ""}
          ${rivalry.notes ? `<p>${escapeHtml(rivalry.notes)}</p>` : ""}
        </article>
      `
    )
    .join("");
}

function renderEvents() {
  if (!data.events.length) {
    elements.eventList.innerHTML = `<p class="muted">No premium live events logged yet.</p>`;
    return;
  }

  elements.eventList.innerHTML = data.events
    .map(
      (event, index) => `
        <article class="list-card">
          <button type="button" class="delete-btn" data-type="event" data-index="${index}">Remove</button>
          <strong>${escapeHtml(event.name)}</strong>
          ${event.date ? `<span>${escapeHtml(formatDate(event.date))}</span>` : ""}
          ${event.location ? `<span>${escapeHtml(event.location)}</span>` : ""}
          ${event.highlights ? `<p>${escapeHtml(event.highlights)}</p>` : ""}
        </article>
      `
    )
    .join("");
}

function syncShowOptions() {
  const options = ['<option value="">Select a show</option>']
    .concat(data.shows.map((show) => `<option value="${escapeHtml(show.name)}">${escapeHtml(show.name)}</option>`))
    .join("");

  elements.assignedShow.innerHTML = options;
  elements.titleShow.innerHTML = options;
  elements.rivalryShow.innerHTML = options;

  const filterOptions = ['<option value="">All Shows</option>']
    .concat(data.shows.map((show) => `<option value="${escapeHtml(show.name)}">${escapeHtml(show.name)}</option>`))
    .join("");

  elements.showFilter.innerHTML = filterOptions;
  if (state.filterShow && !data.shows.find((show) => show.name === state.filterShow)) {
    state.filterShow = "";
  }
}

function addShow(formData) {
  const show = {
    name: formData.get("showName").trim(),
    day: formData.get("showDay").trim(),
    arena: formData.get("showArena").trim(),
    color: formData.get("showColor") || "#ffffff",
    notes: formData.get("showNotes").trim()
  };

  if (!show.name || !show.day) {
    showToast("Show name and broadcast day are required.");
    return;
  }

  data.shows.push(show);
  saveData();
  renderShows();
  syncShowOptions();
  showToast(`${show.name} added.`);
}

function addSuperstar(formData) {
  const superstar = {
    name: formData.get("superstarName").trim(),
    show: formData.get("assignedShow"),
    alignment: formData.get("superstarAlignment") || "Face",
    status: formData.get("superstarStatus").trim(),
    notes: formData.get("superstarNotes").trim()
  };

  if (!superstar.name || !superstar.show) {
    showToast("Superstar name and show are required.");
    return;
  }

  data.superstars.push(superstar);
  saveData();
  renderSuperstars();
  showToast(`${superstar.name} added to ${superstar.show}.`);
}

function addChampionship(formData) {
  const title = {
    name: formData.get("titleName").trim(),
    show: formData.get("titleShow"),
    champion: formData.get("currentChampion").trim(),
    notes: formData.get("titleNotes").trim()
  };

  if (!title.name || !title.show || !title.champion) {
    showToast("Title name, defending show, and champion are required.");
    return;
  }

  data.championships.push(title);
  saveData();
  renderChampionships();
  showToast(`${title.name} saved.`);
}

function addRivalry(formData) {
  const rivalry = {
    show: formData.get("rivalryShow"),
    participants: formData.get("rivalryParticipants").trim(),
    start: formData.get("rivalryStart").trim(),
    status: formData.get("rivalryStatus"),
    notes: formData.get("rivalryNotes").trim()
  };

  if (!rivalry.show || !rivalry.participants) {
    showToast("Show and participants are required for a rivalry.");
    return;
  }

  data.rivalries.push(rivalry);
  saveData();
  renderRivalries();
  showToast(`Rivalry saved for ${rivalry.show}.`);
}

function addEvent(formData) {
  const event = {
    name: formData.get("eventName").trim(),
    date: formData.get("eventDate"),
    location: formData.get("eventLocation").trim(),
    highlights: formData.get("eventHighlights").trim()
  };

  if (!event.name) {
    showToast("Event name is required.");
    return;
  }

  data.events.push(event);
  saveData();
  renderEvents();
  showToast(`${event.name} added.`);
}

function deleteItem(type, index) {
  if (!data[type] || !data[type][index]) return;
  const [removed] = data[type].splice(index, 1);

  if (type === "shows" && removed?.name) {
    const showName = removed.name;
    data.superstars = data.superstars.filter((star) => star.show !== showName);
    data.championships = data.championships.filter((title) => title.show !== showName);
    data.rivalries = data.rivalries.filter((rivalry) => rivalry.show !== showName);
    if (state.filterShow === showName) {
      state.filterShow = "";
    }
  }

  saveData();

  switch (type) {
    case "shows":
      renderShows();
      renderSuperstars();
      renderChampionships();
      renderRivalries();
      syncShowOptions();
      break;
    case "superstars":
      renderSuperstars();
      break;
    case "championships":
      renderChampionships();
      break;
    case "rivalries":
      renderRivalries();
      break;
    case "events":
      renderEvents();
      break;
    default:
      break;
  }

  showToast(`${removed?.name || "Item"} removed.`);
}

function handleDelete(event) {
  const button = event.target.closest("button.delete-btn");
  if (!button) return;

  const type = button.dataset.type;
  const index = Number(button.dataset.index);
  const map = {
    show: "shows",
    superstar: "superstars",
    championship: "championships",
    rivalry: "rivalries",
    event: "events"
  };

  deleteItem(map[type], index);
}

function handleFormSubmit(form, handler) {
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    handler(formData);
    form.reset();
  });
}

function handleOverviewSubmit() {
  elements.overviewForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(elements.overviewForm);
    data.overview.universeName = formData.get("universeName").trim();
    data.overview.currentWeek = formData.get("currentWeek").trim();
    data.overview.owner = formData.get("owner").trim();
    data.overview.notes = formData.get("overviewNotes").trim();
    saveData();
    renderOverview();
    showToast("Overview updated.");
  });
}

function setupFilter() {
  elements.showFilter.addEventListener("change", (event) => {
    state.filterShow = event.target.value;
    renderSuperstars();
  });
}

function handleExport() {
  elements.exportBtn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(data, null, 2));
      showToast("Universe copied to clipboard as JSON!");
    } catch (error) {
      console.error(error);
      showToast("Copy failed. JSON downloaded instead.");
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${data.overview.universeName || "wwe-universe"}.json`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    }
  });
}

function handleImport() {
  elements.importInput.addEventListener("change", async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const text = await file.text();
      const imported = JSON.parse(text);
      for (const key of Object.keys(data)) {
        if (imported[key] !== undefined) {
          data[key] = imported[key];
        }
      }
      saveData();
      renderAll();
      showToast("Universe data imported!");
    } catch (error) {
      console.error("Import failed", error);
      showToast("Could not import file. Make sure it's a valid export.");
    } finally {
      event.target.value = "";
    }
  });
}

function handleReset() {
  elements.resetBtn.addEventListener("click", () => {
    if (!confirm("Reset all saved Universe data? This cannot be undone.")) return;
    for (const key of Object.keys(data)) {
      if (Array.isArray(data[key])) {
        data[key] = [];
      } else {
        data[key] = { universeName: "", currentWeek: "", owner: "", notes: "" };
      }
    }
    state.filterShow = "";
    saveData();
    renderAll();
    showToast("Universe reset.");
  });
}

function showToast(message) {
  elements.toast.textContent = message;
  elements.toast.setAttribute("open", "");
  setTimeout(() => {
    elements.toast.removeAttribute("open");
  }, 2800);
}

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric"
  });
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function hydrateForms() {
  elements.overviewForm.universeName.value = data.overview.universeName;
  elements.overviewForm.currentWeek.value = data.overview.currentWeek;
  elements.overviewForm.owner.value = data.overview.owner;
  elements.overviewForm.overviewNotes.value = data.overview.notes;
}

function hydrateSelects() {
  syncShowOptions();
  elements.showFilter.value = state.filterShow;
}

function init() {
  loadData();
  hydrateForms();
  hydrateSelects();

  handleOverviewSubmit();
  handleFormSubmit(elements.showForm, addShow);
  handleFormSubmit(elements.superstarForm, addSuperstar);
  handleFormSubmit(elements.championshipForm, addChampionship);
  handleFormSubmit(elements.rivalryForm, addRivalry);
  handleFormSubmit(elements.eventForm, addEvent);

  elements.showsList.addEventListener("click", handleDelete);
  elements.superstarList.addEventListener("click", handleDelete);
  elements.championshipList.addEventListener("click", handleDelete);
  elements.rivalryList.addEventListener("click", handleDelete);
  elements.eventList.addEventListener("click", handleDelete);

  setupFilter();
  handleExport();
  handleImport();
  handleReset();
}

init();
