import cv2
import mediapipe as mp
import numpy as np
# Prefer tflite-runtime, fall back to TensorFlow's TFLite interpreter on platforms without tflite-runtime
try:
    import tflite_runtime.interpreter as tflite
    print("Using tflite-runtime interpreter")
except Exception:
    try:
        import tensorflow as tf
        class _TFWrapper:
            Interpreter = tf.lite.Interpreter
        tflite = _TFWrapper
        print("tflite-runtime not available — using TensorFlow's TFLite Interpreter as fallback")
    except Exception as e:
        print(f"Error: Neither tflite_runtime nor tensorflow is available: {e}")
        raise

import time
from collections import deque
import gradio as gr
import os
import shutil # สำหรับ copy ไฟล์ example

# --- Configuration (ปรับให้เหมาะกับ Gradio) ---
# Ensure model path resolves relative to this script's directory
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'fall_detection_transformer.tflite')
INPUT_TIMESTEPS = 30
FALL_CONFIDENCE_THRESHOLD = 0.90
MIN_KEYPOINT_CONFIDENCE_FOR_NORMALIZATION = 0.3
# --- MediaPipe Tasks API (mp.solutions is deprecated) ---
pose_complexity = 0 # ลด complexity เพื่อความเร็วบน Spaces, ลอง 0 หรือ 1
use_static_image_mode = False # สำหรับวิดีโอไฟล์ จะถูก override เป็น True ใน process_video

# Define POSE_CONNECTIONS (same connectivity as MediaPipe Pose) for drawing
POSE_CONNECTIONS = [
    (0,1),(0,2),(1,3),(2,4),(5,6),(5,7),(7,9),(6,8),(8,10),(11,12),(11,13),(13,15),(12,14),(14,16),(15,17),(16,18),(15,19),(19,21),(16,20),(20,22),(11,23),(12,24),(23,24),(23,25),(24,26),(25,27),(26,28),(27,29),(28,30),(29,31),(30,32)
]

# Small helper to build a MediaPipe-like landmark object
class _Landmark:
    def __init__(self, x, y, z=0.0, visibility=1.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.visibility = float(visibility)

class _PoseResults:
    def __init__(self, landmarks):
        # landmarks: list of _Landmark
        class LMHolder:
            def __init__(self, landmark_list):
                self.landmark = landmark_list
        self.pose_landmarks = LMHolder(landmarks)


# Use MediaPipe Tasks API (mp.solutions is deprecated)
POSE_BACKEND = 'mp_tasks'
try:
    from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
    from mediapipe.tasks.python.core.base_options import BaseOptions
    # Prefer explicit environment override, otherwise search common repo locations for a `.task` file
    MP_POSE_MODEL_PATH = os.environ.get('MP_POSE_MODEL_PATH', None)
    MODEL_PATH_FOR_TASK = None
    if MP_POSE_MODEL_PATH and os.path.exists(MP_POSE_MODEL_PATH):
        MODEL_PATH_FOR_TASK = MP_POSE_MODEL_PATH
        print('Using MediaPipe Tasks PoseLandmarker model from MP_POSE_MODEL_PATH:', MP_POSE_MODEL_PATH)
    else:
        # Search for .task files in likely locations (repo root, deployment folders)
        search_dirs = [
            os.path.join(os.path.dirname(__file__), '..'),
            os.path.join(os.path.dirname(__file__), '..', 'raspberry_pi'),
            os.path.join(os.path.dirname(__file__), '..', 'huggingface_space'),
            os.getcwd()
        ]
        candidate = None
        for sd in search_dirs:
            try:
                sd_abs = os.path.abspath(sd)
                for fname in os.listdir(sd_abs):
                    if fname.endswith('.task') and 'pose' in fname.lower():
                        candidate = os.path.join(sd_abs, fname)
                        break
                if candidate:
                    break
            except Exception:
                continue
        if candidate and os.path.exists(candidate):
            MODEL_PATH_FOR_TASK = candidate
            print('Auto-detected MediaPipe Task model at:', MODEL_PATH_FOR_TASK)

    if not MODEL_PATH_FOR_TASK:
        raise RuntimeError('No MediaPipe .task model found. Place a pose_landmarker*.task file in deployment/raspberry_pi/ or set MP_POSE_MODEL_PATH environment variable.')
    
    print('Using MediaPipe Tasks PoseLandmarker with model:', MODEL_PATH_FOR_TASK)
except Exception as e:
    raise RuntimeError(f'Failed to initialize MediaPipe Tasks API: {e}')

# Draw landmarks manually when mp drawing utilities are not available
def _draw_landmarks_custom(image_bgr, landmarks):
    h, w = image_bgr.shape[:2]
    # draw connections
    for a, b in POSE_CONNECTIONS:
        if a < len(landmarks) and b < len(landmarks):
            pt1 = (int(landmarks[a].x * w), int(landmarks[a].y * h))
            pt2 = (int(landmarks[b].x * w), int(landmarks[b].y * h))
            cv2.line(image_bgr, pt1, pt2, (0,255,0), 2)
    # draw keypoints
    for lm in landmarks:
        cx = int(lm.x * w)
        cy = int(lm.y * h)
        cv2.circle(image_bgr, (cx, cy), 3, (0,0,255), -1)

# Wrapper to provide a context manager with a process(image_rgb) method
class PoseWrapper:
    def __init__(self, static_image_mode=False, model_complexity=0, smooth_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.static_image_mode = static_image_mode
        self.model_complexity = model_complexity
        self.smooth_landmarks = smooth_landmarks
        self.min_detection_confidence = min_detection_confidence
        self.min_tracking_confidence = min_tracking_confidence
        self._backend_inst = None
        self._mp_tasks_landmarker = None

    def __enter__(self):
        # Use MediaPipe Tasks API
        base_opts = BaseOptions(model_asset_path=MODEL_PATH_FOR_TASK)
        # Use VIDEO running mode for better tracking when processing video frames
        chosen_running_mode = RunningMode.VIDEO if not self.static_image_mode else RunningMode.IMAGE
        opts = PoseLandmarkerOptions(
            base_options=base_opts,
            running_mode=chosen_running_mode,
            min_pose_detection_confidence=self.min_detection_confidence,
            min_pose_presence_confidence=0.5,
            min_tracking_confidence=self.min_tracking_confidence
        )
        self._mp_tasks_landmarker = PoseLandmarker.create_from_options(opts)
        self._backend_inst = self._mp_tasks_landmarker
        self._running_mode = chosen_running_mode
        return self

    def process(self, image_rgb, timestamp_ms=None):
        # image_rgb: numpy RGB image
        # Construct a mediapipe Image correctly for the Tasks API
        from mediapipe import Image
        from mediapipe.tasks.python.vision.core import image as mp_image_core
        mp_image = Image(image_format=mp_image_core.ImageFormat.SRGB, data=image_rgb)
        
        # Use appropriate detection method based on running mode
        if hasattr(self, '_running_mode') and self._running_mode == RunningMode.VIDEO:
            # VIDEO mode requires timestamp
            if timestamp_ms is None:
                timestamp_ms = 0
            res = self._mp_tasks_landmarker.detect_for_video(mp_image, timestamp_ms)
        else:
            # IMAGE mode
            res = self._mp_tasks_landmarker.detect(mp_image)

        # res.pose_landmarks is a list of landmark lists; use first pose if present
        landmarks_list = []
        if hasattr(res, 'pose_landmarks') and res.pose_landmarks:
            # pose_landmarks[0] is already a list of landmarks (not an object with .landmark attribute)
            if len(res.pose_landmarks) > 0:
                for lm in res.pose_landmarks[0]:
                    landmarks_list.append(_Landmark(lm.x, lm.y, lm.z, getattr(lm, 'visibility', 1.0)))
        return _PoseResults(landmarks_list)

    def __exit__(self, exc_type, exc, tb):
        if self._mp_tasks_landmarker is not None:
            self._mp_tasks_landmarker.close()


FALL_EVENT_COOLDOWN = 10

# ----- 0. KEYPOINT DEFINITIONS (เหมือนเดิม) -----
KEYPOINT_NAMES_ORIGINAL = [
    'Nose', 'Left Eye Inner', 'Left Eye', 'Left Eye Outer', 'Right Eye Inner', 'Right Eye', 'Right Eye Outer',
    'Left Ear', 'Right Ear', 'Mouth Left', 'Mouth Right',
    'Left Shoulder', 'Right Shoulder', 'Left Elbow', 'Right Elbow', 'Left Wrist', 'Right Wrist',
    'Left Pinky', 'Right Pinky', 'Left Index', 'Right Index', 'Left Thumb', 'Right Thumb',
    'Left Hip', 'Right Hip', 'Left Knee', 'Right Knee', 'Left Ankle', 'Right Ankle',
    'Left Heel', 'Right Heel', 'Left Foot Index', 'Right Foot Index'
]
# Create a mapping from MediaPipe landmark index -> our training keypoint name
# MediaPipe Tasks API uses the same 33-point model as the deprecated mp.solutions
MEDIAPIPE_TO_YOUR_KEYPOINTS_MAPPING = {
    0: 'Nose', 2: 'Left Eye', 5: 'Right Eye', 7: 'Left Ear', 8: 'Right Ear',
    11: 'Left Shoulder', 12: 'Right Shoulder', 13: 'Left Elbow', 14: 'Right Elbow',
    15: 'Left Wrist', 16: 'Right Wrist', 23: 'Left Hip', 24: 'Right Hip',
    25: 'Left Knee', 26: 'Right Knee', 27: 'Left Ankle', 28: 'Right Ankle'
}
YOUR_KEYPOINT_NAMES_TRAINING = [
    'Nose', 'Left Eye', 'Right Eye', 'Left Ear', 'Right Ear',
    'Left Shoulder', 'Right Shoulder', 'Left Elbow', 'Right Elbow',
    'Left Wrist', 'Right Wrist', 'Left Hip', 'Right Hip',
    'Left Knee', 'Right Knee', 'Left Ankle', 'Right Ankle'
]
SORTED_YOUR_KEYPOINT_NAMES = sorted(YOUR_KEYPOINT_NAMES_TRAINING)
KEYPOINT_DICT_TRAINING = {name: i for i, name in enumerate(SORTED_YOUR_KEYPOINT_NAMES)}
NUM_KEYPOINTS_TRAINING = len(KEYPOINT_DICT_TRAINING)
NUM_FEATURES = NUM_KEYPOINTS_TRAINING * 3

print("--- Initializing Keypoint Definitions for Gradio App ---")
print(f"NUM_FEATURES for model input: {NUM_FEATURES}")
# ---------------------------------------------------------------

# --- Load TFLite Model ---
try:
    print(f"Attempting to load TFLite model from: {MODEL_PATH}")
    interpreter = tflite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print(f"TFLite Model Loaded: {MODEL_PATH}")
    model_expected_shape = tuple(input_details[0]['shape'])
    if model_expected_shape[2] != NUM_FEATURES or model_expected_shape[1] != INPUT_TIMESTEPS:
        raise RuntimeError(f"Model's expected input shape features/timesteps ({model_expected_shape[1]},{model_expected_shape[2]}) does not match configured ({INPUT_TIMESTEPS},{NUM_FEATURES}).")
except Exception as e:
    print(f"Error loading TFLite model at {MODEL_PATH}: {e}")
    raise

# --- Helper Functions (get_kpt_indices, normalize_skeleton_frame, extract_and_normalize_features - เหมือนเดิม) ---
def get_kpt_indices_training_order(keypoint_name):
    if keypoint_name not in KEYPOINT_DICT_TRAINING:
        raise ValueError(f"Keypoint '{keypoint_name}' not found in KEYPOINT_DICT_TRAINING. Available: {list(KEYPOINT_DICT_TRAINING.keys())}")
    kp_idx = KEYPOINT_DICT_TRAINING[keypoint_name]
    return kp_idx * 3, kp_idx * 3 + 1, kp_idx * 3 + 2

def normalize_skeleton_frame(frame_features_sorted, min_confidence=MIN_KEYPOINT_CONFIDENCE_FOR_NORMALIZATION):
    normalized_frame = np.copy(frame_features_sorted)
    ref_kp_names = {'ls': 'Left Shoulder', 'rs': 'Right Shoulder', 'lh': 'Left Hip', 'rh': 'Right Hip'}
    try:
        ls_x_idx, ls_y_idx, ls_c_idx = get_kpt_indices_training_order(ref_kp_names['ls'])
        rs_x_idx, rs_y_idx, rs_c_idx = get_kpt_indices_training_order(ref_kp_names['rs'])
        lh_x_idx, lh_y_idx, lh_c_idx = get_kpt_indices_training_order(ref_kp_names['lh'])
        rh_x_idx, rh_y_idx, rh_c_idx = get_kpt_indices_training_order(ref_kp_names['rh'])
    except ValueError as e:
        print(f"Warning in normalize_skeleton_frame (get_kpt_indices): {e}")
        return frame_features_sorted

    ls_x, ls_y, ls_c = frame_features_sorted[ls_x_idx], frame_features_sorted[ls_y_idx], frame_features_sorted[ls_c_idx]
    rs_x, rs_y, rs_c = frame_features_sorted[rs_x_idx], frame_features_sorted[rs_y_idx], frame_features_sorted[rs_c_idx]
    lh_x, lh_y, lh_c = frame_features_sorted[lh_x_idx], frame_features_sorted[lh_y_idx], frame_features_sorted[lh_c_idx]
    rh_x, rh_y, rh_c = frame_features_sorted[rh_x_idx], frame_features_sorted[rh_y_idx], frame_features_sorted[rh_c_idx]

    mid_shoulder_x, mid_shoulder_y = np.nan, np.nan
    valid_ls, valid_rs = ls_c > min_confidence, rs_c > min_confidence
    if valid_ls and valid_rs: mid_shoulder_x, mid_shoulder_y = (ls_x + rs_x) / 2, (ls_y + rs_y) / 2
    elif valid_ls: mid_shoulder_x, mid_shoulder_y = ls_x, ls_y
    elif valid_rs: mid_shoulder_x, mid_shoulder_y = rs_x, rs_y

    mid_hip_x, mid_hip_y = np.nan, np.nan
    valid_lh, valid_rh = lh_c > min_confidence, rh_c > min_confidence
    if valid_lh and valid_rh: mid_hip_x, mid_hip_y = (lh_x + rh_x) / 2, (lh_y + rh_y) / 2
    elif valid_lh: mid_hip_x, mid_hip_y = lh_x, lh_y
    elif valid_rh: mid_hip_x, mid_hip_y = rh_x, rh_y

    if np.isnan(mid_hip_x) or np.isnan(mid_hip_y):
        return frame_features_sorted

    reference_height = np.nan
    if not np.isnan(mid_shoulder_y) and not np.isnan(mid_hip_y):
        reference_height = np.abs(mid_shoulder_y - mid_hip_y)

    perform_scaling = not (np.isnan(reference_height) or reference_height < 1e-5)

    for kp_name_sorted in SORTED_YOUR_KEYPOINT_NAMES:
        try:
            x_col, y_col, _ = get_kpt_indices_training_order(kp_name_sorted)
            normalized_frame[x_col] -= mid_hip_x
            normalized_frame[y_col] -= mid_hip_y
            if perform_scaling:
                normalized_frame[x_col] /= reference_height
                normalized_frame[y_col] /= reference_height
        except ValueError: # Should not happen if kp_name_sorted is from SORTED_YOUR_KEYPOINT_NAMES
            pass
    return normalized_frame

def extract_and_normalize_features(pose_results):
    frame_features_sorted = np.zeros(NUM_FEATURES, dtype=np.float32)
    if pose_results.pose_landmarks and getattr(pose_results.pose_landmarks, 'landmark', None):
        landmarks = pose_results.pose_landmarks.landmark
        if not landmarks:
            return frame_features_sorted
        for mp_landmark_key, your_kp_name in MEDIAPIPE_TO_YOUR_KEYPOINTS_MAPPING.items():
            if your_kp_name in KEYPOINT_DICT_TRAINING:
                try:
                    # First try direct index access (handles mp.solutions enums and ints)
                    if isinstance(mp_landmark_key, int):
                        lm = landmarks[mp_landmark_key]
                    else:
                        try:
                            lm = landmarks[mp_landmark_key.value]
                        except Exception:
                            # If direct enum->value access fails (different MediaPipe API), try name-based lookup
                            lm = None
                    # If direct access failed or list is shorter, try mapping by landmark name (robust for MediaPipe Tasks)
                    if lm is None:
                        try:
                            idx = KEYPOINT_NAMES_ORIGINAL.index(your_kp_name)
                            if idx < len(landmarks):
                                lm = landmarks[idx]
                        except ValueError:
                            lm = None
                    if lm is None:
                        raise IndexError(f'Could not find landmark for {your_kp_name}')
                    x_idx, y_idx, c_idx = get_kpt_indices_training_order(your_kp_name)
                    frame_features_sorted[x_idx], frame_features_sorted[y_idx], frame_features_sorted[c_idx] = lm.x, lm.y, getattr(lm, 'visibility', 1.0)
                except (IndexError, ValueError) as e:
                    print(f"Warning in extract_and_normalize_features for {your_kp_name}: {e}")
                    pass
    normalized_features = normalize_skeleton_frame(frame_features_sorted.copy())
    return normalized_features
# -------------------------------------------------------------------------------------------------------------------

# --- Function to process uploaded video for Gradio ---
def process_video_for_gradio(uploaded_video_path_temp):
    if uploaded_video_path_temp is None:
        return None, "Please upload a video file."

    print(f"Gradio provided temp video path: {uploaded_video_path_temp}")
    base_name = os.path.basename(uploaded_video_path_temp)
    # สร้าง path ที่ unique มากขึ้นสำหรับไฟล์ที่ copy มา
    timestamp_str = str(int(time.time() * 1000)) # เพิ่ม timestamp เพื่อความ unique
    local_video_path = os.path.join(os.getcwd(), f"{timestamp_str}_{base_name}") 

    try:
        print(f"Copying video from {uploaded_video_path_temp} to {local_video_path}")
        shutil.copy2(uploaded_video_path_temp, local_video_path)
        print(f"Video copied successfully to {local_video_path}")
    except Exception as e:
        error_msg = f"Error copying video file: {e}\nTemp path: {uploaded_video_path_temp}"
        print(error_msg); return None, error_msg

    local_feature_sequence = deque(maxlen=INPUT_TIMESTEPS)
    local_last_fall_event_time = 0 # ใช้ local_last_fall_event_time_sec เพื่อความชัดเจนว่าเป็นหน่วยวินาทีของวิดีโอ
    
    cap = cv2.VideoCapture(local_video_path)
    if not cap.isOpened():
        error_msg = f"Error: OpenCV cannot open video file at copied path: {local_video_path}"
        if os.path.exists(local_video_path): print(f"File size of '{local_video_path}': {os.path.getsize(local_video_path)} bytes")
        else: print(f"File '{local_video_path}' does not exist after copy attempt.")
        if os.path.exists(local_video_path): os.remove(local_video_path) # Cleanup
        return None, error_msg

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0 or np.isnan(fps) or fps < 1: fps = 25.0 # Default FPS, ensure it's float
    
    processed_frames_list = []
    overall_status_updates = []

    with PoseWrapper(
            static_image_mode=False,  # Use VIDEO mode for video processing
            model_complexity=pose_complexity,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5) as pose:
        
        frame_count = 0
        while cap.isOpened():
            success, original_bgr_frame = cap.read() # อ่าน frame มาเป็น BGR
            if not success:
                break
            
            frame_count += 1

            # *** START: การแก้ไขเรื่องสีและการวาด ***
            # สร้างสำเนาของ BGR frame สำหรับการวาดผลลัพธ์
            frame_for_display = original_bgr_frame.copy()

            # 1. แปลงเป็น RGB เฉพาะตอนส่งให้ MediaPipe
            image_rgb_for_mediapipe = cv2.cvtColor(original_bgr_frame, cv2.COLOR_BGR2RGB)
            image_rgb_for_mediapipe.flags.writeable = False
            current_video_time_sec = frame_count / fps
            # Pass timestamp_ms to pose.process (required for VIDEO mode)
            timestamp_ms = int(current_video_time_sec * 1000)
            results = pose.process(image_rgb_for_mediapipe, timestamp_ms=timestamp_ms)
            # image_rgb_for_mediapipe.flags.writeable = True # ไม่จำเป็นแล้ว

            # 2. Extract and Normalize Features
            current_features = extract_and_normalize_features(results)
            local_feature_sequence.append(current_features)
            
            # ... (ส่วนการทำนายผล prediction เหมือนเดิม) ...
            current_status_text_for_log = f"Frame {frame_count}: Collecting..." # สำหรับ log
            prediction_label = "no_fall"
            display_confidence_value = 0.0

            if len(local_feature_sequence) == INPUT_TIMESTEPS:
                model_input_data = np.array(local_feature_sequence, dtype=np.float32)
                model_input_data = np.expand_dims(model_input_data, axis=0)
                try:
                    interpreter.set_tensor(input_details[0]['index'], model_input_data)
                    interpreter.invoke()
                    output_data = interpreter.get_tensor(output_details[0]['index'])
                    prediction_probability_fall = output_data[0][0]

                    if prediction_probability_fall >= FALL_CONFIDENCE_THRESHOLD:
                        prediction_label = "fall"
                        display_confidence_value = prediction_probability_fall
                    else:
                        prediction_label = "no_fall"
                        display_confidence_value = 1.0 - prediction_probability_fall
                    
                    current_status_text_for_log = f"Frame {frame_count}: {prediction_label.upper()} (Conf: {display_confidence_value:.2f})"

                    current_video_time_sec = frame_count / fps
                    if prediction_label == "fall":
                        if (current_video_time_sec - local_last_fall_event_time) > FALL_EVENT_COOLDOWN: # ใช้ local_last_fall_event_time
                            fall_message = f"Frame {frame_count} (~{current_video_time_sec:.1f}s): FALL DETECTED! (Conf: {prediction_probability_fall:.2f})"
                            print(fall_message)
                            overall_status_updates.append(fall_message)
                            local_last_fall_event_time = current_video_time_sec # อัปเดตเวลา
                except Exception as e:
                    print(f"Frame {frame_count}: Error during prediction: {e}")
                    current_status_text_for_log = f"Frame {frame_count}: Prediction Error"
                    display_confidence_value = 0.0
            
            # อัปเดต overall_status_updates โดยใช้ current_status_text_for_log
            if "FALL DETECTED" not in current_status_text_for_log and \
               (frame_count % int(fps*1) == 0 or (len(local_feature_sequence) == INPUT_TIMESTEPS and frame_count == INPUT_TIMESTEPS) or frame_count ==1) :
                 if "Collecting..." not in current_status_text_for_log or frame_count == 1 :
                    overall_status_updates.append(current_status_text_for_log)


            # 3. วาด Landmarks (ถ้ามี) บน frame_for_display (BGR)
            if results.pose_landmarks:
                # Draw landmarks with our custom renderer
                temp_rgb_to_draw_landmarks = cv2.cvtColor(original_bgr_frame, cv2.COLOR_BGR2RGB).copy()
                try:
                    # Our results have normalized x,y in [0,1] and list of landmarks
                    _draw_landmarks_custom(temp_rgb_to_draw_landmarks, results.pose_landmarks.landmark)
                except Exception as e:
                    print('Warning: drawing landmarks failed:', e)
                # แปลงกลับเป็น BGR แล้วใช้เป็น frame_for_display ใหม่
                frame_for_display = cv2.cvtColor(temp_rgb_to_draw_landmarks, cv2.COLOR_RGB2BGR)
            # ถ้าไม่มี landmarks, frame_for_display จะยังคงเป็น original_bgr_frame.copy()

            # 4. วาด Text บน frame_for_display (BGR) ทางขวามือ
            font_face = cv2.FONT_HERSHEY_DUPLEX
            font_scale_status = 0.6
            thickness_status = 1
            font_scale_alert = 1
            thickness_alert = 2
            padding = 30 # ระยะห่างจากขอบ

            text_to_show_on_frame = f"{prediction_label.upper()} (Conf: {display_confidence_value:.2f})"
            if "Collecting" in current_status_text_for_log or "Error" in current_status_text_for_log: # ใช้ current_status_text_for_log
                 text_to_show_on_frame = current_status_text_for_log.split(': ')[-1]

            (text_w, text_h), _ = cv2.getTextSize(text_to_show_on_frame, font_face, font_scale_status, thickness_status)
            text_x_status = frame_for_display.shape[1] - text_w - padding
            text_y_status = padding + text_h

            status_color_bgr = (255, 255, 255) # เขียว (BGR)
            current_video_time_sec_for_alert_check = frame_count / fps
            if prediction_label == "fall" and not (current_video_time_sec_for_alert_check - local_last_fall_event_time < FALL_EVENT_COOLDOWN):
                status_color_bgr = (0, 165, 255) # สีส้ม (BGR)
            if "Error" in text_to_show_on_frame:
                status_color_bgr = (0,0,255) # สีแดง (BGR)

            cv2.putText(frame_for_display, text_to_show_on_frame, (text_x_status, text_y_status), font_face, font_scale_status, status_color_bgr, thickness_status, cv2.LINE_AA)
            
            if prediction_label == "fall" and (current_video_time_sec_for_alert_check - local_last_fall_event_time < FALL_EVENT_COOLDOWN):
                alert_text = "FALL DETECTED!"
                (alert_w, alert_h), _ = cv2.getTextSize(alert_text, font_face, font_scale_alert, thickness_alert)
                alert_x_pos = frame_for_display.shape[1] - alert_w - padding
                alert_y_pos = text_y_status + alert_h + padding // 2
                cv2.putText(frame_for_display, alert_text, (alert_x_pos, alert_y_pos), font_face, font_scale_alert, (0, 0, 255), thickness_alert, cv2.LINE_AA) # สีแดง (BGR)
            
            # *** END ***
            processed_frames_list.append(frame_for_display) # เพิ่ม BGR frame ที่วาดแล้ว

    cap.release()

    if not processed_frames_list:
        if os.path.exists(local_video_path):
            try: os.remove(local_video_path); print(f"Cleaned up temp copied file: {local_video_path}")
            except Exception as e: print(f"Could not remove temp copied file {local_video_path} after no frames: {e}")
        return None, "No frames processed. Video might be empty or unreadable after copy."

    output_temp_video_path = f"processed_gradio_output_{timestamp_str}.mp4"
    height, width, _ = processed_frames_list[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_temp_video_path, fourcc, fps, (width, height))
    for frame_out_bgr in processed_frames_list:
        video_writer.write(frame_out_bgr)
    video_writer.release()
    print(f"Processed video saved to: {output_temp_video_path}")
    
    summary_text = "Recent Events / Status:\n" + "\n".join(overall_status_updates[-15:])

    if os.path.exists(local_video_path):
        try: os.remove(local_video_path); print(f"Cleaned up temp copied file: {local_video_path}")
        except Exception as e: print(f"Could not remove temp copied file {local_video_path}: {e}")

    return output_temp_video_path, summary_text


# --- สร้าง Gradio Interface ---

# กำหนด list ของชื่อไฟล์ตัวอย่างของคุณ
example_filenames = [
    "fall_example_1.mp4",     # <<<< แก้ไขชื่อไฟล์ตามที่คุณใช้
    "fall_example_2.mp4",     # <<<< แก้ไขชื่อไฟล์ตามที่คุณใช้
    "fall_example_3.mp4",  # <<<< แก้ไขชื่อไฟล์ตามที่คุณใช้
    "fall_example_4.mp4"   # <<<< แก้ไขชื่อไฟล์ตามที่คุณใช้
]

examples_list_for_gradio = []
for filename in example_filenames:
    # ตรวจสอบว่าไฟล์ example มีอยู่ใน root directory ของ repo จริงๆ
    if os.path.exists(filename): # Gradio examples ต้องการแค่ชื่อไฟล์ (ถ้าอยู่ใน root)
        examples_list_for_gradio.append([filename]) # Gradio ต้องการ list ของ list
        print(f"Info: Example file '{filename}' found and added.")
    else:
        print(f"Warning: Example file '{filename}' not found in the repository root. It will not be added to examples.")

# Create Gradio Interface (wrapped to be tolerant of API differences on different Gradio versions)
try:
    iface = gr.Interface(
        fn=process_video_for_gradio,
        inputs=gr.Video(label="Upload Video File (.mp4)", sources=["upload"]),
        outputs=[
            gr.Video(label="Processed Video with Detections"),
            gr.Textbox(label="Detection Summary (Events / Status)")
        ],
        title="AI Fall Detection from Video",
        description="Upload a video file (MP4 format recommended) to detect falls. " \
                    "Processing may take time depending on video length.",
        examples=examples_list_for_gradio if examples_list_for_gradio else None, # <<<< ใช้ list ใหม่นี้
        allow_flagging="never",
        cache_examples=False
    )
except TypeError as e:
    # Older/newer gradio versions may not accept `allow_flagging` — retry without it
    print('Gradio Interface creation warning:', e)
    iface = gr.Interface(
        fn=process_video_for_gradio,
        inputs=gr.Video(label="Upload Video File (.mp4)", sources=["upload"]),
        outputs=[
            gr.Video(label="Processed Video with Detections"),
            gr.Textbox(label="Detection Summary (Events / Status)")
        ],
        title="AI Fall Detection from Video",
        description="Upload a video file (MP4 format recommended) to detect falls. " \
                    "Processing may take time depending on video length.",
        examples=examples_list_for_gradio if examples_list_for_gradio else None,
        cache_examples=False
    )

if __name__ == "__main__":
    iface.launch()