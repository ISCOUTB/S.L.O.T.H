FROM alpine:latest AS workspace

WORKDIR /workspace

COPY pnpm-lock.yaml pnpm-workspace.yaml /workspace/
COPY apps/backend/parsers/formula-parser /workspace/apps/backend/parsers/formula-parser
COPY packages/proto-utils/proto-utils-js /workspace/packages/utils
COPY tools/eslint /workspace/tools/eslint
COPY tools/tsconfig /workspace/tools/tsconfig
COPY .moon /workspace/.moon

FROM node:lts-alpine AS builder

ENV NODE_ENV="production"
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

RUN pnpm install -g @moonrepo/cli

WORKDIR /app

COPY --from=workspace /workspace /app/

RUN pnpm i --force

RUN moon formula-parser:build

FROM node:lts-alpine AS runner

ENV NODE_ENV="production"

WORKDIR /app

COPY --from=builder /app/apps/backend/parsers/formula-parser/dist /app/dist

CMD [ "node", "dist/server.cjs" ]