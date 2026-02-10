# Build
FROM python:3.14-slim AS builder

RUN apt-get -y update && \
    apt-get -y --no-install-recommends install gettext && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

RUN pip install --upgrade pip

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/
RUN django-admin compilemessages

# Production
FROM python:3.14-slim
LABEL maintainer="Iván Moya Ortiz <ivn.moya@proton.me>" \
      version="1.0" \
      description="Aplicación web para la gestión de préstamos (taquillas, libros, etc) en la ETSIAE-UPM" \
      org.opencontainers.image.source="https://github.com/DA-ETSIAE/Prestamos"

RUN useradd -m -r appuser && \
   mkdir /app && \
   chown -R appuser /app

COPY --from=builder /usr/local/lib/python3.14/site-packages/ /usr/local/lib/python3.14/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/locale /app/locale

WORKDIR /app

COPY --chown=appuser:appuser . .
RUN chmod +x *.sh

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
