const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

function authHeaders() {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function listProducts() {
  const res = await fetch(`${API_BASE}/products/`)
  if (!res.ok) throw new Error('加载商品失败')
  return res.json()
}

export async function createOrder(userId, items) {
  const res = await fetchWithAuth(`${API_BASE}/orders/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '下单失败' }))
    throw new Error(err.detail || '下单失败')
  }
  return res.json()
}

export async function signup(email, password, full_name) {
  const res = await fetch(`${API_BASE}/users/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, full_name }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '注册失败' }))
    throw new Error(err.detail || '注册失败')
  }
  return res.json()
}

export async function login(email, password) {
  // By default use JSON token flow. To use HttpOnly cookie refresh flow, pass header 'x-use-cookie': '1' and set includeCookie flag.
  const useCookie = !!(window && window.__USE_COOKIE_REFRESH__)
  const opts = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  }
  if (useCookie) {
    opts.headers['x-use-cookie'] = '1'
    opts.credentials = 'include'
  }
  const res = await fetch(`${API_BASE}/users/login`, opts)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: '登录失败' }))
    throw new Error(err.detail || '登录失败')
  }
  const data = await res.json()
  // backend returns { access_token: '...' }
  if (data.access_token) {
    localStorage.setItem('access_token', data.access_token)
  }
  if (data.refresh_token) {
    localStorage.setItem('refresh_token', data.refresh_token)
  }
  return data
}

export function logout() {
  const refresh = localStorage.getItem('refresh_token')
  if (refresh) {
    // best-effort revoke on server
    fetch(`${API_BASE}/users/logout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
      credentials: 'include',
    }).catch(() => {})
  } else {
    // try cookie-based logout
    fetch(`${API_BASE}/users/logout`, { method: 'POST', credentials: 'include' }).catch(() => {})
  }
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export async function refreshToken() {
  const refresh = localStorage.getItem('refresh_token')
  if (!refresh) throw new Error('No refresh token')
  const res = await fetch(`${API_BASE}/users/refresh`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: refresh }),
  })
  if (!res.ok) {
    // clear tokens on failure
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    throw new Error('Failed to refresh token')
  }
  const data = await res.json()
  if (data.access_token) localStorage.setItem('access_token', data.access_token)
  if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token)
  return data
}

async function fetchWithAuth(input, init = {}) {
  const headers = init.headers ? { ...init.headers } : {}
  const token = localStorage.getItem('access_token')
  if (token) headers.Authorization = `Bearer ${token}`
  let res = await fetch(input, { ...init, headers })
  if (res.status === 401) {
    try {
      await refreshToken()
      const newToken = localStorage.getItem('access_token')
      if (newToken) headers.Authorization = `Bearer ${newToken}`
      res = await fetch(input, { ...init, headers })
    } catch (err) {
      throw err
    }
  }
  return res
}
