FROM node:20-bullseye-slim

WORKDIR /app

ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
ENV NODE_ENV=development

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npx prisma generate --schema=src/providers/schema.prisma || true

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]
