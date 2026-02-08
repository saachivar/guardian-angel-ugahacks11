# 🎯 Computer Vision Integration - Quick Start

## What This Does

The `computer-vision/monitor_clips.py` script automatically watches the `receiver-backend/clips/` directory and keeps the latest uploaded fall detection video available at:

```
computer-vision/latest_clips/latest_fall_detection.mp4
```

This file is **always updated** with the newest video, so your computer vision code can process it immediately.

## Quick Start (3 Steps)

### 1. Start the Monitor (Terminal 1)

```bash
cd /Users/anishakumar/ugahacks2026/computer-vision
python3 monitor_clips.py
```

Keep this running in the background. It will automatically detect and copy new videos.

### 2. Access Latest Video in Your Code

```python
# Option A: Direct path (always the latest)
video_path = "/Users/anishakumar/ugahacks2026/computer-vision/latest_clips/latest_fall_detection.mp4"

# Option B: Use the helper function
from monitor_clips import get_latest_clip_path
video_path = get_latest_clip_path()

# Now process your video
import cv2
cap = cv2.VideoCapture(str(video_path))
# ... your processing code ...
```

### 3. Test It Works

```bash
# Check current status
cd /Users/anishakumar/ugahacks2026/computer-vision
python3 monitor_clips.py --check

# Example output:
# ✅ Latest video: webcam-01_2026-02-08T03-55-43.mp4
# ✅ Computer Vision has latest video
```

## Current Status

✅ **Monitor script created:** `computer-vision/monitor_clips.py`  
✅ **Storage directory created:** `computer-vision/latest_clips/`  
✅ **Latest video available:** `latest_clips/latest_fall_detection.mp4` (4.64 MB)  
✅ **Example script created:** `computer-vision/example_use_latest_video.py`  
✅ **Full documentation:** `computer-vision/CLIPS_INTEGRATION.md`

## File Flow

```
Raspberry Pi → Receiver Backend → Computer Vision
                    ↓
            receiver-backend/clips/
            device_01_timestamp.mp4
                    ↓
              (monitor copies)
                    ↓
          computer-vision/latest_clips/
          latest_fall_detection.mp4 ← ALWAYS THE NEWEST
```

## Integration Points

### With Your Existing Code

Your pose detection and fall classification code can now use:

```python
from monitor_clips import get_latest_clip_path

# In your main processing loop
video = get_latest_clip_path()
if video:
    results = your_pose_detector.process(video)
    fall_detected = your_classifier.classify(results)
```

### Automatic Processing

To process videos automatically when they arrive, modify `monitor_clips.py` line 111:

```python
if copy_latest_video(latest):
    processed_files.add(str(latest))
    
    # Add your processing here
    from your_module import process_fall_video
    process_fall_video(LATEST_VIDEO_PATH)
```

## Next Steps

1. ✅ Keep the monitor running: `python3 computer-vision/monitor_clips.py`
2. ✅ Upload a new video to test: Use receiver backend's test script
3. ✅ Integrate with your pose detection code
4. ✅ Add automatic processing on new uploads

---

**Need more details?** See `CLIPS_INTEGRATION.md` for full documentation.
