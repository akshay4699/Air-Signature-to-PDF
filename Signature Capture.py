import cv2
import numpy as np
import mediapipe as mp

# Setup
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)

# White canvas (signature will be black)
canvas = np.ones((480, 640, 3), dtype=np.uint8) * 255

cap = cv2.VideoCapture(0)
prev_x, prev_y = None, None
drawing = False

# Utility: Check if a finger is up (by comparing y of tip and pip)
def finger_is_up(landmarks, tip_id, pip_id):
    return landmarks[tip_id].y < landmarks[pip_id].y

# Utility: Check for thumbs-up gesture
def is_thumbs_up(landmarks):
    thumb_up = landmarks[4].y < landmarks[3].y < landmarks[2].y
    other_fingers_down = all(landmarks[tip].y > landmarks[pip].y for tip, pip in [
        (8, 6), (12, 10), (16, 14), (20, 18)
    ])
    return thumb_up and other_fingers_down

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            lm = hand_landmarks.landmark

            # Detect gestures
            index_up = finger_is_up(lm, 8, 6)
            thumb_up = is_thumbs_up(lm)

            # Drawing state control
            if thumb_up:
                drawing = False
                prev_x, prev_y = None, None
                cv2.putText(frame, "Thumbs up - Drawing OFF", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            elif index_up:
                drawing = True
                cv2.putText(frame, "Index up - Drawing ON", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            # Get index fingertip
            x = int(lm[8].x * w)
            y = int(lm[8].y * h)

            # Draw on canvas
            if drawing:
                if prev_x is not None and prev_y is not None:
                    cv2.line(canvas, (prev_x, prev_y), (x, y), (0, 0, 0), 3)
                prev_x, prev_y = x, y
            else:
                prev_x, prev_y = None, None

            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Show frames
    overlay = cv2.addWeighted(frame, 0.5, canvas, 0.5, 0)
    cv2.imshow("Air Signature (Index = Draw, Thumb = Stop)", overlay)

    key = cv2.waitKey(1)
    if key == ord('s'):
        cv2.imwrite("signature_output.png", canvas)
        print("Signature saved as 'signature_output.png'")
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
