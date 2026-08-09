# Multi-stage. Compose picks a stage with `target:` —
#   docker-compose.yml      -> target: dev        (hot reload, no build step)
#   docker-compose.prod.yml -> target: production (optimized build)

FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install


# ── Development: hot reload, reads env vars at runtime ──────────────────────
FROM deps AS dev
WORKDIR /app
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--hostname", "0.0.0.0"]


# ── Build stage for production ───────────────────────────────────────────────
FROM deps AS builder
WORKDIR /app
COPY . .
# NEXT_PUBLIC_* values are inlined into the client bundle at BUILD time, so this
# has to be a build arg — setting it only at runtime would have no effect.
ARG NEXT_PUBLIC_API_URL=http://localhost:5000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build


# ── Production: optimized build served by next start ─────────────────────────
FROM node:20-alpine AS production
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.ts ./next.config.ts
EXPOSE 3000
CMD ["npm", "start", "--", "--hostname", "0.0.0.0"]
