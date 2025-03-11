# Local Logs Monitoring System

A local monitoring system using Grafana and Loki for log aggregation and visualization.

## Overview

This project sets up a local environment for collecting, storing, and visualizing logs using:

- **Grafana**: For visualization and dashboards
- **Loki**: For log aggregation and querying
- **Nginx**: As a reverse proxy to access services

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

- **Grafana**: http://localhost:9011 or http://localhost:8020/grafana
- **Loki**: http://localhost:9012 or http://localhost:8020/loki

## Configuration

### Docker Compose

The `docker-compose.yaml` file defines the following services:

- **Grafana**: Visualization platform
- **Loki**: Log aggregation system
- **Nginx**: Reverse proxy for accessing services

### Nginx Configuration

Nginx is configured to proxy requests to both Grafana and Loki, allowing access through a single port.

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

     - If using Nginx proxy: `http://localhost:8020/loki`

   - Leave other settings as default
6. Click **Save & Test** to verify the connection

If you're using Docker Compose networking, the internal URL `http://loki:3100` is recommended as it uses Docker's internal DNS.

## Usage

### Sending Logs to Loki

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
}' http://localhost:9012/loki/api/v1/push
```

### Querying Logs in Grafana

1. Log in to Grafana
2. Add Loki as a data source (if not already configured)
3. Create a new dashboard or use the "Explore" feature
4. Use LogQL to query your logs, e.g., `{app="test-app"}`

## Troubleshooting

- If services are not accessible, check Docker container status:

```bash
docker-compose ps
```

- View logs for specific services:

```bash
docker-compose logs grafana
docker-compose logs loki
docker-compose logs nginx
```

## License

MIT
