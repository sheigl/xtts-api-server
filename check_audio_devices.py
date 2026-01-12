#!/usr/bin/env python3
"""
Script to check available audio devices and their supported sample rates.
"""
import pyaudio

def check_audio_devices():
    p = pyaudio.PyAudio()

    print("Available Audio Devices:")
    print("=" * 80)

    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        print(f"\nDevice {i}: {info['name']}")
        print(f"  Max Input Channels: {info['maxInputChannels']}")
        print(f"  Max Output Channels: {info['maxOutputChannels']}")
        print(f"  Default Sample Rate: {info['defaultSampleRate']}")

        # Test common sample rates
        if info['maxOutputChannels'] > 0:  # Only test output devices
            print(f"  Supported sample rates for output:")
            test_rates = [8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000]
            supported = []
            for rate in test_rates:
                try:
                    if p.is_format_supported(
                        rate,
                        output_device=i,
                        output_channels=1,
                        output_format=pyaudio.paFloat32
                    ):
                        supported.append(rate)
                except ValueError:
                    pass

            if supported:
                print(f"    {', '.join(map(str, supported))} Hz")
            else:
                print(f"    Unable to determine (device may not support querying)")

    print("\n" + "=" * 80)
    default_output = p.get_default_output_device_info()
    print(f"\nDefault Output Device: {default_output['name']}")
    print(f"Default Sample Rate: {default_output['defaultSampleRate']}")

    p.terminate()

if __name__ == "__main__":
    check_audio_devices()
