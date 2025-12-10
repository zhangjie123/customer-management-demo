# CUSTOMER_MANAGEMENT_DEMO

Python + React 客户档案管理（姓名/联系电话/性别），后端使用 Flask + MySQL，前端使用 React + Vite。

## 快速开始

### 1) MySQL
- 已有数据库：`customer_demo`（Host: localhost，Port: 8889，用户/密码: root/root）
- 建表脚本：`sql/create_customers.sql`
- 手动建表：
  ```bash
  mysql -h localhost -P 8889 -u root -proot customer_demo < sql/create_customers.sql
  ```

### 2) 后端 (Flask)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/app.py   # 默认 0.0.0.0:5000
```
环境变量可选：`DB_HOST` (默认 localhost), `DB_PORT` (默认 8889), `DB_USER`/`DB_PASSWORD` (默认 root/root), `DB_NAME` (默认 customer_demo), `PORT`。

### 3) 前端 (React + Vite)
```bash
cd frontend
npm install
npm run dev   # 默认 http://localhost:5173
```
如需修改后端地址，启动前设置 `VITE_API_BASE`（默认 `http://localhost:5000`）。
