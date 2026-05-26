# Multi-stage build for Backend Node.js
FROM node:20-alpine AS base
WORKDIR /app
COPY package*.json ./

FROM base AS deps
RUN npm ci

FROM base AS runner
COPY --from=deps /app/node_modules ./node_modules
COPY . .

ENV NODE_ENV=production
ENV PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:8000/health', (res) => res.statusCode === 200 ? process.exit(0) : process.exit(1))"

# Usar exec form para asegurar que las señales (SIGTERM) se propaguen correctamente al proceso node
ENTRYPOINT ["node"]
CMD ["server.js"]