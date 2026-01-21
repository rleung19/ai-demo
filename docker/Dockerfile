FROM node:20-bullseye AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-bullseye
WORKDIR /app

# Install Oracle Instant Client into the image.
# Prerequisite: download the Instant Client basic package and unpack it into
# an `instantclient_23_3` directory at the project root (same level as `app/`,
# `docker/`, etc.) before running `podman-compose build`.
#
# The build context for this Dockerfile is the project root (`..` in podman-compose),
# so this COPY brings that directory into the image at /opt/oracle/instantclient_23_3.
COPY instantclient_23_3 /opt/oracle/instantclient_23_3

# Ensure Oracle libraries are on the dynamic linker path and advertise the
# library directory to the app via ORACLE_CLIENT_LIB_DIR (used by app/lib/db/oracle.ts).
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_23_3:${LD_LIBRARY_PATH}
ENV ORACLE_CLIENT_LIB_DIR=/opt/oracle/instantclient_23_3

COPY package*.json ./
RUN npm ci --omit=dev

COPY --from=builder /app ./

ENV NODE_ENV=production
# Internal container ports (mapped to 4000/4001 on the host via podman-compose)
EXPOSE 3000 3001

CMD ["npm", "run", "start-all"]

