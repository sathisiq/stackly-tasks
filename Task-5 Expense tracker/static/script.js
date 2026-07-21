const money = value => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(Number(value || 0));
const escapeHtml = text => String(text ?? '').replace(/[&<>'"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c]));

async function api(url, options = {}) {
  const response = await fetch(url, { credentials: 'include', headers: { 'Content-Type': 'application/json', ...(options.headers || {}) }, ...options });
  const data = await response.json().catch(() => ({}));
  if (response.status === 401 && !location.pathname.endsWith('login.html')) location.href = '/login.html';
  if (!response.ok) throw new Error(data.error || 'Something went wrong.');
  return data;
}
function showMessage(id, message, success = false) { const el = document.getElementById(id); if (el) { el.textContent = message; el.className = `message${success ? ' success' : ''}`; } }
function today() { return new Date().toISOString().slice(0, 10); }

async function redirectIfLoggedIn() { try { await api('/me'); location.href = '/dashboard.html'; } catch (_) { } }
async function initProtected() { const { user } = await api('/me'); const name = document.getElementById('username'); if (name) name.textContent = user.username; }

function wireLogout() { document.querySelectorAll('[data-logout]').forEach(button => button.onclick = async () => { try { await api('/logout'); } finally { location.href = '/login.html'; } }); }

function initLogin() {
  redirectIfLoggedIn();
  document.getElementById('loginForm').onsubmit = async event => { event.preventDefault(); const form = new FormData(event.currentTarget); try { await api('/login', { method: 'POST', body: JSON.stringify(Object.fromEntries(form)) }); location.href = '/dashboard.html'; } catch (error) { showMessage('message', error.message); } };
}
function initRegister() {
  document.getElementById('registerForm').onsubmit = async event => { event.preventDefault(); const values = Object.fromEntries(new FormData(event.currentTarget)); if (values.password !== values.confirm) return showMessage('message', 'Passwords do not match.'); delete values.confirm; try { await api('/register', { method: 'POST', body: JSON.stringify(values) }); showMessage('message', 'Account created. Redirecting to login…', true); setTimeout(() => location.href = '/login.html', 700); } catch (error) { showMessage('message', error.message); } };
}

async function initDashboard() {
  await initProtected(); wireLogout();
  try {
    const [summary, list] = await Promise.all([api('/expenses/summary'), api('/expenses')]);
    document.getElementById('totalCount').textContent = summary.expense_count;
    document.getElementById('totalAmount').textContent = money(summary.total_amount);
    document.getElementById('highest').textContent = money(summary.highest_expense);
    document.getElementById('categoryCount').textContent = summary.category_count;
    const breakdown = document.getElementById('breakdown');
    breakdown.innerHTML = summary.by_category.length ? summary.by_category.map(row => `<div><div class="bar-label"><span>${escapeHtml(row.category)}</span><b>${money(row.amount)}</b></div><div class="bar-track"><div class="bar-fill" style="width:${summary.total_amount ? row.amount / summary.total_amount * 100 : 0}%"></div></div></div>`).join('') : '<p class="empty">No expenses yet. Add your first one to see a breakdown.</p>';
    const recent = document.getElementById('recent');
    recent.innerHTML = list.expenses.slice(0, 5).map(item => `<div class="expense-row"><div><b>${escapeHtml(item.title)}</b><br><small>${escapeHtml(item.category)} · ${item.date}</small></div><strong>${money(item.amount)}</strong></div>`).join('') || '<p class="empty">No expenses recorded yet.</p>';
  } catch (error) { console.error(error); }
}

async function initExpenses() {
  await initProtected(); wireLogout();
  const form = document.getElementById('expenseForm'), table = document.getElementById('expenseTable'); let editingId = null, loaded = [];
  form.elements.date.value = today();
  const reset = () => { editingId = null; form.reset(); form.elements.date.value = today(); document.getElementById('formTitle').textContent = 'Add expense'; document.getElementById('saveButton').textContent = 'Add expense'; document.getElementById('cancelEdit').classList.add('hidden'); showMessage('formMessage', ''); };
  const render = expenses => {
    loaded = expenses; table.innerHTML = expenses.map(item => `<tr><td><b>${escapeHtml(item.title)}</b>${item.note ? `<br><small>${escapeHtml(item.note)}</small>` : ''}</td><td>${escapeHtml(item.category)}</td><td>${item.date}</td><td class="amount">${money(item.amount)}</td><td class="actions"><button class="small secondary" data-edit="${item.id}">Edit</button><button class="small danger" data-delete="${item.id}">Delete</button></td></tr>`).join('') || '<tr><td colspan="5" class="empty">No matching expenses.</td></tr>';
    table.querySelectorAll('[data-edit]').forEach(btn => btn.onclick = () => { const item = loaded.find(x => x.id === Number(btn.dataset.edit)); editingId = item.id;['title', 'amount', 'category', 'date', 'note'].forEach(key => form.elements[key].value = item[key] ?? ''); document.getElementById('formTitle').textContent = 'Edit expense'; document.getElementById('saveButton').textContent = 'Save changes'; document.getElementById('cancelEdit').classList.remove('hidden'); form.scrollIntoView({ behavior: 'smooth', block: 'start' }); });
    table.querySelectorAll('[data-delete]').forEach(btn => btn.onclick = async () => { if (!confirm('Delete this expense? This cannot be undone.')) return; try { await api(`/expenses/${btn.dataset.delete}`, { method: 'DELETE' }); await refresh(); } catch (error) { alert(error.message); } });
  };
  async function refresh() { const category = document.getElementById('filterCategory').value, from = document.getElementById('filterFrom').value, to = document.getElementById('filterTo').value; const params = new URLSearchParams(); if (category) params.set('category', category); if (from) params.set('from', from); if (to) params.set('to', to); const result = await api(params.size ? `/expenses/filter?${params}` : '/expenses'); render(result.expenses); }
  form.onsubmit = async event => { event.preventDefault(); const data = Object.fromEntries(new FormData(form)); try { await api(editingId ? `/expenses/${editingId}` : '/expenses', { method: editingId ? 'PUT' : 'POST', body: JSON.stringify(data) }); reset(); await refresh(); } catch (error) { showMessage('formMessage', error.message); } };
  document.getElementById('cancelEdit').onclick = reset;
  ['filterCategory', 'filterFrom', 'filterTo'].forEach(id => document.getElementById(id).onchange = () => refresh().catch(error => alert(error.message)));
  document.getElementById('clearFilters').onclick = () => { ['filterCategory', 'filterFrom', 'filterTo'].forEach(id => document.getElementById(id).value = ''); refresh(); };
  await refresh();
}

if (document.getElementById('loginForm')) initLogin();
if (document.getElementById('registerForm')) initRegister();
if (document.getElementById('breakdown')) initDashboard();
if (document.getElementById('expenseForm')) initExpenses();
