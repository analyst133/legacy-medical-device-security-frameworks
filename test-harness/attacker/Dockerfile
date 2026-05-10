FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 \
    iputils-ping \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY scenarios/ /app/scenarios/
COPY runner.py /app/

CMD ["sleep", "infinity"]
