import cv2
import face_recognition
import numpy as np
from .face_db import get_all_users

def capture_face_encoding(frame):
    """
    Capture face encoding from a given frame
    Returns the face encoding if a face is detected, None otherwise
    """
    try:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        
        if faces:
            encodings = face_recognition.face_encodings(rgb, faces)
            if encodings:
                return encodings[0]  # Return the first face encoding
        return None
    except Exception as e:
        print(f"Error capturing face encoding: {e}")
        return None

def recognize_face():
    """
    Recognize faces in real-time using webcam
    Returns the name of recognized person, None if not recognized
    """
    known_users = get_all_users()
    known_encodings = [enc for _, enc in known_users]
    known_names = [name for name, _ in known_users]

    cap = cv2.VideoCapture(0)
    recognized_name = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, faces)

        for face_encoding in encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    recognized_name = known_names[best_match_index]
                    cap.release()
                    cv2.destroyAllWindows()
                    return recognized_name

        cv2.imshow("Facial Attendance", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None