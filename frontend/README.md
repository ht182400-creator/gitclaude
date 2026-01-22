React 前端脚手架（Vite）

快速启动（从仓库根目录）：

```powershell
cd frontend
npm install
npm run dev
```

在终端中会看到 Vite 的开发服务器地址。默认情况下前端会请求后端 `http://127.0.0.1:8000`。
如需更改后端地址，可在运行前设置环境变量 `VITE_API_BASE`：

```powershell
$env:VITE_API_BASE = 'http://127.0.0.1:8000'
npm run dev
```

示例功能：
- 从后端列出商品
- 创建简单订单（演示 API 调用）

下一步建议：
- 添加完整的认证流程（注册/登录），并将访问令牌与刷新令牌安全存储
- 添加购物车与结算页面

认证使用说明（演示）
- 使用 "注册" 创建用户，然后使用 "登录" 获取访问令牌。
- 前端将 `access_token` 存储在 `localStorage`（示例），并在需要时把令牌放入 `Authorization` 头部；生产环境应改用更安全的存储和传输机制（例如 HttpOnly Cookie）。
 
Auth usage:
- Use the "Sign Up" button to create a user, then "Login" to obtain an access token.
- The frontend will store the token in `localStorage` as `access_token` and include it in API requests.

Notes:
- This is a demo scaffold; production apps should handle token expiry securely, use HTTPS, and protect secrets.
