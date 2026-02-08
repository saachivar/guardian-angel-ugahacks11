# 🎥 Computer Vision Clips Integration

This system automatically monitors the `receiver-backend/clips/` directory and makes the latest uploaded fall detection video available to the computer vision processing pipeline.

## Overview

When a Raspberry Pi uploads a fall detection video to the receiver backend:
1. Video is saved to `receiver-backend/clips/`
2. The clips monitor detects the new file
3. Video is copied to `computer-vision/latest_clips/latest_fall_detection.mp4`
4. Computer vision system can immediately access and process it

## Directory Structure

```
ugahacks2026/
├── receiver-backend/
│   └── clips/                    # Videos uploaded from Raspberry Pi
│       ├── device_01_2026-02-08T12-30-45.mp4
│       ├── device_01_2026-02-08T12-35-12.mp4
│       └── ...
│
└── computer-vision/
    ├── monitor_clips.py          # Main monitoring script
    ├── example_use_latest_video.py  # Example usage
    └── latest_clips/             # CV storage (auto-created)
        ├── latest_fall_detection.mp4  # ALWAYS the newest video
        └── fall_detection_TIMESTAMP.mp4  # Archived copies
```

## Usage

### 1. Start the Clips Monitor (Background Service)

This runs continuously and automatically updates when new videos arrive:

```bash
cd /Users/anishakumar/ugahacks2026/computer-vision
python3 monitor_clips.py
```

**Output:**
```
🎥 Starting Clips Directory Monitor
   Watching: /Users/anishakumar/ugahacks2026/receiver-backend/clips
   Storing to: /Users/anishakumar/ugahacks2026/computer-vision/latest_clips
   Poll interval: 2 seconds
============================================================
✅ Copied latest video: device_01_2026-02-08T12-30-45.mp4
   → latest_fall_detection.mp4
   → fall_detection_20260208_123045.mp4 (archived)
🆕 New video detected: device_01_2026-02-08T12-35-12.mp4
✅ Copied latest video: device_01_2026-02-08T12-35-12.mp4
   → latest_fall_detection.mp4
   → fall_detection_20260208_123512.mp4 (archived)
```

**Options:**
```bash
# Custom poll interval (check every 5 seconds)
python3 monitor_clips.py --interval 5

# Just check current status (don't monitor)
python3 monitor_clips.py --check
```

### 2. Use Latest Video in Your Code

#### Python API:

```python
from computer-vision.monitor_clips import get_latest_clip_path, get_clip_metadata

# Get path to latest video
video_path = get_latest_clip_path()
if video_path:
    print(f"Processing: {video_path}")
    # Your processing code here
    
# Get metadata
metadata = get_clip_metadata()
print(f"Video size: {metadata['size_mb']} MB")
print(f"Last updated: {metadata['modified']}")
```

#### Direct Access:

The latest video is always at:
```
/Users/anishakumar/ugahacks2026/computer-vision/latest_clips/latest_fall_detection.mp4
```

You can directly read this file in any script - it's automatically updated when new videos arrive.

### 3. Example Processing Script

```bash
cd /Users/anishakumar/ugahacks2026/computer-vision
python3 example_use_latest_video.py
```

This demonstrates how to:
- Access the latest video
- Get metadata (size, timestamp)
- Load it with OpenCV
- Process it with your fall detection model

## Integration with Existing Computer Vision Code

### With Pose Detection:

```python
from core.pose_detector import PoseDetector
from core.fall_classifier import FallClassifier
from monitor_clips import get_latest_clip_path

# Get latest video
video_path = get_latest_clip_path()

# Initialize your models
detector = PoseDetector()
classifier = FallClassifier()

# Process the video
results = detector.process_video(video_path)
fall_detected = classifier.classify(results)

print(f"Fall detected: {fall_detected}")
```

### Automatic Processing on New Upload:

You can modify `monitor_clips.py` to automatically trigger processing:

```python
# In monitor_clips.py, after line 111:
if copy_latest_video(latest):
    processed_files.add(str(latest))
    
    # Add this:
    from your_fall_detector import process_video
    process_video(LATEST_VIDEO_PATH)
```

## File Naming Convention

Videos from the receiver backend follow this pattern:
```
{device_id}_{timestamp}.mp4

Examples:
- raspberry_pi_01_2026-02-08T12-30-45.mp4
- test_device_2026-02-08T14-15-30.mp4
```

Archived copies in `latest_clips/` use:
```
fall_detection_{timestamp}.mp4

Example:
- fall_detection_20260208_123045.mp4
```

## Testing

### 1. Test with a sample video:

```bash
# Create a test video in clips directory
cd /Users/anishakumar/ugahacks2026/receiver-backend/clips
touch test_fall_$(date +%Y-%m-%d_%H-%M-%S).mp4
```

The monitor should detect it immediately and copy it.

### 2. Check current status:

```bash
cd /Users/anishakumar/ugahacks2026/computer-vision
python3 monitor_clips.py --check
```

### 3. Test the full flow:

```bash
# Terminal 1: Start monitor
python3 computer-vision/monitor_clips.py

# Terminal 2: Upload a video via receiver backend
cd receiver-backend
python3 test_upload.py

# Terminal 3: Process the latest video
python3 computer-vision/example_use_latest_video.py
```

## Running as a Background Service

### Option 1: Using screen (keeps running after logout)

```bash
screen -S clips-monitor
cd /Users/anishakumar/ugahacks2026/computer-vision
python3 monitor_clips.py

# Detach: Ctrl+A then D
# Reattach later: screen -r clips-monitor
```

### Option 2: Using nohup

```bash
cd /Users/anishakumar/ugahacks2026/computer-vision
nohup python3 monitor_clips.py > monitor.log 2>&1 &

# Check it's running
ps aux | grep monitor_clips

# View logs
tail -f monitor.log
```

### Option 3: Add to startup (macOS)

Create a launchd plist to start automatically on boot (advanced).

## Cleanup Old Videos

To prevent disk space issues, periodically clean old archived videos:

```bash
# Delete archived videos older than 7 days
cd /Users/anishakumar/ugahacks2026/computer-vision/latest_clips
find . -name "fall_detection_*.mp4" -mtime +7 -delete

# Keep only the 10 most recent archived videos
ls -t fall_detection_*.mp4 | tail -n +11 | xargs rm -f
```

## Troubleshooting

### Monitor not detecting new files

**Check permissions:**
```bash
ls -la /Users/anishakumar/ugahacks2026/receiver-backend/clips
```

**Check directory exists:**
```bash
ls /Users/anishakumar/ugahacks2026/receiver-backend/clips
```

### Video file is corrupted

The monitor waits 0.5 seconds after detecting a new file to ensure it's fully written. If you're still getting corrupted files, increase this delay in `monitor_clips.py` line 96:
```python
time.sleep(1.0)  # Wait 1 second instead of 0.5
```

### Latest video not updating

Check if monitor is running:
```bash
ps aux | grep monitor_clips
```

Manually check for new files:
```bash
python3 computer-vision/monitor_clips.py --check
```

## Performance Notes

- **Poll interval:** Default 2 seconds. Lower values = faster detection but more CPU usage
- **Disk space:** Each video is stored twice (receiver + CV storage). Consider cleanup strategy
- **Processing time:** The monitor doesn't block - it copies files asynchronously
- **Multiple monitors:** Only run one monitor instance at a time to avoid conflicts

## Next Steps

1. ✅ Start the clips monitor in the background
2. ✅ Test with a video upload from Raspberry Pi
3. ✅ Integrate with your existing pose detection code
4. ✅ Set up automatic processing on new videos
5. ✅ Configure cleanup for old archived videos

---

**Questions?** Check the logs in the monitor terminal or `monitor.log` file.
