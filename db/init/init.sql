version: '3.8'

services:
  db:
    image: timescale/timescaledb:2.19.3-pg14
    container_name: timescaledb
    restart: always
    env_file: .env
    ports:
      - "5432:5432"
    volumes:
      - ./db/data:/var/lib/postgresql/data
      - ./db/init:/docker-entrypoint-initdb.d
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}

  grafana:
    image: grafana/grafana
    container_name: grafana
    restart: always
    ports:
      - "3000:3000"
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      GF_SECURITY_ADMIN_USER: admin
      GF_SECURITY_ADMIN_PASSWORD: admin
