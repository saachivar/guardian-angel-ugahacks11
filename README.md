# 🛡️ Guardian Angel

> **🏆 Winner at [Insert Hackathon Name]**  
> *A real-time, edge-computed fall detection and multi-channel caregiver alert system.*

---

## 📌 Overview

**Guardian Angel** is an IoT-enabled safety system built to protect seniors and individuals with mobility challenges. 

When a fall occurs, the system detects it instantly on-device using edge computer vision, records a short video snippet for context, and dispatches immediate alerts across a Flutter mobile app, direct phone communications, and in-home Amazon Alexa devices. By cutting down response time, Guardian Angel helps turn critical, survivable incidents into immediate action.

---

## ✨ Key Features

- **⚡ On-Device Fall Detection:** Real-time pose estimation and fall classification running locally on edge hardware with minimal latency.
- **📹 Automated Clip Capture:** Automatically records and stores short video context clips upon event detection.
- **📱 Caregiver Mobile App:** Real-time push alerts, live status updates, and instant video playback for immediate triage.
- **🗣️ Smart Home Integration:** AWS Lambda-powered Amazon Alexa voice broadcasts within the home for hands-free warnings.
- **🔒 Privacy & Safety Focused:** Optimized to reduce false negatives while processing keypoints locally before cloud dispatch.

---

## 🏗️ System Architecture & Tech Stack

[ Edge Device / Camera ] ──(MediaPipe + TFLite)──> [ Fall Detected ]
│
▼
[ Caregiver Mobile App ] <──(Flutter)─── [ FastAPI + MongoDB ] ───(AWS Lambda)──> [ Amazon Alexa ]

### **Core Technologies**

* **Computer Vision & ML:** Python, OpenCV, MediaPipe Pose, TensorFlow Lite (TFLite Transformer Model)
* **Backend & API:** FastAPI, MongoDB, Python
* **Mobile Frontend:** Flutter, Dart
* **Cloud & Voice Services:** Amazon Web Services (AWS Lambda), Alexa Skills Kit
* **Tools & Environment:** Git, GitHub, Kaggle, Gradio

---

## 🧠 Engineering & ML Insights

* **Pose Estimation:** Extracted 17 human body keypoints per frame using MediaPipe Pose.
* **Temporal Sequence Modeling:** Leveraged a custom-trained TFLite Transformer architecture over traditional LSTMs/Bi-LSTMs to better capture long-range spatial-temporal motion patterns.
* **Safety-Critical Metrics:** Designed model evaluation around high recall and $F_1$ scores to strictly minimize false negatives (missed falls).
* **Edge Optimization:** Transformed and quantized models to TFLite for resource-constrained, always-on edge deployment.

---

## 🚀 Future Roadmap

- [ ] **Multi-Person Detection:** Scaling pose tracking algorithms for shared living spaces and care facilities.
- [ ] **Dataset Expansion:** Diversifying training data across varied angles, lighting conditions, and body types.
- [ ] **Fall Severity Classification:** Distinguishing between low-impact drops and severe falls to prioritize emergency triage.
- [ ] **Direct SMS & EMS Integration:** Adding automated cellular fail-safes and health provider integrations.
- [ ] **Ultra-Low-Power Edge Runtime:** Further optimizing model graph execution to reduce device power draw.

---

## 👥 Authors

Built with ❤️ at **[Insert Hackathon Name]**.
