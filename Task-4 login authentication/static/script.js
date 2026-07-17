const message = document.querySelector("#message");
function showMessage(text, type = "error") { if (message) { message.textContent = text; message.className = `notice ${type}`; } }
async function request(url, options = {}) { const response = await fetch(url, { credentials: "same-origin", ...options }); const data = await response.json().catch(() => ({})); return { response, data }; }

const registerForm = document.querySelector("#register-form");
if (registerForm) registerForm.addEventListener("submit", async (event) => {
  event.preventDefault(); const username = registerForm.username.value.trim(); const email = registerForm.email.value.trim(); const password = registerForm.password.value; const confirm = document.querySelector("#confirmPassword").value;
  if (!username || !email || !password || !confirm) return showMessage("Please complete every field.");
  if (!/^\S+@\S+\.\S+$/.test(email)) return showMessage("Enter a valid email address.");
  if (password.length < 8) return showMessage("Password must contain at least 8 characters.");
  if (password !== confirm) return showMessage("Passwords do not match.");
  try { const { response, data } = await request("/register", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, email, password }) }); if (!response.ok) return showMessage(data.message || "Could not create your account."); showMessage(data.message, "success"); setTimeout(() => location.assign("/"), 700); } catch { showMessage("Unable to reach the server."); }
});

const loginForm = document.querySelector("#login-form");
if (loginForm) loginForm.addEventListener("submit", async (event) => {
  event.preventDefault(); const username = loginForm.username.value.trim(); const password = loginForm.password.value;
  if (!username || !password) return showMessage("Enter your username and password.");
  try { const { response, data } = await request("/login", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ username, password, rememberMe: document.querySelector("#rememberMe").checked }) }); if (!response.ok) return showMessage(response.status === 401 ? "Invalid username or password" : (data.message || "Unable to sign in.")); location.assign("/dashboard.html"); } catch { showMessage("Unable to reach the server."); }
});

if (document.querySelector("#welcome")) (async () => { try { const { response, data } = await request("/profile"); if (!response.ok) return location.replace("/"); const user = data.user; document.querySelector("#welcome").textContent = `Welcome, ${user.username}!`; document.querySelector("#role").textContent = user.role; document.querySelector("#email").textContent = user.email; document.querySelector("#created-at").textContent = user.created_at ? new Date(user.created_at).toLocaleString() : "—"; } catch { location.replace("/"); } })();
document.querySelector("#logout")?.addEventListener("click", async () => { try { await request("/logout"); } finally { location.replace("/"); } });
