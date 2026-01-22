import React, { useState } from 'react'
import { signup } from './api'

export default function Signup({ onSignup }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fullName, setFullName] = useState('')
  const [loading, setLoading] = useState(false)

  const submit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await signup(email, password, fullName)
      onSignup(res)
    } catch (err) {
      alert('注册失败：' + err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={submit} style={{ marginBottom: 12 }}>
      <h3>注册</h3>
      <div>
        <input placeholder="姓名" value={fullName} onChange={(e) => setFullName(e.target.value)} />
      </div>
      <div>
        <input placeholder="邮箱" value={email} onChange={(e) => setEmail(e.target.value)} />
      </div>
      <div>
        <input placeholder="密码" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </div>
      <button type="submit" disabled={loading} style={{ marginTop: 8 }}>
        {loading ? '创建中...' : '注册'}
      </button>
    </form>
  )
}
