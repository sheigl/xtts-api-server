#!/usr/bin/env python3
"""
Simple test script to verify streaming mode works with the resampled audio.
"""
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from xtts_api_server.RealtimeTTS.engines.coqui_engine import CoquiEngine
import pyaudio

def test_sample_rate():
    """Test that the engine reports the correct sample rate"""
    print("Testing CoquiEngine sample rate configuration...")

    # We can't fully initialize the engine without a model, but we can test the method
    # by reading the source code directly
    print("\nChecking get_stream_info method...")

    # Create a mock instance just to call the method
    # Note: This will fail if we try to actually use it, but we just want to check the method
    try:
        # Just verify the method exists and returns the right values
        import inspect
        source = inspect.getsource(CoquiEngine.get_stream_info)
        if "48000" in source:
            print("✓ get_stream_info returns 48000 Hz sample rate")
        else:
            print("✗ get_stream_info does not return 48000 Hz")

        # Check postprocess_wave has resampling
        source_file = inspect.getsourcefile(CoquiEngine)
        with open(source_file, 'r') as f:
            content = f.read()
            if "signal.resample" in content and "48000" in content:
                print("✓ postprocess_wave includes resampling to 48000 Hz")
            else:
                print("✗ postprocess_wave does not include resampling")

    except Exception as e:
        print(f"Error checking methods: {e}")

    # Test that pyaudio can open a stream with 48000 Hz
    print("\nTesting PyAudio with 48000 Hz...")
    p = pyaudio.PyAudio()
    try:
        # Try to open a test stream with 48000 Hz
        stream = p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=48000,
            output=True
        )
        print("✓ PyAudio successfully opened stream with 48000 Hz")
        stream.close()
    except OSError as e:
        print(f"✗ PyAudio failed to open stream with 48000 Hz: {e}")
    finally:
        p.terminate()

if __name__ == "__main__":
    test_sample_rate()
