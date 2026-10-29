FROM node:22-alpine AS builder

ENV NODE_ENV="production"
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN npm install --global pnpm@12.16.1

WORKDIR /workspace

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml /workspace/
COPY apps/backend/parsers/formula-parser /workspace/apps/backend/parsers/formula-parser/
COPY packages/proto-utils/proto-utils-js /workspace/packages/proto-utils/proto-utils-js/
COPY tools/eslint /workspace/tools/eslint/
COPY tools/tsconfig /workspace/tools/tsconfig/

RUN --mount=type=cache,target=/pnpm/store \
    pnpm install --frozen-lockfile --ignore-scripts

RUN pnpm --filter @sloth/packages-proto-utils-js exec tsup
RUN pnpm install --force --frozen-lockfile --ignore-scripts
RUN pnpm --filter @etl-design/apps-formula-parser build

FROM node:22-alpine AS runner

ENV NODE_ENV="production"
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

RUN npm install --global pnpm@12.16.1

WORKDIR /app

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml /app/
COPY apps/backend/parsers/formula-parser/package.json /app/apps/backend/parsers/formula-parser/package.json
COPY --from=builder /workspace/apps/backend/parsers/formula-parser/dist /app/apps/backend/parsers/formula-parser/dist
COPY --from=builder /workspace/packages/proto-utils/proto-utils-js /app/packages/proto-utils/proto-utils-js/
COPY tools/eslint /app/tools/eslint/
COPY tools/tsconfig /app/tools/tsconfig/

RUN --mount=type=cache,target=/pnpm/store \
    pnpm install --prod --frozen-lockfile --ignore-scripts

CMD ["node", "apps/backend/parsers/formula-parser/dist/server.cjs"]