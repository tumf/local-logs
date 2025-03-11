# Local Logs Monitoring System

A local monitoring system using Grafana and Loki for log aggregation and visualization.

## Overview

This project sets up a local environment for collecting, storing, and visualizing logs using:

- **Grafana**: For visualization and dashboards
- **Loki**: For log aggregation and querying
- **Nginx**: As a reverse proxy to access services
- **WebSocket Server**: For sending logs to Loki via WebSocket

## Prerequisites

- Docker and Docker Compose
- Git

## Getting Started

### Installation

#### 1. Clone this repository

```bash
git clone https://github.com/yourusername/local-logs.git
cd local-logs
```

#### 2. Start the services

```bash
docker-compose up -d
```

### Accessing the Services

- **Grafana**: http://localhost:9021 or http://localhost:9020/
- **Loki**: http://localhost:9022 or http://localhost:9020/loki
- **WebSocket**: ws://localhost:9023 or ws://localhost:9020/ws/

## Configuration

### Docker Compose

The `docker-compose.yaml` file defines the following services:

- **Grafana**: Visualization platform
- **Loki**: Log aggregation system
- **WebSocket**: Server for sending logs to Loki via WebSocket
- **Nginx**: Reverse proxy for accessing services

### Nginx Configuration

Nginx is configured to proxy requests to Grafana, Loki, and the WebSocket server, allowing access through a single port.

### Adding Loki as a Data Source in Grafana

To configure Loki as a data source in Grafana:

1. Log in to Grafana (default credentials: admin/admin)
2. Go to **Configuration** > **Data Sources**
3. Click **Add data source**
4. Select **Loki** from the list
5. Configure the data source:
   - **Name**: Loki
   - **URL**:

     - If using direct access: `http://loki:3100`

     - If using Nginx proxy: `http://localhost:9020/loki`

   - Leave other settings as default
6. Click **Save & Test** to verify the connection

If you're using Docker Compose networking, the internal URL `http://loki:3100` is recommended as it uses Docker's internal DNS.

## Usage

### Sending Logs to Loki via HTTP API

You can send logs to Loki using various clients like Promtail, Fluentd, or directly via the HTTP API.

Example using curl:

```bash
curl -X POST -H "Content-Type: application/json" -d '{
  "streams": [
    {
      "stream": {
        "app": "test-app"
      },
      "values": [
        ["1609455600000000000", "test log message"]
      ]
    }
  ]
}' http://localhost:9022/loki/api/v1/push
```

### Sending Logs to Loki via WebSocket

You can also send logs to Loki via WebSocket, which can be useful for web applications or scenarios where maintaining a persistent connection is beneficial.

#### WebSocket URL

- Direct access: `ws://localhost:9023`
- Via Nginx proxy: `ws://localhost:9020/ws/`

#### WebSocket Message Format

The WebSocket server accepts messages in the following formats:

1. **Simple text message**: The server will convert it to Loki format with default labels.

2. **JSON object**: The server will attempt to convert it to Loki format.

3. **Loki format**: You can send data directly in Loki format:

```json
{
  "streams": [
    {
      "stream": {
        "app": "my-app",
        "level": "info"
      },
      "values": [
        ["1609455600000000000", "This is a log message"]
      ]
    }
  ]
}
```

#### Example WebSocket Client

An example HTML/JavaScript client is provided in the `websocket/websocket_client_example.html` file. Open this file in a browser to test sending logs via WebSocket.

### Querying Logs in Grafana

1. Log in to Grafana
2. Add Loki as a data source (if not already configured)
3. Create a new dashboard or use the "Explore" feature
4. Use LogQL to query your logs, e.g.,  `{app="test-app"}` or `{source="websocket"}`

## Troubleshooting

- If services are not accessible, check Docker container status:

```bash
docker-compose ps
```

- View logs for specific services:

```bash
docker-compose logs grafana
docker-compose logs loki
docker-compose logs websocket
docker-compose logs nginx
```

## Project Structure

```
local-logs/
├── docker-compose.yaml    # Docker Compose configuration
├── nginx.conf            # Nginx configuration
├── README.md             # This documentation
└── websocket/            # WebSocket related files
    ├── Dockerfile.websocket      # Dockerfile for WebSocket server
    ├── websocket_to_loki.py      # WebSocket server implementation
    └── websocket_client_example.html  # Example WebSocket client
```

## License

MIT
