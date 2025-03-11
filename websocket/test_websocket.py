#!/usr/bin/env python3
import asyncio
import os
import time

from playwright.async_api import async_playwright


async def test_websocket_connection():
    """Test WebSocket connection using Playwright"""
    print("Starting WebSocket connection test...")
    
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Enable console logs
        page = await context.new_page()
        page.on("console", lambda msg: print(f"BROWSER LOG: {msg.text}"))
        
        # Open the WebSocket client page
        file_path = os.path.abspath("websocket/websocket_client_example.html")
        await page.goto(f"file://{file_path}")
        
        print("Page loaded. Testing direct connection to WebSocket server...")
        
        # Test direct connection (ws://localhost:9023)
        await page.fill("#wsUrl", "ws://localhost:9023")
        await page.click("#connectBtn")
        
        # Wait for connection status to change
        await asyncio.sleep(2)
        
        # Check connection status
        status_text = await page.text_content("#connectionStatus")
        print(f"Connection status (direct): {status_text}")
        
        # If connected, try sending a log
        if "Connected" in status_text:
            print("Connected successfully! Sending a test log...")
            await page.click("#sendLogBtn")
            await asyncio.sleep(1)
            print("Log sent. Check WebSocket server logs for details.")
        else:
            print("Failed to connect directly. Testing proxy connection...")
            
            # Disconnect if needed
            if await page.is_enabled("#disconnectBtn"):
                await page.click("#disconnectBtn")
                await asyncio.sleep(1)
            
            # Test proxy connection (ws://localhost:9020/ws/)
            await page.fill("#wsUrl", "ws://localhost:9020/ws/")
            await page.click("#connectBtn")
            
            # Wait for connection status to change
            await asyncio.sleep(2)
            
            # Check connection status
            status_text = await page.text_content("#connectionStatus")
            print(f"Connection status (proxy): {status_text}")
            
            # If connected, try sending a log
            if "Connected" in status_text:
                print("Connected successfully via proxy! Sending a test log...")
                await page.click("#sendLogBtn")
                await asyncio.sleep(1)
                print("Log sent. Check WebSocket server logs for details.")
            else:
                print("Failed to connect via proxy as well.")
        
        # Keep the browser open for a while to see the results
        print("Test completed. Browser will close in 10 seconds...")
        await asyncio.sleep(10)
        
        # Close browser
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_websocket_connection()) 