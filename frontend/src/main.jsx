import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './styles.css'

// 默认启用基于 HttpOnly Cookie 的刷新流程（更安全）
window.__USE_COOKIE_REFRESH__ = true

const root = createRoot(document.getElementById('root'))
root.render(<App />)
