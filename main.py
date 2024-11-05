import json
import cv2
import face_recognition
import numpy as np
import paho.mqtt.client as mqtt
import time

email = file = open("tapo_username.txt", "r").read()
pw = file = open("tapo_password.txt", "r").read()
ip_address = '192.168.68.139'

mqtt_username = file = open("mqtt_username.txt", "r").read().strip().replace("\n", "")
mqtt_password = file = open("mqtt_password.txt", "r").read().strip().replace("\n", "")

MQTT_BROKER = "192.168.68.131"
MQTT_PORT = 1883
MQTT_USERNAME = mqtt_username
MQTT_PASSWORD = mqtt_password
MQTT_TOPIC = "homeassistant/binary_sensor/leon_is_present/config"
MQTT_STATE_TOPIC = "homeassistant/binary_sensor/leon_is_present/state"

mqtt_client = mqtt.Client()
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# MQTT Discovery Payload
discovery_payload = {
    "name": "Leon is Present",
    "state_topic": MQTT_STATE_TOPIC,
    "device_class": "presence",
    "payload_on": "ON",
    "payload_off": "OFF",
    "unique_id": "leon_presence_sensor",
    "value_template": "{{ value_json.state }}"
}

mqtt_client.publish(MQTT_TOPIC, json.dumps(discovery_payload), retain=True)

def main():
    rtsp_url = f'rtsp://{email}:{pw}@{ip_address}:554/stream1'

    known_face_encodings = []
    known_face_names = []

    leon_image = face_recognition.load_image_file("leon.jpg")
    leon_face_encoding = face_recognition.face_encodings(leon_image)[0]
    known_face_encodings.append(leon_face_encoding)
    known_face_names.append("Leon")

    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print('Error opening video stream or file')
        return

    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    leon_is_present = False
    absence_timer_started = False
    absent_time_threshold = 10
    process_frame_interval = 0.5
    last_frame_time = time.time()
    debug = False

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to retrieve frame")
            break

        current_time = time.time()
        if current_time - last_frame_time >= process_frame_interval:
            last_frame_time = current_time
            
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, known_face_locations=face_locations)

            leon_detected = False

            if face_encodings:
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(
                        known_face_encodings, face_encoding)

                    if matches[0]: 
                        leon_detected = True

            if leon_detected:
                absence_timer_started = False 

                if not leon_is_present:
                    leon_is_present = True
                    print("Leon is present")
                    mqtt_client.publish(MQTT_STATE_TOPIC, json.dumps({"state": "ON"}))

        if leon_is_present and not leon_detected:
            if not absence_timer_started:
                absence_timer_started = True
                last_absence_time = time.time()
            else:
                elapsed_time = time.time() - last_absence_time
                if elapsed_time >= absent_time_threshold:
                    print("Leon is absent")
                    mqtt_client.publish(MQTT_STATE_TOPIC, json.dumps({"state": "OFF"}))
                    leon_is_present = False
                    absence_timer_started = False 

        process_this_frame = not process_this_frame

        if debug:
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

                cv2.rectangle(frame, (left, bottom - 35),
                            (right, bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6),
                            font, 1.0, (255, 255, 255), 1)

            cv2.imshow('Facial Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
