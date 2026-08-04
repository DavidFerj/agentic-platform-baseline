FROM node:24.14.0-bookworm-slim AS dependencies

ENV PNPM_HOME="/pnpm"
ENV PATH="${PNPM_HOME}:${PATH}"
RUN corepack enable && corepack prepare pnpm@11.9.0 --activate

WORKDIR /workspace
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY frontend/package.json frontend/package.json
COPY gcp/packages/contracts/package.json gcp/packages/contracts/package.json
RUN pnpm install --frozen-lockfile --filter @agentic-platform/web...

FROM dependencies AS builder
COPY frontend frontend
RUN pnpm --filter @agentic-platform/web build

FROM gcr.io/distroless/nodejs24-debian13:nonroot@sha256:fbbdda866ea71aef98c4abece17e3d61fbf820cc2ef3961522caa2478716171a AS runner
ENV NODE_ENV=production

WORKDIR /app
COPY --from=builder --chown=nonroot:nonroot /workspace/frontend/.next/standalone ./
COPY --from=builder --chown=nonroot:nonroot /workspace/frontend/.next/static ./frontend/.next/static

USER nonroot
EXPOSE 3000
ENV PORT=3000 HOSTNAME=0.0.0.0

CMD ["frontend/server.js"]
