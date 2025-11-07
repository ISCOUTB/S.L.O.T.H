FROM alpine:latest AS workspace

WORKDIR /workspace

COPY pnpm-lock.yaml pnpm-workspace.yaml /workspace/
COPY apps/backend/parsers/formula-parser /workspace/apps/backend/parsers/formula-parser/  
COPY packages/proto-utils/proto-utils-js /workspace/packages/proto-utils/proto-utils-js/
COPY tools/eslint /workspace/tools/eslint/
COPY tools/tsconfig /workspace/tools/tsconfig/
COPY .moon /workspace/.moon/

FROM node:lts-alpine AS builder

ENV NODE_ENV="production"
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

RUN pnpm install -g @moonrepo/cli

WORKDIR /app

COPY --from=workspace /workspace /app/

RUN --mount=type=cache,target=/app/.pnpm \
    pnpm i

RUN moon formula-parser:build

FROM node:lts-alpine AS runner

ENV NODE_ENV="production"
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

COPY --from=builder /app/apps/backend/parsers/formula-parser/dist /app/dist

COPY --from=builder /app/packages /app/packages/
COPY --from=builder /app/tools /app/tools/
COPY --from=builder /app/apps/backend/parsers/formula-parser/package.json /app/package.json
COPY --from=builder /app/pnpm-lock.yaml /app/pnpm-lock.yaml
COPY --from=builder /app/pnpm-workspace.yaml /app/pnpm-workspace.yaml

RUN --mount=type=cache,target=/app/.pnpm \
    pnpm i --prod

CMD [ "node", "dist/server.js" ]