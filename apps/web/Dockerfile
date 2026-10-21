FROM node:lts AS builder

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN corepack enable \
    && corepack prepare pnpm@latest --activate \
    && pnpm config set global-bin-dir /pnpm

RUN pnpm install -g @moonrepo/cli

WORKDIR /app

COPY . .

RUN --mount=type=cache,target=/pnpm/store \
    pnpm install --frozen-lockfile --ignore-scripts

RUN moon run web:build

FROM gcr.io/distroless/nodejs22-debian13 AS runner

ENV NODE_ENV="production"
WORKDIR /app

COPY --from=builder /app/apps/web/.output /app/.output

EXPOSE 3000

CMD [ ".output/server/index.mjs" ]