FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    iptables \
    iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ips.py /app/

CMD ["python", "-u", "ips.py"]
