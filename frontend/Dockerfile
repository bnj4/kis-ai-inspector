FROM node:22-bookworm-slim
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY . .
RUN npm run build
ENV NODE_ENV=production
CMD ["sh", "-c", "exec npm run start -- --hostname 0.0.0.0 --port ${PORT:-3000}"]
