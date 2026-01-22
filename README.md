 # 电商平台（脚手架）

 本工作区包含一个简易的在线电商平台脚手架，便于快速演示用户注册、商品、订单与简单支付流程。

 目录结构
 - `backend/`：基于 FastAPI 的后端（含认证、商品、订单），使用 SQLite 作为示例数据库
 - `frontend/`：前端示例（Vite + React），包含基本的登录/注册和购买演示

 快速启动（后端示例）

 ```powershell
 # 从仓库根目录进入
 cd backend
 python -m venv .venv
 .\.venv\Scripts\Activate.ps1
 pip install -r requirements.txt
 uvicorn app.main:app --reload --port 8000
 ```

 在浏览器打开 API 文档： http://127.0.0.1:8000/docs

 下一步建议
 - 为生产环境完善认证和支付集成（例如使用 Stripe、支付宝或微信支付）
 - 将刷新令牌与会话管理、安全策略（HTTPS、HttpOnly Cookie）并入部署流程
 - 添加前端完整的购物车与结算页面

 安全注意（发布前必须处理）
 - 使用 HTTPS，刷新令牌应通过 `HttpOnly` + `Secure` 的 Cookie 存储或安全的存储策略；服务端仅保存令牌标识哈希。
 - 在生产环境使用 Redis 等共享存储进行分布式限流与会话管理，避免内存限流的单点限制。
 - 为用户会话与令牌活动添加审计与监控，检测异常登录或令牌滥用。
 
 使用 Docker Compose（可选）
 - 仓库根目录包含 `docker-compose.yml`，可用于快速启动 Redis 和后端：
 
 ```powershell
 docker compose up --build
 ```
 
 - 这会把 `backend` 服务绑定到 `http://localhost:8000`，并将 `REDIS_URL` 环境变量指向 Compose 中的 `redis` 服务。
 - 开发时 `dev.db` 将被创建在 `backend` 目录下；如果更改模型请删除 `backend/dev.db` 以便在下次启动时重建表。
 
Security notes (important before production):
- Use HTTPS for all requests and set cookies with `Secure` and `HttpOnly` for refresh tokens.
- Store only hashed identifiers for refresh tokens server-side (done in backend).
- Use a shared store (Redis) for rate limiting in production instead of in-memory limits.
- Rotate and revoke refresh tokens on use or logout; consider storing additional metadata (user agent, IP) for detection.
