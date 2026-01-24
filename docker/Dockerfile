FROM node:20-bullseye AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

COPY ../opt/oracle /opt/oracle
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_26:${LD_LIBRARY_PATH}
ENV ORACLE_CLIENT_LIB_DIR=/opt/oracle/instantclient_23_26
RUN apt-get update && apt-get install -y libaio1

# Build both Next.js and API server
RUN npm run build
RUN npm run server:build

FROM node:20-bullseye
WORKDIR /app

# Install Oracle Instant Client into the image.
# Prerequisite: download the Instant Client basic package and unpack it into
# an `instantclient_23_26` directory at the project root (same level as `app/`,
# `docker/`, etc.) before running `podman-compose build`.
#
# The build context for this Dockerfile is the project root (`..` in podman-compose),
# so this COPY brings that directory into the image at /opt/oracle/instantclient_23_26.
COPY ../opt/oracle /opt/oracle

# Ensure Oracle libraries are on the dynamic linker path and advertise the
# library directory to the app via ORACLE_CLIENT_LIB_DIR (used by app/lib/db/oracle.ts).
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_26:${LD_LIBRARY_PATH}
ENV ORACLE_CLIENT_LIB_DIR=/opt/oracle/instantclient_23_26

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=builder /app ./

RUN apt-get update && apt-get install -y libaio1

ENV NODE_ENV=production
# Internal container ports (mapped to 3002/3003 on the host via podman-compose)
EXPOSE 3000 3001

# Run both servers in production mode (uses compiled assets from build stage)
CMD ["npm", "run", "start:all"]

