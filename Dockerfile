# 前端构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

# 生产阶段
FROM node:20-alpine AS runner

WORKDIR /app

# 从构建阶段复制构建产物
COPY --from=builder /app/.next/standalone ./app/.next/standalone

# 复制数据文件
COPY --from=builder /app/src/data ./app/src/data

# 暴露端口
EXPOSE 3000

# 启动应用
CMD ["node", "server.js"]
