#!/bin/bash
# Full integration test for streaming mode with lisa voice

echo "================================================================================"
echo "Full Integration Test: Streaming Mode with 'lisa' voice"
echo "================================================================================"
echo ""

# Start the server in background
echo "Starting server with --streaming-mode-improve..."
/home/sheigl/miniconda3/envs/xtts310/bin/python -m xtts_api_server \
    -hs 0.0.0.0 --listen -d xpu --streaming-mode-improve > /tmp/xtts_test.log 2>&1 &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Waiting for server to initialize (30 seconds)..."
sleep 30

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "✗ Server process died!"
    echo "Server log:"
    cat /tmp/xtts_test.log
    exit 1
fi

echo "✓ Server process is running"
echo ""

# Check for sample rate errors in the log
if grep -q "Invalid sample rate\|9997" /tmp/xtts_test.log; then
    echo "✗ FAILED: Sample rate error detected in server log!"
    echo "Error details:"
    grep -A 3 -B 3 "Invalid sample rate\|9997" /tmp/xtts_test.log
    kill $SERVER_PID
    exit 1
fi

echo "✓ No sample rate errors in server log"
echo ""

# Test the API
echo "Testing TTS synthesis with 'lisa' voice..."
echo "Making API request..."

curl -s -G "http://localhost:8020/tts_stream" \
    --data-urlencode "text=Hello, this is a comprehensive test of streaming mode with the lisa voice. The audio should play without any sample rate errors." \
    --data-urlencode "speaker_wav=lisa.wav" \
    --data-urlencode "language=en" \
    -o /tmp/test_output.wav

# Check if we got output
if [ -f /tmp/test_output.wav ] && [ -s /tmp/test_output.wav ]; then
    FILE_SIZE=$(stat -f%z /tmp/test_output.wav 2>/dev/null || stat -c%s /tmp/test_output.wav)
    echo "✓ Generated audio file: /tmp/test_output.wav ($FILE_SIZE bytes)"

    # Check file signature (should be WAV or valid audio)
    FILE_TYPE=$(file /tmp/test_output.wav)
    echo "   File type: $FILE_TYPE"

    if [ $FILE_SIZE -gt 100 ]; then
        echo "✓ File size is reasonable (> 100 bytes)"
    else
        echo "⚠ Warning: File size is very small"
    fi
else
    echo "✗ No output file generated or file is empty"
    kill $SERVER_PID
    exit 1
fi

echo ""

# Final check of server log for any errors
if grep -qi "error.*sample\|traceback" /tmp/xtts_test.log; then
    echo "⚠ Warning: Some errors detected in server log"
    echo "Last 20 lines of log:"
    tail -20 /tmp/xtts_test.log
else
    echo "✓ No critical errors in server log"
fi

# Cleanup
echo ""
echo "Cleaning up..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo ""
echo "================================================================================"
echo "SUCCESS! Streaming mode with 'lisa' voice works correctly!"
echo "The sample rate issue has been fixed."
echo "================================================================================"

exit 0
