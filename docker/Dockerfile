FROM node:20-bullseye AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-bullseye
WORKDIR /app

# TODO: Install Oracle Instant Client in this image and set LD_LIBRARY_PATH appropriately.
# Example (pseudo-steps, to be filled in with your preferred install method):
# COPY instantclient_23_3 /opt/oracle/instantclient_23_3
# ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_3:${LD_LIBRARY_PATH}

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=builder /app ./

ENV NODE_ENV=production
# Internal container ports (mapped to 4000/4001 on the host via podman-compose)
EXPOSE 3000 3001

CMD ["npm", "run", "start-all"]

