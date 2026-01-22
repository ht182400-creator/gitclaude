import React, { useState } from 'react'
import { login } from './api'

export default function Login({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await login(email, password)
      onLogin(res)
    } catch (err) {
      alert('登录失败：' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} style={{ marginBottom: 12 }}>
      <h3>登录</h3>
      <div>
        <input placeholder="邮箱" value={email} onChange={(e) => setEmail(e.target.value)} />
      </div>
      <div>
        <input placeholder="密码" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </div>
      <button type="submit" disabled={loading} style={{ marginTop: 8 }}>
        {loading ? '登录中...' : '登录'}
      </button>
    </form>
  )
}
