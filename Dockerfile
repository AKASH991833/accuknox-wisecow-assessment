FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends fortune-mod cowsay fortunes-min \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --system --uid 10001 --create-home wisecow
ENV PATH="/usr/games:${PATH}" PORT=4499 PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --chown=10001:10001 server.py wisecow.sh ./
USER 10001:10001
EXPOSE 4499
CMD ["python", "server.py"]
