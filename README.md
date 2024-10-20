# Leon Presence Detection with MQTT Integration

This project uses facial recognition to detect Leon's presence in front of an RTSP-enabled camera. If Leon is detected, the system publishes an "ON" state to an MQTT topic. If Leon is absent for 20 consecutive seconds, the system publishes an "OFF" state to the MQTT topic.

## Features

- Detects Leon’s face in real-time using an RTSP camera feed.
- Publishes Leon's presence (`ON`) or absence (`OFF`) to an MQTT broker after a 20-second threshold.
- Processes video frames once every 2 seconds to reduce CPU usage.
- Utilizes the `face_recognition` library for facial detection and `paho-mqtt` for MQTT messaging.

## Prerequisites

Before running the project, make sure you have the following installed:

- Python 3.x
- `paho-mqtt` library for MQTT messaging
- `face_recognition` library for facial recognition
- `OpenCV` for video capture and processing
- A camera supporting RTSP feed
- MQTT broker setup (e.g., Home Assistant's Mosquitto add-on)

### Installing Required Python Libraries

To install the required dependencies, you can run:

```bash
pip install paho-mqtt face_recognition opencv-python
