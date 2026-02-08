#!/usr/bin/env python3
"""
Clips Directory Monitor for Guardian Angel Computer Vision
Monitors the receiver-backend/clips directory for new video uploads
and automatically processes the latest fall detection video.
"""

import os
import time
import shutil
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).parent.parent  # ugahacks2026 directory
CLIPS_DIR = BASE_DIR / "receiver-backend" / "clips"
CV_STORAGE_DIR = Path(__file__).parent / "latest_clips"
LATEST_VIDEO_PATH = CV_STORAGE_DIR / "latest_fall_detection.mp4"

# Create storage directory if it doesn't exist
CV_STORAGE_DIR.mkdir(exist_ok=True)

# Track processed files
processed_files = set()


def get_latest_video():
    """Get the most recently added video file from clips directory"""
    if not CLIPS_DIR.exists():
        logger.warning(f"Clips directory does not exist: {CLIPS_DIR}")
        return None
    
    # Get all .mp4 files
    video_files = list(CLIPS_DIR.glob("*.mp4"))
    
    if not video_files:
        return None
    
    # Sort by modification time, get the newest
    latest_file = max(video_files, key=lambda f: f.stat().st_mtime)
    return latest_file


def delete_old_clips(keep_latest=True):
    """
    Delete old video clips from receiver-backend/clips directory
    
    Args:
        keep_latest: If True, keeps only the most recent video
    """
    if not CLIPS_DIR.exists():
        return
    
    video_files = list(CLIPS_DIR.glob("*.mp4"))
    
    if not video_files:
        return
    
    if keep_latest and len(video_files) > 1:
        # Sort by modification time
        video_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        # Keep the newest, delete the rest
        for old_file in video_files[1:]:
            try:
                old_file.unlink()
                logger.info(f"🗑️  Deleted old clip: {old_file.name}")
            except Exception as e:
                logger.error(f"❌ Failed to delete {old_file.name}: {e}")


def copy_latest_video(source_path):
    """Copy the latest video to the computer-vision storage directory"""
    try:
        # Copy to latest_fall_detection.mp4 (always overwrites)
        shutil.copy2(source_path, LATEST_VIDEO_PATH)
        
        # Also keep a timestamped copy for history
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archived_path = CV_STORAGE_DIR / f"fall_detection_{timestamp}.mp4"
        shutil.copy2(source_path, archived_path)
        
        logger.info(f"✅ Copied latest video: {source_path.name}")
        logger.info(f"   → {LATEST_VIDEO_PATH}")
        logger.info(f"   → {archived_path.name} (archived)")
        
        # Delete old clips from receiver-backend/clips to save space
        delete_old_clips(keep_latest=True)
        
        return True
    except Exception as e:
        logger.error(f"❌ Failed to copy video: {e}")
        return False


def monitor_clips_directory(poll_interval=2):
    """
    Continuously monitor the clips directory for new videos
    
    Args:
        poll_interval: How often to check for new files (in seconds)
    """
    logger.info("🎥 Starting Clips Directory Monitor")
    logger.info(f"   Watching: {CLIPS_DIR}")
    logger.info(f"   Storing to: {CV_STORAGE_DIR}")
    logger.info(f"   Poll interval: {poll_interval} seconds")
    logger.info("=" * 60)
    
    # Initial scan
    latest = get_latest_video()
    if latest:
        copy_latest_video(latest)
        processed_files.add(str(latest))
    
    # Monitor loop
    try:
        while True:
            time.sleep(poll_interval)
            
            latest = get_latest_video()
            
            if latest and str(latest) not in processed_files:
                logger.info(f"🆕 New video detected: {latest.name}")
                
                # Wait a moment to ensure file is fully written
                time.sleep(0.5)
                
                if copy_latest_video(latest):
                    processed_files.add(str(latest))
                    
                    # Optional: Trigger fall detection processing here
                    # process_fall_detection(LATEST_VIDEO_PATH)
                    
    except KeyboardInterrupt:
        logger.info("\n⏹️  Monitor stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitor error: {e}")


def get_latest_clip_path():
    """
    Utility function for other scripts to get the path to the latest video
    
    Returns:
        Path to the latest fall detection video, or None if not available
    """
    if LATEST_VIDEO_PATH.exists():
        return LATEST_VIDEO_PATH
    return None


def get_clip_metadata():
    """
    Get metadata about the latest clip
    
    Returns:
        dict with metadata or None
    """
    if not LATEST_VIDEO_PATH.exists():
        return None
    
    stats = LATEST_VIDEO_PATH.stat()
    
    return {
        "path": str(LATEST_VIDEO_PATH),
        "filename": LATEST_VIDEO_PATH.name,
        "size_bytes": stats.st_size,
        "size_mb": round(stats.st_size / (1024 * 1024), 2),
        "modified": datetime.fromtimestamp(stats.st_mtime).isoformat(),
        "exists": True
    }


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Monitor clips directory for new videos")
    parser.add_argument(
        "--interval",
        type=int,
        default=2,
        help="Poll interval in seconds (default: 2)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Just check for latest video and exit (don't monitor)"
    )
    
    args = parser.parse_args()
    
    if args.check:
        # Just check and report
        latest = get_latest_video()
        if latest:
            print(f"✅ Latest video: {latest}")
            print(f"   Size: {latest.stat().st_size / (1024*1024):.2f} MB")
            print(f"   Modified: {datetime.fromtimestamp(latest.stat().st_mtime)}")
        else:
            print("❌ No videos found in clips directory")
        
        # Check CV storage
        if LATEST_VIDEO_PATH.exists():
            print(f"\n✅ Computer Vision has latest video:")
            print(f"   Path: {LATEST_VIDEO_PATH}")
            metadata = get_clip_metadata()
            print(f"   Size: {metadata['size_mb']} MB")
            print(f"   Modified: {metadata['modified']}")
        else:
            print(f"\n❌ No video in CV storage yet")
    else:
        # Start monitoring
        monitor_clips_directory(poll_interval=args.interval)
