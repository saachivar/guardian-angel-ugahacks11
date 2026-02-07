"""Inspect per-frame pose features and detection inputs for debugging.
Usage: python inspect_features.py /path/to/video.mp4 [start_frame] [end_frame]
If no frame range provided, prints summary for entire video and highlights first frames with predictions.
"""
import sys
from pathlib import Path
repo_root = str(Path(__file__).resolve().parents[2])
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import cv2
import numpy as np
from deployment.huggingface_space import app as appmod


def inspect(video_path, start=None, end=None):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print('Cannot open video:', video_path); return
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    with appmod.PoseWrapper(static_image_mode=False, model_complexity=appmod.pose_complexity, smooth_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        frame_idx = 0
        local_feature_sequence = []
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            frame_idx += 1
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            t_ms = int((frame_idx / fps) * 1000)
            res = pose.process(rgb, timestamp_ms=t_ms)
            landmarks_present = bool(res.pose_landmarks and getattr(res.pose_landmarks, 'landmark', None))
            lm_count = len(res.pose_landmarks.landmark) if landmarks_present else 0
            features = appmod.extract_and_normalize_features(res)
            # compute some diagnostics
            feat_sum = float(np.nansum(features))
            feat_mean = float(np.nanmean(features)) if features.size>0 else float('nan')
            feat_nonzero = int(np.count_nonzero(features))
            # try to infer whether normalization applied: check shoulders and hips indices
            def kp_idx(name):
                try:
                    x,y,c = appmod.get_kpt_indices_training_order(name)
                    return x,y,c
                except Exception:
                    return None
            shoulder_idxs = kp_idx('Left Shoulder'), kp_idx('Right Shoulder')
            hip_idxs = kp_idx('Left Hip'), kp_idx('Right Hip')
            shoulders_vals = []
            hips_vals = []
            for idxs in (shoulder_idxs+hip_idxs):
                if idxs and idxs[0] is not None:
                    x_i,y_i,c_i = idxs
                    shoulders_vals.append((features[x_i], features[y_i], features[c_i])) if idxs in shoulder_idxs else hips_vals.append((features[x_i], features[y_i], features[c_i]))
            # decide to print
            if (start and end and start <= frame_idx <= end) or (not start and not end and frame_idx<=60) or (start is None and end is None and frame_idx%30==0):
                print(f"Frame {frame_idx}: lm_count={lm_count} feat_nonzero={feat_nonzero} sum={feat_sum:.6f} mean={feat_mean:.6f}")
                print("  shoulders:", shoulders_vals, "hips:", hips_vals)
            local_feature_sequence.append(features)
    cap.release()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python inspect_features.py /path/to/video.mp4 [start_frame] [end_frame]'); sys.exit(1)
    path = sys.argv[1]
    s = int(sys.argv[2]) if len(sys.argv)>=3 else None
    e = int(sys.argv[3]) if len(sys.argv)>=4 else None
    inspect(path, s, e)
