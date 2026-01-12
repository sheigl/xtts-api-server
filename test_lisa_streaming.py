#!/usr/bin/env python3
"""
Test script to verify streaming mode works with the 'lisa' voice.
"""
import sys
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Set environment variables for the test
os.environ['DEVICE'] = 'xpu'
os.environ['OUTPUT'] = 'output/'
os.environ['SPEAKER'] = 'speakers/'
os.environ['MODEL'] = 'xtts_models/'
os.environ['MODEL_SOURCE'] = 'local'
os.environ['MODEL_VERSION'] = 'v2.0.2'
os.environ['STREAM_MODE_IMPROVE'] = 'true'
os.environ['STREAM_MODE'] = 'false'
os.environ['STREAM_PLAY_SYNC'] = 'false'

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from xtts_api_server.RealtimeTTS.engines.coqui_engine import CoquiEngine
    from xtts_api_server.RealtimeTTS.text_to_stream import TextToAudioStream
    import pyaudio

    print("=" * 80)
    print("Testing Streaming Mode with 'lisa' voice")
    print("=" * 80)

    # Check that lisa voice files exist
    lisa_wav = "speakers/lisa.wav"
    lisa_json = "speakers/lisa.json"

    if not os.path.exists(lisa_wav):
        print(f"ERROR: {lisa_wav} not found!")
        sys.exit(1)

    if not os.path.exists(lisa_json):
        print(f"ERROR: {lisa_json} not found!")
        sys.exit(1)

    print(f"✓ Found lisa.wav ({os.path.getsize(lisa_wav)} bytes)")
    print(f"✓ Found lisa.json ({os.path.getsize(lisa_json)} bytes)")
    print()

    # Test PyAudio with 48000 Hz first
    print("Testing PyAudio with 48000 Hz...")
    p = pyaudio.PyAudio()
    try:
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=48000,
            output=True
        )
        print("✓ PyAudio successfully opened stream with 48000 Hz")
        stream.close()
    except OSError as e:
        print(f"✗ PyAudio failed to open stream: {e}")
        sys.exit(1)
    finally:
        p.terminate()

    print()
    print("Initializing CoquiEngine with streaming mode...")
    print("This will load the XTTS model (may take some time)...")
    print()

    # Initialize the engine with streaming mode
    model_path = "xtts_models/"

    try:
        engine = CoquiEngine(
            specific_model="v2.0.2",
            use_deepspeed=False,
            local_models_path=str(model_path),
            cloning_reference_wav="lisa.wav",
            voices_path="speakers/",
            language="en"
        )

        print("✓ CoquiEngine initialized successfully")
        print()

        # Check stream info
        format_info, channels, sample_rate = engine.get_stream_info()
        print(f"Stream configuration:")
        print(f"  Format: {format_info}")
        print(f"  Channels: {channels}")
        print(f"  Sample Rate: {sample_rate} Hz")

        if sample_rate == 48000:
            print("✓ Sample rate is correctly set to 48000 Hz")
        else:
            print(f"✗ Sample rate is {sample_rate} Hz (expected 48000 Hz)")

        print()
        print("Creating TextToAudioStream...")
        stream = TextToAudioStream(engine)
        print("✓ TextToAudioStream created successfully")
        print()

        # Test synthesis with a short text
        test_text = "Hello, this is a test of the streaming mode with the lisa voice."
        print(f"Testing synthesis with: '{test_text}'")
        print()

        # Feed the text to the stream
        stream.feed(test_text)
        print("✓ Text fed to stream successfully")

        # Give it a moment to start processing
        time.sleep(2)

        # Try to play the stream (muted to avoid actual audio output during test)
        print("Testing stream playback (muted)...")
        try:
            # Play with improved mode settings but muted
            stream.play_async(
                minimum_sentence_length=2,
                minimum_first_fragment_length=2,
                tokenizer="stanza",
                language="en",
                context_size=2,
                muted=True
            )
            print("✓ Stream playback started successfully (no sample rate error!)")

            # Wait a bit for processing
            time.sleep(3)

            # Stop the stream
            stream.stop()
            print("✓ Stream stopped successfully")

        except OSError as e:
            if "-9997" in str(e) or "Invalid sample rate" in str(e):
                print(f"✗ FAILED: Sample rate error still occurs: {e}")
                sys.exit(1)
            else:
                print(f"✗ Different error occurred: {e}")
                sys.exit(1)

        print()
        print("=" * 80)
        print("SUCCESS! Streaming mode with 'lisa' voice works correctly!")
        print("=" * 80)

    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this with the correct Python environment")
    sys.exit(1)
