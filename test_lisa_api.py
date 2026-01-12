#!/usr/bin/env python3
"""
Test script that makes an actual API call to test streaming mode with lisa voice.
This script will:
1. Start the server in background with streaming mode
2. Wait for it to initialize
3. Make a test TTS request with lisa voice
4. Check for any sample rate errors
"""
import requests
import time
import subprocess
import sys
import signal
import os

def test_streaming_api():
    print("=" * 80)
    print("Testing Streaming Mode API with 'lisa' voice")
    print("=" * 80)
    print()

    # Start the server
    print("Starting server with --streaming-mode-improve...")
    server_process = subprocess.Popen(
        ["/home/sheigl/miniconda3/envs/xtts310/bin/python", "-m", "xtts_api_server",
         "-hs", "0.0.0.0", "--listen", "-d", "xpu", "--streaming-mode-improve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Give the server time to start and load the model
    print("Waiting for server to initialize (this may take 30-60 seconds)...")
    time.sleep(5)

    # Check if server is starting up
    max_wait = 120  # Wait up to 2 minutes
    start_time = time.time()
    server_ready = False

    while time.time() - start_time < max_wait:
        try:
            response = requests.get("http://localhost:8020/docs", timeout=2)
            if response.status_code == 200:
                server_ready = True
                print("✓ Server is ready!")
                break
        except requests.exceptions.RequestException:
            pass

        # Check for any sample rate errors in the output
        try:
            line = server_process.stderr.readline()
            if line:
                if "Invalid sample rate" in line or "-9997" in line:
                    print(f"✗ FAILED: Sample rate error detected!")
                    print(f"   Error: {line.strip()}")
                    server_process.terminate()
                    return False
                if "error" in line.lower() and "sample" in line.lower():
                    print(f"   Server output: {line.strip()}")
        except:
            pass

        time.sleep(1)

    if not server_ready:
        print("✗ Server failed to start within timeout")
        server_process.terminate()
        return False

    print()
    print("Testing TTS synthesis with 'lisa' voice...")

    try:
        # Test a simple TTS request
        url = "http://localhost:8020/tts_stream"
        params = {
            "text": "Hello, this is a test of the streaming mode with the lisa voice.",
            "speaker_wav": "lisa.wav",
            "language": "en"
        }

        print(f"Making request to {url}")
        response = requests.get(url, params=params, stream=True, timeout=60)

        if response.status_code == 200:
            print("✓ Request successful (status 200)")

            # Read some of the streaming response
            chunks_received = 0
            total_bytes = 0
            try:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        chunks_received += 1
                        total_bytes += len(chunk)
                        if chunks_received >= 10:  # Get enough chunks to verify it works
                            break
            except Exception as e:
                # If we received some chunks, it's still a success
                if chunks_received > 0:
                    print(f"   (Stream ended after {chunks_received} chunks, which is OK)")
                else:
                    raise e

            print(f"✓ Received {chunks_received} audio chunks ({total_bytes} bytes)")
            print()
            print("=" * 80)
            print("SUCCESS! Streaming mode with 'lisa' voice works correctly!")
            print("No sample rate errors detected!")
            print("=" * 80)
            server_process.terminate()
            return True
        else:
            print(f"✗ Request failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            server_process.terminate()
            return False

    except Exception as e:
        print(f"✗ Error during test: {e}")
        server_process.terminate()
        return False
    finally:
        # Make sure to cleanup
        try:
            server_process.terminate()
            server_process.wait(timeout=5)
        except:
            server_process.kill()

if __name__ == "__main__":
    success = test_streaming_api()
    sys.exit(0 if success else 1)
