FROM node:20-bullseye-slim AS builder

WORKDIR /app
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Copy package files and install all dependencies for build
COPY frontend/package*.json ./
RUN npm ci

# Copy source code and build the application
COPY frontend/ ./
RUN npx prisma generate --schema=src/providers/schema.prisma || true
RUN npm run build

FROM node:20-bullseye-slim AS runner

WORKDIR /app
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Install only production dependencies for runtime
COPY frontend/package*.json ./

# Copy node_modules built in builder to avoid re-installing in runner (speeds up and avoids I/O issues)
COPY --from=builder /app/node_modules ./node_modules

# Copy built app and public assets
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["npm", "start"]