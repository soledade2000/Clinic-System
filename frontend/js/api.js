// frontend/js/api.js
// Centraliza todas as chamadas ao backend (API)
const API_URL = "http://127.0.0.1:8000"; // ajuste conforme necessário (ex: http://localhost:8000 ou URL do servidor)

const api = {
  _TOKEN_KEY: "token",
  _ACCESS_KEY: "access_token",
  _REFRESH_KEY: "refresh_token",
  _USER_KEY: "user",
  _userCache: null,

  // =====================
  // 🔐 AUTENTICAÇÃO
  // =====================
  getToken() {
    return localStorage.getItem(this._TOKEN_KEY) || localStorage.getItem(this._ACCESS_KEY);
  },

  setToken(t) {
    if (!t) return;
    localStorage.setItem(this._TOKEN_KEY, t);
    localStorage.setItem(this._ACCESS_KEY, t);
  },

  getRefreshToken() {
    return localStorage.getItem(this._REFRESH_KEY);
  },

  setRefreshToken(rt) {
    if (!rt) return;
    localStorage.setItem(this._REFRESH_KEY, rt);
  },

  setTokens(obj = {}) {
    if (obj.access_token) this.setToken(obj.access_token);
    if (obj.refresh_token) this.setRefreshToken(obj.refresh_token);
    if (obj.token) this.setToken(obj.token);
  },

  clearToken() {
    localStorage.removeItem(this._TOKEN_KEY);
    localStorage.removeItem(this._ACCESS_KEY);
  },

  clearRefreshToken() {
    localStorage.removeItem(this._REFRESH_KEY);
  },

  clearTokens() {
    this.clearToken();
    this.clearRefreshToken();
  },

  // =====================
  // 👤 USUÁRIO
  // =====================
  getUser() {
    try {
      return this._userCache || JSON.parse(localStorage.getItem(this._USER_KEY));
    } catch {
      return null;
    }
  },

  setUser(u) {
    this._userCache = u;
    if (!u) {
      localStorage.removeItem(this._USER_KEY);
    } else {
      localStorage.setItem(this._USER_KEY, JSON.stringify(u));
    }
  },

  clearUser() {
    this._userCache = null;
    localStorage.removeItem(this._USER_KEY);
  },

  getCargo() {
    return this.getUser()?.cargo || null;
  },

  hasRole(...roles) {
    const c = this.getCargo();
    return c && roles.includes(c);
  },

  logout() {
    try {
      const token = this.getToken();
      if (token) {
        fetch(`${API_URL}/auth/logout`, { method: "POST", headers: { Authorization: `Bearer ${token}` } }).catch(() => {});
      }
    } finally {
      this.clearTokens();
      this.clearUser();
      window.location.href = "login.html";
    }
  },

  // =====================
  // 🌐 REQUEST CENTRAL
  // =====================
  async request(endpoint, options = {}, useAuth = true) {
    const method = (options.method || "GET").toUpperCase();
    const headers = { ...(options.headers || {}) };

    if (useAuth) {
      const token = this.getToken();
      if (token) headers["Authorization"] = `Bearer ${token}`;
    }

    let body = options.body;
    const isForm = body instanceof FormData || body instanceof URLSearchParams;

    if (!isForm && body && typeof body === "object") {
      body = JSON.stringify(body);
      headers["Content-Type"] = "application/json";
    }

    const fetchOpts = { method, headers };
    if (method !== "GET" && method !== "HEAD") fetchOpts.body = body;

    let res = await fetch(`${API_URL}${endpoint}`, fetchOpts);

    // 🔄 tentar refresh se token expirou
    if (res.status === 401 && useAuth) {
      const refreshed = await this._tryRefresh();
      if (refreshed) {
        const token = this.getToken();
        if (token) headers["Authorization"] = `Bearer ${token}`;
        res = await fetch(`${API_URL}${endpoint}`, { ...fetchOpts, headers });
      } else {
        this.clearTokens();
        this.clearUser();
        window.location.href = "login.html";
        throw new Error("Não autorizado");
      }
    }

    const text = await res.text().catch(() => "");
    let data = null;
    try { data = text ? JSON.parse(text) : null; } catch { data = text; }

    if (!res.ok) {
      const message = (data && (data.detail || data.message)) || res.statusText || `Erro ${res.status}`;
      const err = new Error(message);
      err.status = res.status;
      err.body = data;
      throw err;
    }

    return data;
  },

  // =====================
  // 🔄 REFRESH TOKEN
  // =====================
  async _tryRefresh() {
    const refresh = this.getRefreshToken();
    if (!refresh) return false;
    try {
      const form = new URLSearchParams();
      form.append("refresh_token", refresh);
      const res = await fetch(`${API_URL}/auth/refresh`, { method: "POST", body: form });
      if (!res.ok) return false;
      const data = await res.json().catch(() => null);
      this.setTokens(data || {});
      return true;
    } catch {
      return false;
    }
  },

  // =====================
  // 🔑 LOGIN / LOGOUT / USUÁRIO
  // =====================
  async login(email, password) {
    const form = new URLSearchParams();
    form.append("email", email);
    form.append("password", password);

    const res = await fetch(`${API_URL}/auth/login`, { method: "POST", body: form });
    const data = await res.json().catch(() => null);
    if (!res.ok) throw new Error(data?.detail || "Erro no login");
    this.setTokens(data || {});
    return data;
  },

  async apiLogin(email, password) {
    const data = await this.login(email, password);
    try {
      const me = await this.request("/usuarios/me");
      this.setUser(me);
      return { token: data.access_token || data.token, user: me };
    } catch {
      return { token: data.access_token || data.token, user: null };
    }
  },

  async apiLogout() {
    return this.request("/auth/logout", { method: "POST" })
      .finally(() => { this.clearTokens(); this.clearUser(); window.location.href = "login.html"; });
  },

  async apiGetMe() { return this.request("/usuarios/me"); },
  async getCurrentUser() { return this.request("/usuarios/me"); },

  // =====================
  // 📊 DASHBOARD
  // =====================
  async apiGetDashboard() { return this.request("/dashboard"); },

  // =====================
  // 👥 PACIENTES
  // =====================
  async apiGetPacientes(skip = 0, limit = 100) { return this.request(`/pacientes?skip=${skip}&limit=${limit}`); },
  async apiGetPacienteById(id) { return this.request(`/pacientes/${id}`); },
  async apiCreatePaciente(payload) { return this.request("/pacientes/", { method: "POST", body: payload }); },
  async apiUpdatePaciente(id, payload) { return this.request(`/pacientes/${id}`, { method: "PUT", body: payload }); },
  async apiDeletePaciente(id) { return this.request(`/pacientes/${id}`, { method: "DELETE" }); },

  // =====================
  // 📅 CONSULTAS
  // =====================
  async apiGetConsultas(skip = 0, limit = 100) { return this.request(`/consultas?skip=${skip}&limit=${limit}`); },
  async apiGetConsultasPorPaciente(pacienteId) {
    try { return await this.request(`/consultas/paciente/${pacienteId}`); }
    catch { return this.request(`/consultas?paciente_id=${pacienteId}`); }
  },
  async apiCreateConsulta(payload) { return this.request("/consultas/", { method: "POST", body: payload }); },
  async apiUpdateConsulta(id, payload) { return this.request(`/consultas/${id}`, { method: "PUT", body: payload }); },
  async apiDeleteConsulta(id) { return this.request(`/consultas/${id}`, { method: "DELETE" }); },

  // =====================
  // 👩‍⚕️ USUÁRIOS
  // =====================
  async apiListUsuarios() { return this.request("/usuarios"); },
  async apiCreateUsuario(payload) { return this.request("/usuarios/", { method: "POST", body: payload }); },
  async apiUpdateUsuario(id, payload) { return this.request(`/usuarios/${id}`, { method: "PUT", body: payload }); },
  async apiDeleteUsuario(id) { return this.request(`/usuarios/${id}`, { method: "DELETE" }); },

  // =====================
  // 📤 UPLOADS
  // =====================
  /**
   * Upload de arquivo vinculado a um paciente
   * @param {number|string} pacienteId
   * @param {File} file
   */
  async uploadFile(pacienteId, file) {
    if (!pacienteId) throw new Error("pacienteId requerido");
    const fd = new FormData();
    fd.append("file", file);
    // Inclui o token automaticamente
    return this.request(`/uploads/${pacienteId}/upload`, { method: "POST", body: fd }, true);
  },
};

window.api = api;
