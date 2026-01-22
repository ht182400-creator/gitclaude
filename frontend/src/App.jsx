import React, { useEffect, useState } from 'react'
import { listProducts, createOrder, logout as apiLogout } from './api'
import Login from './Login'
import Signup from './Signup'

export default function App() {
  const [products, setProducts] = useState([])
  const [token, setToken] = useState(() => localStorage.getItem('access_token'))
  const [view, setView] = useState('products')

  useEffect(() => {
    listProducts().then(setProducts).catch(console.error)
  }, [])

  const buy = async (productId) => {
    try {
      const res = await createOrder(1, [{ product_id: productId, quantity: 1 }])
      alert(`Order created: ${JSON.stringify(res)}`)
    } catch (err) {
      alert('Order failed: ' + err.message)
    }
  }

  function handleLogout() {
    apiLogout()
    setToken(null)
  }

  function handleLoginSuccess(res) {
    setToken(localStorage.getItem('access_token'))
    setView('products')
    // optionally refresh products or user info
  }

  function handleSignupSuccess() {
    alert('注册成功 — 请登录')
    setView('login')
  }

  return (
    <div style={{ padding: 20 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between' }}>
        <h1>电商前端（示例）</h1>
        <div>
          {token ? (
            <>
              <button onClick={() => setView('products')} style={{ marginRight: 8 }}>
                商品
              </button>
              <button onClick={handleLogout}>登出</button>
            </>
          ) : (
            <>
              <button onClick={() => setView('login')} style={{ marginRight: 8 }}>
                登录
              </button>
              <button onClick={() => setView('signup')}>注册</button>
            </>
          )}
        </div>
      </header>

      {view === 'login' && <Login onLogin={handleLoginSuccess} />}
      {view === 'signup' && <Signup onSignup={handleSignupSuccess} />}

      {view === 'products' && (
        <ul>
          {products.map((p) => (
            <li key={p.id} style={{ marginBottom: 8 }}>
              <strong>{p.name}</strong> — ${(p.price_cents / 100).toFixed(2)} — 库存: {p.inventory}
              <button onClick={() => buy(p.id)} style={{ marginLeft: 10 }}>
                购买 1
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
