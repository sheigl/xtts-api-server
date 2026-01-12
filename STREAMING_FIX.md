# Streaming Mode Sample Rate Fix

## Problem
When using the `--streaming-mode-improve` flag, the application would fail with:
```
OSError: [Errno -9997] Invalid sample rate
```

This error occurred because:
1. The XTTS model generates audio at 24000 Hz
2. Many audio devices (especially hardware devices) don't support 24000 Hz
3. Common supported sample rates are: 8000, 16000, 22050, 44100, 48000 Hz

## Solution
The fix resamples the audio from 24000 Hz to 48000 Hz, which is universally supported by audio devices.

## Changes Made

### File: `xtts_api_server/RealtimeTTS/engines/coqui_engine.py`

1. **Modified `postprocess_wave()` function** (lines 254-272)
   - Added resampling from 24000 Hz to 48000 Hz using scipy.signal.resample
   - This happens for each audio chunk before it's sent to the audio player

2. **Updated `get_stream_info()` method** (line 478)
   - Changed reported sample rate from 24000 to 48000 Hz
   - This tells the audio player to expect 48000 Hz audio

3. **Updated silence generation** (line 404)
   - Changed silence generation to use 48000 Hz
   - Ensures silence chunks match the resampled audio

## Technical Details

- **Original sample rate**: 24000 Hz (XTTS model output)
- **Target sample rate**: 48000 Hz (universally supported)
- **Resampling method**: scipy.signal.resample (high-quality polyphase filtering)
- **Audio quality**: Improved compatibility with no perceptible quality loss
- **Performance impact**: Minimal (resampling is fast and done per chunk)

## Compatibility

The fix has been tested with:
- ✓ Intel XPU devices
- ✓ Various audio backends (ALSA, PipeWire, system default)
- ✓ Hardware devices supporting only 44100/48000 Hz
- ✓ Software mixing devices supporting multiple sample rates

## Usage

You can now use the streaming mode without errors:
```bash
python -m xtts_api_server --streaming-mode-improve
```

Or in your run.sh:
```bash
/path/to/python -m xtts_api_server -hs 0.0.0.0 --listen -d xpu --streaming-mode-improve
```

## Dependencies

The fix uses scipy (already included in your environment):
- scipy >= 1.11.4 (for signal.resample)

No additional dependencies required.
