FROM python:3.9-slim

WORKDIR /app

COPY websocket_to_loki.py /app/

RUN pip install --no-cache-dir websockets aiohttp

EXPOSE 8765

CMD ["python", "websocket_to_loki.py"] 