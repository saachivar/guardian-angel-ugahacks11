"""Diagnostic helper: analyze a video with current pose+classifier pipeline and export per-frame fall probabilities and top frames.
Usage: python debug_inspect.py [video_path]
If no path is given, the script will pick the most recent video file in repo root (.mp4/.mov).
"""
import os
import sys
import csv
import cv2
import numpy as np
from collections import deque

# Ensure repo root is on sys.path so we can import the app module when running this script directly
from pathlib import Path
repo_root = str(Path(__file__).resolve().parents[2])  # project root (parent of 'deployment')
import sys
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

# Import app module components
from deployment.huggingface_space import app as appmod

OUT_DIR = 'debug_frames'
os.makedirs(OUT_DIR, exist_ok=True)

EXTS = ('.mp4', '.mov', '.avi', '.mkv')

def find_latest_video(path='.'):
    files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(EXTS)]
    if not files:
        return None
    files_sorted = sorted(files, key=lambda p: os.path.getmtime(p), reverse=True)
    return files_sorted[0]


def analyze(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError('Cannot open video: ' + video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0

    local_feature_sequence = deque(maxlen=appmod.INPUT_TIMESTEPS)
    results_list = []

    frame_idx = 0

    with appmod.PoseWrapper(static_image_mode=False, model_complexity=appmod.pose_complexity, smooth_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while True:
            ok, bgr = cap.read()
            if not ok:
                break
            frame_idx += 1
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            # use timestamp in ms
            t_ms = int((frame_idx / fps) * 1000)
            res = pose.process(rgb, timestamp_ms=t_ms)
            features = appmod.extract_and_normalize_features(res)
            local_feature_sequence.append(features)

            prediction_probability_fall = None
            if len(local_feature_sequence) == appmod.INPUT_TIMESTEPS:
                inp = np.array(local_feature_sequence, dtype=np.float32)
                inp = np.expand_dims(inp, axis=0)
                try:
                    appmod.interpreter.set_tensor(appmod.input_details[0]['index'], inp)
                    appmod.interpreter.invoke()
                    out = appmod.interpreter.get_tensor(appmod.output_details[0]['index'])
                    prediction_probability_fall = float(out[0][0])
                except Exception as e:
                    prediction_probability_fall = None

            results_list.append({'frame': frame_idx, 'time_s': frame_idx / fps, 'prob_fall': prediction_probability_fall})

    cap.release()

    # Write CSV
    csv_path = os.path.join(OUT_DIR, 'per_frame_probs.csv')
    with open(csv_path, 'w', newline='') as fp:
        writer = csv.DictWriter(fp, fieldnames=['frame', 'time_s', 'prob_fall'])
        writer.writeheader()
        for r in results_list:
            writer.writerow(r)

    # Find top frames by probability
    scored = [r for r in results_list if r['prob_fall'] is not None]
    if not scored:
        print('No frames had model predictions (sequence length may be too short)')
        return csv_path, []
    scored_sorted = sorted(scored, key=lambda x: x['prob_fall'], reverse=True)
    topk = scored_sorted[:10]

    # Re-open video and save annotated top frames
    cap = cv2.VideoCapture(video_path)
    saved = []
    top_frames_idx = set([t['frame'] for t in topk])
    frame_idx = 0
    while True:
        ok, bgr = cap.read()
        if not ok:
            break
        frame_idx += 1
        if frame_idx in top_frames_idx:
            # draw simple overlay text
            r = next(filter(lambda x: x['frame']==frame_idx, topk))
            txt = f"Frame {frame_idx} ({r['time_s']:.2f}s) P(fall)={r['prob_fall']:.3f}"
            cv2.putText(bgr, txt, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
            out_path = os.path.join(OUT_DIR, f"top_frame_{frame_idx}.jpg")
            cv2.imwrite(out_path, bgr)
            saved.append(out_path)
    cap.release()

    return csv_path, saved


if __name__ == '__main__':
    vid = sys.argv[1] if len(sys.argv) > 1 else None
    if not vid:
        vid = find_latest_video('.')
    if not vid:
        print('No video found in repo root. Provide a path: python debug_inspect.py /path/to/video.mp4')
        sys.exit(1)
    print('Analyzing:', vid)
    csv_path, imgs = analyze(vid)
    print('Wrote CSV:', csv_path)
    if imgs:
        print('Saved top frames:', imgs)
    else:
        print('No top frames saved')
