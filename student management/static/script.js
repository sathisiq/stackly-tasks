const API = "/api/students";
const form = document.querySelector("#studentForm");
const table = document.querySelector("#studentTable");
const totalCount = document.querySelector("#totalCount");
const courseStats = document.querySelector("#courseStats");
const formError = document.querySelector("#formError");
const statusMessage = document.querySelector("#statusMessage");
const searchInput = document.querySelector("#searchInput");
let students = [];
let searchTimer;

function escapeHtml(value) { const div = document.createElement("div"); div.textContent = value; return div.innerHTML; }
function displayDate(value) { return new Intl.DateTimeFormat(undefined, { day: "2-digit", month: "short", year: "numeric" }).format(new Date(`${value}T00:00:00`)); }
function setStatus(message, isError = false) { statusMessage.textContent = message; statusMessage.classList.toggle("error", isError); }

function renderTable(records) {
  if (!records.length) { table.innerHTML = '<tr><td class="empty" colspan="6">No students found.</td></tr>'; return; }
  table.innerHTML = records.map(s => `<tr><td class="name">${escapeHtml(s.full_name)}</td><td>${escapeHtml(s.email)}</td><td>${escapeHtml(s.phone)}</td><td><span class="course-pill">${escapeHtml(s.course)}</span></td><td>${displayDate(s.enrolled_on)}</td><td class="actions"><button class="edit" data-id="${s.id}">Edit</button><button class="delete" data-id="${s.id}" data-name="${escapeHtml(s.full_name)}">Delete</button></td></tr>`).join("");
}

function renderStats() {
  totalCount.textContent = students.length;
  const counts = students.reduce((acc, student) => ({ ...acc, [student.course]: (acc[student.course] || 0) + 1 }), {});
  courseStats.innerHTML = Object.entries(counts).map(([course, count]) => `<article class="stat-card course-card"><span>${escapeHtml(course)}</span><strong>${count}</strong><small>${count === 1 ? "student" : "students"}</small></article>`).join("") || '<article class="stat-card course-card empty-stat"><span>Courses</span><strong>—</strong><small>Add a student to begin</small></article>';
}

async function request(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

async function loadStudents() {
  try { students = await request(API); renderTable(students); renderStats(); setStatus(""); }
  catch (error) { renderTable([]); setStatus(error.message, true); }
}

function clearForm() { form.reset(); document.querySelector("#studentId").value = ""; document.querySelector("#formTitle").textContent = "Add a student"; document.querySelector("#saveButton").textContent = "Add student"; document.querySelector("#cancelEdit").classList.add("hidden"); formError.textContent = ""; }

form.addEventListener("submit", async event => {
  event.preventDefault(); formError.textContent = "";
  if (!form.checkValidity()) { form.reportValidity(); return; }
  const id = document.querySelector("#studentId").value;
  const payload = Object.fromEntries(new FormData(form));
  try {
    await request(id ? `${API}/${id}` : API, { method: id ? "PUT" : "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    clearForm(); await loadStudents(); setStatus(id ? "Student updated successfully." : "Student added successfully.");
  } catch (error) { formError.textContent = error.message; }
});

document.querySelector("#cancelEdit").addEventListener("click", clearForm);
table.addEventListener("click", async event => {
  const button = event.target.closest("button"); if (!button) return;
  const id = Number(button.dataset.id);
  const student = students.find(item => item.id === id);
  if (button.classList.contains("edit") && student) {
    document.querySelector("#studentId").value = student.id; document.querySelector("#fullName").value = student.full_name; document.querySelector("#email").value = student.email; document.querySelector("#phone").value = student.phone; document.querySelector("#course").value = student.course;
    document.querySelector("#formTitle").textContent = "Edit student"; document.querySelector("#saveButton").textContent = "Save changes"; document.querySelector("#cancelEdit").classList.remove("hidden"); document.querySelector("#fullName").focus();
  }
  if (button.classList.contains("delete") && confirm(`Delete ${button.dataset.name}? This cannot be undone.`)) {
    try { await request(`${API}/${id}`, { method: "DELETE" }); if (document.querySelector("#studentId").value === String(id)) clearForm(); await loadStudents(); setStatus("Student deleted successfully."); }
    catch (error) { setStatus(error.message, true); }
  }
});

searchInput.addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(async () => { try { const records = await request(`${API}/search?q=${encodeURIComponent(searchInput.value.trim())}`); renderTable(records); setStatus(""); } catch (error) { setStatus(error.message, true); } }, 220); });
loadStudents();
