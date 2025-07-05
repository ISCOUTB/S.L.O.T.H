FROM node:22.16.0-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json /app/

RUN npm install --omit dev

COPY ./src /app/src

FROM node:22.16.0-alpine AS runner

WORKDIR /app

COPY --from=builder /app/node_modules /app/node_modules
COPY --from=builder /app /app

CMD ["npm", "start"]
