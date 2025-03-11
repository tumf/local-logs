#!/usr/bin/env python3
import asyncio
import json
import logging
import os
import sys
from datetime import datetime

import aiohttp
import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger('websocket-to-loki')

# Configuration
WEBSOCKET_HOST = os.environ.get('WEBSOCKET_HOST', '0.0.0.0')
WEBSOCKET_PORT = int(os.environ.get('WEBSOCKET_PORT', 8765))
LOKI_URL = os.environ.get('LOKI_URL', 'http://loki:3100/loki/api/v1/push')

async def forward_to_loki(log_data):
    """Forward log data to Loki via HTTP API"""
    try:
        # If log_data is a string, try to parse it as JSON
        if isinstance(log_data, str):
            try:
                log_data = json.loads(log_data)
            except json.JSONDecodeError:
                # If it's not valid JSON, create a simple log entry
                timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                log_data = {
                    "streams": [
                        {
                            "stream": {
                                "source": "websocket",
                                "level": "info"
                            },
                            "values": [
                                [str(int(datetime.now().timestamp() * 1e9)), log_data]
                            ]
                        }
                    ]
                }
        
        # Ensure log_data has the correct format for Loki
        if not isinstance(log_data, dict) or "streams" not in log_data:
            timestamp = str(int(datetime.now().timestamp() * 1e9))
            log_data = {
                "streams": [
                    {
                        "stream": {
                            "source": "websocket",
                            "level": "info"
                        },
                        "values": [
                            [timestamp, json.dumps(log_data)]
                        ]
                    }
                ]
            }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                LOKI_URL,
                json=log_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 204:
                    response_text = await response.text()
                    logger.warning(f"Loki responded with status {response.status}: {response_text}")
                else:
                    logger.info("Successfully sent logs to Loki")
                return response.status
    except Exception as e:
        logger.error(f"Error forwarding to Loki: {str(e)}")
        return None

async def handle_websocket(websocket):
    """Handle WebSocket connections and messages"""
    client_id = id(websocket)
    logger.info(f"Client {client_id} connected from {websocket.remote_address}")
    
    try:
        async for message in websocket:
            logger.info(f"Received message from client {client_id}")
            
            # Forward the message to Loki
            status = await forward_to_loki(message)
            
            # Send acknowledgment back to the client
            await websocket.send(json.dumps({
                "status": "success" if status == 204 else "error",
                "timestamp": datetime.now().isoformat()
            }))
    except websockets.exceptions.ConnectionClosed as e:
        logger.info(f"Client {client_id} disconnected: {e}")
    except Exception as e:
        logger.error(f"Error handling message from client {client_id}: {str(e)}")
    finally:
        logger.info(f"Connection with client {client_id} closed")

async def main():
    """Start the WebSocket server"""
    logger.info(f"Starting WebSocket server on {WEBSOCKET_HOST}:{WEBSOCKET_PORT}")
    logger.info(f"Forwarding logs to Loki at {LOKI_URL}")
    
    async with websockets.serve(handle_websocket, WEBSOCKET_HOST, WEBSOCKET_PORT):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main()) 