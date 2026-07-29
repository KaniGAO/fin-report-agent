# ---- 阶段1：构建前端 ----
FROM node:20-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- 阶段2：运行后端（同时同源托管前端）----
FROM python:3.11-slim
WORKDIR /app
COPY backend/ /app/backend/
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8080

# 云平台（Render / Railway）会注入 PORT 环境变量；兜底 8080
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
