FROM python:3.11-slim

WORKDIR /app

COPY infusion-pump-emulator.py /app/

# This emulator deliberately exposes the constraints of an Archetype 2 device:
#   - Hardcoded service credentials (no per-user accounts)
#   - Cleartext HL7 v2 (no TLS)
#   - No audit logging on the device itself
#   - Vulnerable simulated protocol parser
# These constraints are the test surface for compensating-control evaluation.

EXPOSE 2575 8080

HEALTHCHECK --interval=5s --timeout=3s --retries=5 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', 8080))"

CMD ["python", "-u", "infusion-pump-emulator.py"]
