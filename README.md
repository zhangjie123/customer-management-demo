# CUSTOMER_MANAGEMENT_DEMO

Python + React demo for managing customer profiles (姓名 / 联系电话 / 性别) backed by MySQL.

## 数据库

- 已假设存在数据库：`customer_demo`（Host: localhost, 用户/密码: root/root）
- 建表语句位于 `sql/create_customers.sql`，后端启动时也会自动创建表与索引。
- 手动执行示例（可在终端运行）：  
  ```bash
  mysql -h localhost -u root -proot customer_demo < sql/create_customers.sql
  ```

## 后端 (Flask)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/app.py  # 默认监听 0.0.0.0:5000
```

可用环境变量：`DB_HOST`, `DB_PORT` (默认 8889), `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `PORT`。

## 前端 (React + Vite)

```bash
cd frontend
npm install
npm run dev   # 默认 http://localhost:5173
```

默认会请求 `http://localhost:5000/api/...`，如需调整可在前端启动时设置 `VITE_API_BASE` 环境变量。
