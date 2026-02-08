#!/usr/bin/env python3
"""
Fall detector with video recording feature.
Records 5 seconds before fall + 10 seconds after fall.
"""

import cv2
import mediapipe as mp
import numpy as np
# Prefer tflite-runtime, fall back to TensorFlow's TFLite interpreter
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
import sys
from collections import deque
import requests
import argparse
from dotenv import load_dotenv
import os
from datetime import datetime
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe import Image
from mediapipe.tasks.python.vision.core import image as mp_image_core

# Voice Intervention imports
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    print("WARNING: pyttsx3 not installed. Voice alerts disabled. Install with: pip install pyttsx3")
    TTS_AVAILABLE = False

try:
    import speech_recognition as sr
    STT_AVAILABLE = True
except ImportError:
    print("WARNING: speech_recognition not installed. Voice listening disabled. Install with: pip install SpeechRecognition pyaudio")
    STT_AVAILABLE = False

# --- Configuration ---
MODEL_PATH = 'fall_detection_transformer.tflite'
INPUT_TIMESTEPS = 30
FALL_CONFIDENCE_THRESHOLD = 0.70  # Adjusted for demo/testing
MIN_KEYPOINT_CONFIDENCE_FOR_NORMALIZATION = 0.3

# Fall confirmation settings (prevent false positives from proximity)
FALL_CONFIRMATION_FRAMES = 15  # Must detect fall for 15 consecutive frames (~0.5 sec) to avoid walking false positives
fall_confirmation_counter = 0  # Tracks consecutive fall detections

# Logging settings
ENABLE_VERBOSE_LOGGING = True  # Set to False to reduce log output
LOG_FALL_PROBABILITIES = True  # Log fall probabilities for analysis

# Voice Intervention settings
ENABLE_VOICE_INTERVENTION = True  # Speak and listen after fall detection
VOICE_LISTEN_TIMEOUT = 15  # Seconds to wait for voice response (starts after calibration)
VOICE_PHRASE_TIME_LIMIT = 15  # Max recording time for speech

# MediaPipe pose model
POSE_MODEL_PATH = os.environ.get('MP_POSE_MODEL_PATH', 'pose_landmarker_lite.task')

# Load .env
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ENABLE_TELEGRAM_ALERTS = True

# FastAPI Backend Configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://172.20.153.212:8000")  # Change to your backend URL
DEVICE_ID = os.getenv("DEVICE_ID", "webcam-01")  # Unique device identifier
ENABLE_BACKEND_UPLOAD = True  # Set to False to disable backend integration

CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DISPLAY_WINDOW_NAME = "Fall Detection with Recording (Press 'q' to quit)"

LOG_FILE = "fall_detection_log.txt"
FALL_EVENT_COOLDOWN = 10  # seconds

# --- VIDEO RECORDING SETTINGS ---
ENABLE_RECORDING = True
PRE_FALL_SECONDS = 5   # Record 5 seconds before fall
POST_FALL_SECONDS = 10  # Record 10 seconds after fall
RECORDING_OUTPUT_DIR = "fall_recordings"  # Directory to save recordings
VIDEO_CODEC = 'mp4v'  # or 'XVID' for .avi
SAVE_VIDEO_FPS = 30  # Fixed FPS to save videos at to avoid slow-motion playback

# Create recordings directory if it doesn't exist
if ENABLE_RECORDING and not os.path.exists(RECORDING_OUTPUT_DIR):
    os.makedirs(RECORDING_OUTPUT_DIR)
    print(f"Created recordings directory: {RECORDING_OUTPUT_DIR}")

# ----- KEYPOINT DEFINITIONS -----
KEYPOINT_NAMES_ORIGINAL = [
    'Nose', 'Left Eye Inner', 'Left Eye', 'Left Eye Outer', 'Right Eye Inner', 'Right Eye', 'Right Eye Outer',
    'Left Ear', 'Right Ear', 'Mouth Left', 'Mouth Right',
    'Left Shoulder', 'Right Shoulder', 'Left Elbow', 'Right Elbow', 'Left Wrist', 'Right Wrist',
    'Left Pinky', 'Right Pinky', 'Left Index', 'Right Index', 'Left Thumb', 'Right Thumb',
    'Left Hip', 'Right Hip', 'Left Knee', 'Right Knee', 'Left Ankle', 'Right Ankle',
    'Left Heel', 'Right Heel', 'Left Foot Index', 'Right Foot Index'
]

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

print("--- Initializing Fall Detector with Recording ---")
print(f"PRE-FALL BUFFER: {PRE_FALL_SECONDS} seconds")
print(f"POST-FALL RECORDING: {POST_FALL_SECONDS} seconds")
print(f"Recordings saved to: {RECORDING_OUTPUT_DIR}/")
print(f"NUM_FEATURES: {NUM_FEATURES}")
print("-----------------------------------------------------")

# --- Load TFLite Model ---
try:
    interpreter = tflite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    print(f"TFLite Model Loaded: {MODEL_PATH}")
except Exception as e:
    print(f"Error loading TFLite model: {e}")
    exit()

# --- Global Variables ---
feature_sequence = deque(maxlen=INPUT_TIMESTEPS)
last_fall_event_time = 0
fall_confirmation_counter = 0  # Consecutive frames with fall detected

# VIDEO RECORDING BUFFERS
frame_buffer = None  # Will be initialized after we know FPS
recording_state = {
    'is_recording': False,
    'post_fall_frames_remaining': 0,
    'video_writer': None,
    'filename': None,
    'fall_timestamp': None,  # ISO timestamp when fall was confirmed
    'fall_confidence': 0.0,   # Confidence score of the fall
    'voice_response': None,   # Voice response from user after fall
    'processing_complete': False  # Flag to prevent double execution
}

# TTS and STT engines will be initialized after log_message is defined
tts_engine = None
recognizer = None

# --- Helper Functions ---
def log_message(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Error writing to log file: {e}")

def send_telegram_message(message):
    if not ENABLE_TELEGRAM_ALERTS or TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID":
        if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_TELEGRAM_CHAT_ID":
             print("INFO: Telegram not configured. Alerts will not be sent.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'Markdown'}
    try:
        response = requests.post(url, data=payload, timeout=10)
        response.raise_for_status()
        if response.json().get('ok', False):
            print(f"INFO: Telegram message sent successfully.")
    except requests.exceptions.RequestException as e:
        log_message(f"Error sending Telegram message: {e}")

# --- VOICE INTERVENTION FUNCTIONS ---
def initialize_voice_systems():
    """Initialize TTS and STT systems after log_message is available."""
    global tts_engine, recognizer
    
    # Initialize TTS engine
    if TTS_AVAILABLE:
        try:
            tts_engine = pyttsx3.init()
            # Adjust voice properties
            tts_engine.setProperty('rate', 150)  # Speed of speech
            tts_engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
            log_message("🔊 Text-to-Speech initialized")
        except Exception as e:
            log_message(f"⚠️  TTS initialization failed: {e}")
    
    # Initialize speech recognizer
    if STT_AVAILABLE:
        recognizer = sr.Recognizer()
        log_message("🎤 Speech Recognition initialized")

def speak_alert(message):
    """Speak a message out loud using text-to-speech."""
    if not ENABLE_VOICE_INTERVENTION:
        return
    
    try:
        log_message(f"🔊 Speaking: '{message}'")
        print(f"\n{'='*60}\n🔊 SPEAKING NOW: '{message}'\n{'='*60}\n", flush=True)
        
        # Use macOS 'say' command for reliable audio playback
        # This works better than pyttsx3 when video is running
        import subprocess
        subprocess.run(['say', '-v', 'Samantha', '-r', '175', message], check=True)
        
        print(f"✅ Audio playback completed\n", flush=True)
        
        # Wait for audio device to be released before next operation
        time.sleep(0.5)
    except Exception as e:
        log_message(f"⚠️  TTS error: {e}")
        print(f"⚠️  TTS error: {e}\n", flush=True)

def listen_for_response():
    """Listen for voice response from the user."""
    if not ENABLE_VOICE_INTERVENTION or not STT_AVAILABLE or recognizer is None:
        return None
    
    try:
        # Wait a short period to allow audio device release after TTS
        log_message("🎤 Preparing microphone (waiting for audio device)...")
        time.sleep(2.5)

        if not STT_AVAILABLE or recognizer is None:
            log_message("⚠️  Speech-to-text not available (recognizer not initialized)")
            return "ERROR"

        log_message("🎤 Listening for voice response...")
        print("\n" + "="*60, flush=True)
        print("  🎤 MICROPHONE ACTIVATED - PLEASE SPEAK NOW!", flush=True)
        print("="*60 + "\n", flush=True)

        # Try to explicitly instantiate the microphone object before entering context
        mic = None
        try:
            mic = sr.Microphone(device_index=0)
        except Exception as e:
            log_message(f"❌ Failed to create Microphone object: {e}")
            return "ERROR"

        # Try to enter microphone context and listen
        try:
            with mic as source:
                # Fine-tune recognizer sensitivity
                recognizer.energy_threshold = 300
                recognizer.dynamic_energy_threshold = False

                log_message("🎤 Adjusting for ambient noise (1 second)...")
                print("🔊 Calibrating microphone...\n", flush=True)
                try:
                    recognizer.adjust_for_ambient_noise(source, duration=1.0)
                except Exception as e:
                    log_message(f"⚠️  adjust_for_ambient_noise failed: {e}")

                log_message(f"🎤 READY! Listening for up to {VOICE_LISTEN_TIMEOUT}s...")
                print("" + "*"*60, flush=True)
                print("  *** SPEAK NOW - SYSTEM IS LISTENING ***", flush=True)
                print("" + "*"*60 + "\n", flush=True)

                try:
                    audio = recognizer.listen(
                        source,
                        timeout=VOICE_LISTEN_TIMEOUT,
                        phrase_time_limit=VOICE_PHRASE_TIME_LIMIT
                    )
                except sr.WaitTimeoutError:
                    log_message("⏱️  No response heard (timeout - no speech detected)")
                    return "NO_RESPONSE"
                except KeyboardInterrupt:
                    log_message("⚠️  Listening interrupted by user")
                    return "INTERRUPTED"

                log_message("🎤 Audio captured! Processing...")
                print("\n🔄 Processing your response (this may take a few seconds)...\n", flush=True)

                try:
                    text = recognizer.recognize_google(audio)
                    log_message(f"🗣️  Heard: '{text}'")
                    print("\n" + "="*60, flush=True)
                    print(f"  ✅ YOU SAID: '{text}'", flush=True)
                    print("="*60 + "\n", flush=True)
                    return text
                except sr.UnknownValueError:
                    log_message("⚠️  Could not understand audio (speech unclear)")
                    return "UNCLEAR"
                except sr.RequestError as e:
                    log_message(f"❌ Speech recognition request failed: {e}")
                    return "ERROR"

        except Exception as e:
            log_message(f"❌ Microphone context/listen error: {e}")
            return "ERROR"

    except KeyboardInterrupt:
        raise
    except Exception as e:
        log_message(f"❌ Unexpected error during listening: {e}")
        import traceback
        log_message(f"Traceback: {traceback.format_exc()}")
        return "ERROR"

def get_kpt_indices_training_order(keypoint_name):
    if keypoint_name not in KEYPOINT_DICT_TRAINING:
        raise ValueError(f"Keypoint '{keypoint_name}' not found")
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
    except ValueError:
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
        x_col, y_col, _ = get_kpt_indices_training_order(kp_name_sorted)
        normalized_frame[x_col] -= mid_hip_x
        normalized_frame[y_col] -= mid_hip_y
        if perform_scaling:
            normalized_frame[x_col] /= reference_height
            normalized_frame[y_col] /= reference_height

    return normalized_frame

# Helper classes
class _Landmark:
    def __init__(self, x, y, z=0.0, visibility=1.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.visibility = float(visibility)

class _PoseResults:
    def __init__(self, landmarks):
        class LMHolder:
            def __init__(self, landmark_list):
                self.landmark = landmark_list
        self.pose_landmarks = LMHolder(landmarks) if landmarks else None

def extract_and_normalize_features(pose_results):
    frame_features_sorted = np.zeros(NUM_FEATURES, dtype=np.float32)
    if pose_results.pose_landmarks:
        landmarks = pose_results.pose_landmarks.landmark
        for mp_landmark_idx, your_kp_name in MEDIAPIPE_TO_YOUR_KEYPOINTS_MAPPING.items():
            if your_kp_name in KEYPOINT_DICT_TRAINING:
                try:
                    if mp_landmark_idx < len(landmarks):
                        lm = landmarks[mp_landmark_idx]
                        x_idx, y_idx, c_idx = get_kpt_indices_training_order(your_kp_name)
                        frame_features_sorted[x_idx] = lm.x
                        frame_features_sorted[y_idx] = lm.y
                        frame_features_sorted[c_idx] = getattr(lm, 'visibility', 1.0)
                except:
                    pass
    normalized_features = normalize_skeleton_frame(frame_features_sorted.copy())
    return normalized_features

# Drawing
POSE_CONNECTIONS = [
    (0,1),(0,2),(1,3),(2,4),(5,6),(5,7),(7,9),(6,8),(8,10),(11,12),(11,13),(13,15),(12,14),(14,16),
    (15,17),(16,18),(15,19),(19,21),(16,20),(20,22),(11,23),(12,24),(23,24),(23,25),(24,26),
    (25,27),(26,28),(27,29),(28,30),(29,31),(30,32)
]

def _draw_landmarks_custom(image_bgr, landmarks):
    h, w = image_bgr.shape[:2]
    for a, b in POSE_CONNECTIONS:
        if a < len(landmarks) and b < len(landmarks):
            pt1 = (int(landmarks[a].x * w), int(landmarks[a].y * h))
            pt2 = (int(landmarks[b].x * w), int(landmarks[b].y * h))
            cv2.line(image_bgr, pt1, pt2, (0,255,0), 2)
    for lm in landmarks:
        cv2.circle(image_bgr, (int(lm.x * w), int(lm.y * h)), 3, (0,0,255), -1)

# --- VIDEO RECORDING FUNCTIONS ---
def start_recording(fps):
    """Initialize video recording."""
    global recording_state
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(RECORDING_OUTPUT_DIR, f"fall_{timestamp}.mp4")
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*VIDEO_CODEC)
    # Use fixed save frame rate to avoid slow-motion clips when processing reduces runtime FPS
    save_fps = int(SAVE_VIDEO_FPS)
    video_writer = cv2.VideoWriter(filename, fourcc, save_fps, (FRAME_WIDTH, FRAME_HEIGHT))
    
    if not video_writer.isOpened():
        log_message(f"❌ ERROR: Could not open video writer for {filename}")
        return False
    
    recording_state['is_recording'] = True
    recording_state['video_writer'] = video_writer
    recording_state['filename'] = filename
    # post_fall_frames_remaining is based on save FPS to match final clip duration
    recording_state['post_fall_frames_remaining'] = int(POST_FALL_SECONDS * save_fps)
    
    log_message(f"📹 RECORDING STARTED: {filename} (will record {POST_FALL_SECONDS}s post-fall at {save_fps} FPS)")
    return True

def write_buffered_frames():
    """Write pre-fall buffered frames to video file."""
    global frame_buffer, recording_state
    
    if frame_buffer is None or recording_state['video_writer'] is None:
        return
    
    frames_written = 0
    for frame in frame_buffer:
        recording_state['video_writer'].write(frame)
        frames_written += 1
    
    log_message(f"📼 Wrote {frames_written} buffered frames ({PRE_FALL_SECONDS}s pre-fall footage)")

def write_frame(frame):
    """Write a single frame to the current recording."""
    global recording_state
    
    if recording_state['video_writer'] is not None:
        recording_state['video_writer'].write(frame)
        recording_state['post_fall_frames_remaining'] -= 1
        
        # Check if we're done recording
        if recording_state['post_fall_frames_remaining'] <= 0:
            stop_recording()

def upload_to_backend(video_path, timestamp, confidence, voice_response=None):
    """Upload fall event + video to FastAPI backend."""
    if not ENABLE_BACKEND_UPLOAD:
        return

    if not os.path.exists(video_path):
        log_message(f"❌ Video file not found: {video_path}")
        return

    try:
        # Handle no-response cases
        if voice_response in ["UNCLEAR", "NO_RESPONSE", "ERROR"]:
            voice_response = "patient did not respond"
            log_message(f"📤 Patient did not respond - sending to backend")
        
        log_message(f"📤 Uploading to backend: {BACKEND_API_URL}/upload")
        if voice_response:
            log_message(f"📤 Including voice response: {voice_response}")

        # Prepare multipart/form-data
        files = {'file': (os.path.basename(video_path), open(video_path, 'rb'), 'video/mp4')}
        data = {
            'device_id': DEVICE_ID,
            'confidence': float(confidence),
            'timestamp': timestamp
        }
        
        # Add voice response if available
        if voice_response:
            data['voice_response'] = voice_response

        response = requests.post(
            f"{BACKEND_API_URL}/upload",
            files=files,
            data=data,
            timeout=60
        )
        response.raise_for_status()

        log_message(f"✅ Uploaded to backend successfully: {response.json()}")

    except requests.exceptions.RequestException as e:
        log_message(f"❌ Backend upload failed: {e}")
    except Exception as e:
        log_message(f"❌ Error during backend upload: {e}")


def stop_recording():
    """Stop and finalize video recording."""
    global recording_state
    
    # Prevent double execution
    if recording_state.get('processing_complete', False):
        return
    
    recording_state['processing_complete'] = True
    
    if recording_state['video_writer'] is not None:
        recording_state['video_writer'].release()
        log_message(f"✅ RECORDING COMPLETE: {recording_state['filename']} (15s total: {PRE_FALL_SECONDS}s pre + {POST_FALL_SECONDS}s post)")
        
        # Voice intervention: Speak and listen (wrapped in try/except to prevent crashes)
        voice_response = None
        if ENABLE_VOICE_INTERVENTION:
            try:
                print("\n" + "="*60)
                print("  🔊 VOICE INTERVENTION STARTING...")
                print("="*60 + "\n", flush=True)
                
                speak_alert("A fall was detected. Are you okay? Please speak now if you are able to.")
                voice_response = listen_for_response()
                recording_state['voice_response'] = voice_response
                log_message(f"✅ Voice intervention completed. Response: {voice_response}")
                
                print("\n" + "="*60)
                print(f"  🗣️  USER RESPONSE: {voice_response}")
                print("="*60 + "\n", flush=True)
                
                # Comforting message after response
                speak_alert("Your information has been shared. Help is on the way. Please stay calm.")
                
                print("\n" + "="*60)
                print("  ✅ FALL DETECTION COMPLETE - EXITING")
                print("="*60 + "\n", flush=True)
            except Exception as e:
                log_message(f"⚠️  Voice intervention failed: {e}")
                import traceback
                log_message(f"Traceback: {traceback.format_exc()}")
                voice_response = "ERROR"
        
        # Upload to backend after recording completes
        if recording_state['filename'] and recording_state['fall_timestamp']:
            try:
                upload_to_backend(
                    recording_state['filename'],
                    recording_state['fall_timestamp'],
                    recording_state['fall_confidence'],
                    voice_response
                )
            except Exception as e:
                log_message(f"⚠️  Backend upload failed: {e}")
        
        # Exit app after fall handling is complete
        log_message("🛑 Fall detection cycle complete - shutting down")
        sys.exit(0)
        
    recording_state['is_recording'] = False
    recording_state['video_writer'] = None
    recording_state['filename'] = None
    recording_state['post_fall_frames_remaining'] = 0
    recording_state['fall_timestamp'] = None
    recording_state['fall_confidence'] = 0.0
    recording_state['voice_response'] = None
    recording_state['processing_complete'] = False

# --- PROCESS FRAME ---
def process_frame(frame, pose_landmarker, frame_count, fps):
    global feature_sequence, last_fall_event_time, frame_buffer, recording_state, fall_confirmation_counter
    
    processed_frame_display = frame.copy()
    
    # Pose detection
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = Image(image_format=mp_image_core.ImageFormat.SRGB, data=image_rgb)
    timestamp_ms = int((frame_count / fps) * 1000)
    
    try:
        detection_result = pose_landmarker.detect_for_video(mp_image, timestamp_ms)
    except:
        detection_result = pose_landmarker.detect(mp_image)
    
    landmarks_list = []
    if hasattr(detection_result, 'pose_landmarks') and detection_result.pose_landmarks:
        if len(detection_result.pose_landmarks) > 0:
            for lm in detection_result.pose_landmarks[0]:
                landmarks_list.append(_Landmark(lm.x, lm.y, lm.z, getattr(lm, 'visibility', 1.0)))
    results = _PoseResults(landmarks_list)
    
    # Extract features
    current_features = extract_and_normalize_features(results)
    feature_sequence.append(current_features)
    
    # Prediction
    prediction_label = "no_fall"
    fall_probability = 0.0
    display_confidence = 0.0
    status_text = "Collecting data..."
    
    if len(feature_sequence) == INPUT_TIMESTEPS:
        model_input = np.array(feature_sequence, dtype=np.float32)
        model_input = np.expand_dims(model_input, axis=0)
        
        try:
            interpreter.set_tensor(input_details[0]['index'], model_input)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])
            fall_probability = output[0][0]
            
            if fall_probability >= FALL_CONFIDENCE_THRESHOLD:
                fall_confirmation_counter += 1
                prediction_label = "fall"
                display_confidence = fall_probability
                
                # Log fall verification progress
                if ENABLE_VERBOSE_LOGGING and fall_confirmation_counter <= FALL_CONFIRMATION_FRAMES:
                    if fall_confirmation_counter == 1:
                        log_message(f"⚠️  Fall detected! Verifying... ({fall_confirmation_counter}/{FALL_CONFIRMATION_FRAMES}) - Prob: {fall_probability*100:.1f}%")
                    elif fall_confirmation_counter % 2 == 0:  # Log every other frame to reduce spam
                        log_message(f"⚠️  Verifying fall... ({fall_confirmation_counter}/{FALL_CONFIRMATION_FRAMES}) - Prob: {fall_probability*100:.1f}%")
                
                # TRIGGER RECORDING only after consecutive confirmations
                if fall_confirmation_counter >= FALL_CONFIRMATION_FRAMES:
                    current_time = time.time()
                    # Don't process new falls if we're already handling one
                    if (current_time - last_fall_event_time) > FALL_EVENT_COOLDOWN and not recording_state.get('processing_complete', False):
                        # Store fall metadata
                        fall_timestamp_iso = datetime.now().isoformat()
                        
                        if ENABLE_RECORDING and not recording_state['is_recording']:
                            # Store metadata for later upload
                            recording_state['fall_timestamp'] = fall_timestamp_iso
                            recording_state['fall_confidence'] = float(fall_probability)
                            
                            if start_recording(fps):
                                write_buffered_frames()  # Write pre-fall frames
                        
                        # Send alert
                        confidence_str = f"{fall_probability * 100:.2f}%"
                        fall_message = f"🚨 FALL CONFIRMED! Timestamp: {fall_timestamp_iso}, Confidence: {confidence_str} (verified over {fall_confirmation_counter} frames)"
                        log_message(fall_message)
                        print("\n" + "="*60)
                        print(f"  🚨 FALL DETECTED! Confidence: {confidence_str}")
                        print("  📹 Recording 15-second video clip...")
                        print("="*60 + "\n", flush=True)
                        send_telegram_message(fall_message)
                        last_fall_event_time = current_time
                        fall_confirmation_counter = 0  # Reset after triggering
            else:
                prediction_label = "no_fall"
                display_confidence = 1.0 - fall_probability
                
                # Log when fall verification is cancelled
                if fall_confirmation_counter > 0 and ENABLE_VERBOSE_LOGGING:
                    log_message(f"ℹ️  Fall verification cancelled (was {fall_confirmation_counter}/{FALL_CONFIRMATION_FRAMES}) - Prob dropped to {fall_probability*100:.1f}%")
                
                fall_confirmation_counter = 0  # Reset counter when no fall detected
            
            status_text = f"{prediction_label.upper()} (Conf: {display_confidence:.2f})"
        except Exception as e:
            log_message(f"Prediction error: {e}")
            status_text = "Prediction Error"
    
    # Draw skeleton
    if results.pose_landmarks:
        temp_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).copy()
        _draw_landmarks_custom(temp_rgb, results.pose_landmarks.landmark)
        processed_frame_display = cv2.cvtColor(temp_rgb, cv2.COLOR_RGB2BGR)
    elif ENABLE_VERBOSE_LOGGING and frame_count % 30 == 0:  # Log every second
        log_message(f"⚠️  No pose detected in frame {frame_count}")
    
    # Draw fall probability bar and percentage
    if len(feature_sequence) == INPUT_TIMESTEPS:
        # Fall probability percentage (large display)
        prob_percent = fall_probability * 100
        prob_text = f"Fall: {prob_percent:.1f}%"
        
        # Color based on probability
        if fall_probability >= FALL_CONFIDENCE_THRESHOLD:
            prob_color = (0, 0, 255)  # Red for fall
        elif fall_probability >= 0.5:
            prob_color = (0, 165, 255)  # Orange for warning
        else:
            prob_color = (0, 255, 0)  # Green for normal
        
        # Large probability text (bottom left)
        cv2.putText(processed_frame_display, prob_text, 
                   (10, processed_frame_display.shape[0] - 50),
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, prob_color, 2, cv2.LINE_AA)
        
        # Progress bar
        bar_width = 300
        bar_height = 25
        bar_x = 10
        bar_y = processed_frame_display.shape[0] - 30
        
        # Background bar
        cv2.rectangle(processed_frame_display, 
                     (bar_x, bar_y), 
                     (bar_x + bar_width, bar_y + bar_height),
                     (60, 60, 60), -1)
        
        # Filled bar based on probability
        filled_width = int(bar_width * fall_probability)
        cv2.rectangle(processed_frame_display, 
                     (bar_x, bar_y), 
                     (bar_x + filled_width, bar_y + bar_height),
                     prob_color, -1)
        
        # Threshold line
        threshold_x = bar_x + int(bar_width * FALL_CONFIDENCE_THRESHOLD)
        cv2.line(processed_frame_display, 
                (threshold_x, bar_y), 
                (threshold_x, bar_y + bar_height),
                (255, 255, 255), 2)
        
        # Posture status text (top left)
        if prediction_label == "fall":
            if fall_confirmation_counter >= FALL_CONFIRMATION_FRAMES:
                posture_status = "FALLING!"
                posture_color = (0, 0, 255)  # Red - confirmed fall
            else:
                posture_status = f"Verifying fall... ({fall_confirmation_counter}/{FALL_CONFIRMATION_FRAMES})"
                posture_color = (0, 165, 255)  # Orange - verifying
        else:
            posture_status = "Normal Posture"
            posture_color = (0, 255, 0)  # Green
        
        cv2.putText(processed_frame_display, posture_status, 
                   (10, 40),
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, posture_color, 2, cv2.LINE_AA)
    else:
        # Collecting data message
        cv2.putText(processed_frame_display, "Collecting data...", 
                   (10, 40),
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 0), 2, cv2.LINE_AA)
    
    # Recording indicator (top right)
    if recording_state['is_recording']:
        remaining_sec = recording_state['post_fall_frames_remaining'] / fps
        cv2.circle(processed_frame_display, 
                  (processed_frame_display.shape[1] - 30, 30), 10, (0, 0, 255), -1)  # Red dot
        cv2.putText(processed_frame_display, f"REC {remaining_sec:.1f}s", 
                   (processed_frame_display.shape[1] - 150, 40), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
    
    # Skeleton detection indicator (top right)
    skeleton_detected = "Skeleton: YES" if results.pose_landmarks else "Skeleton: NO"
    skeleton_color = (0, 255, 0) if results.pose_landmarks else (0, 0, 255)
    cv2.putText(processed_frame_display, skeleton_detected, 
               (processed_frame_display.shape[1] - 200, 70),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, skeleton_color, 2, cv2.LINE_AA)
    
    # Write raw (unannotated) frame if recording so backend receives original footage
    if recording_state['is_recording']:
        write_frame(frame)
    
    return processed_frame_display

# --- MAIN ---
def main(source_type, file_path=None):
    global frame_buffer
    
    log_message("Starting Fall Detection System with Recording...")
    
    # Initialize voice systems (TTS and STT)
    initialize_voice_systems()
    
    if source_type == "webcam":
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            log_message(f"Error: Cannot open webcam {CAMERA_INDEX}")
            return
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    else:
        cap = cv2.VideoCapture(file_path)
        if not cap.isOpened():
            log_message(f"Error: Cannot open video file {file_path}")
            return
    
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    
    # Initialize frame buffer for pre-fall recording
    buffer_size = int(PRE_FALL_SECONDS * fps)
    frame_buffer = deque(maxlen=buffer_size)
    log_message(f"📊 Frame buffer initialized: {buffer_size} frames ({PRE_FALL_SECONDS}s at {fps:.1f} FPS)")
    log_message(f"📊 Fall confirmation requires: {FALL_CONFIRMATION_FRAMES} consecutive frames (~{FALL_CONFIRMATION_FRAMES/fps:.2f}s)")
    log_message(f"📊 Verbose logging: {'ENABLED' if ENABLE_VERBOSE_LOGGING else 'DISABLED'}")
    
    # Initialize pose detector
    base_options = BaseOptions(model_asset_path=POSE_MODEL_PATH)
    options = PoseLandmarkerOptions(
        base_options=base_options,
        running_mode=RunningMode.VIDEO,
        min_pose_detection_confidence=0.5,
        min_pose_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )
    landmarker = PoseLandmarker.create_from_options(options)
    
    try:
        frame_counter = 0
        log_message(f"🎥 Starting frame processing loop...")
        
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                if source_type == "file":
                    log_message("📹 End of video file.")
                else:
                    log_message("❌ Failed to grab frame.")
                break
            
            frame_counter += 1
            
            # Log periodic status
            if ENABLE_VERBOSE_LOGGING and frame_counter % 300 == 0:  # Every 10 seconds at 30fps
                log_message(f"📊 Status: {frame_counter} frames processed, Recording: {recording_state['is_recording']}")
            
            # Add frame to buffer (for pre-fall recording)
            frame_buffer.append(frame.copy())
            
            # Process frame
            processed_frame = process_frame(frame, landmarker, frame_counter, fps)
            cv2.imshow(DISPLAY_WINDOW_NAME, processed_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                log_message("👋 User requested exit. Shutting down...")
                break
    finally:
        # Clean up any active recording
        if recording_state['is_recording']:
            log_message("⚠️  Finalizing active recording before shutdown...")
            stop_recording()
        
        log_message(f"📊 Session summary: {frame_counter} frames processed")
        landmarker.close()
        cap.release()
        cv2.destroyAllWindows()
        log_message("🛑 Fall Detection System Stopped.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fall Detection System with Video Recording")
    parser.add_argument("--source", type=str, default="webcam", choices=["webcam", "file"])
    parser.add_argument("--file", type=str, default=None)
    args = parser.parse_args()
    
    if args.source == "file" and not args.file:
        parser.error("--file argument required when source is 'file'")
    
    main(source_type=args.source, file_path=args.file)
