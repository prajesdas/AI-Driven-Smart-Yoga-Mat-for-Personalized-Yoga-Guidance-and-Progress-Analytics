import cv2
import mediapipe as mp
import numpy as np
import math

# Initialize MediaPipe Pose and Drawing Utils
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Function to calculate angle between three points (landmarks)
def calculate_angle(a, b, c):
    a = np.array(a)  # First point (e.g., Shoulder)
    b = np.array(b)  # Middle point (e.g., Elbow)
    c = np.array(c)  # End point (e.g., Wrist)

    # Calculate vectors
    ba = a - b
    bc = c - b

    # Calculate angle using the dot product formula
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    # Convert to degrees and normalize to 0-180
    angle = np.degrees(angle)
    if angle > 180:
        angle = 360 - angle  # Adjust for the convex angle if needed

    return angle

# --- Main Logic ---
cap = cv2.VideoCapture(0)  # Video capture from webcam (0)

# Counter variables
count = 0
stage = None  # 'up' or 'down'

# Setup MediaPipe instance
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            continue

        # Convert the BGR image to RGB.
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Process the image and get pose landmarks
        results = pose.process(image)

        # Convert the image back to BGR.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates for the right arm
            shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
            wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                     landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Calculate elbow angle
            angle = calculate_angle(shoulder, elbow, wrist)

            # Display angle on screen
            cv2.putText(image, str(int(angle)), 
                        tuple(np.multiply(elbow, [image.shape[1], image.shape[0]]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

            # Pushup counting logic
            # Pushup DOWN: Angle at elbow is acute (e.g., < 90 degrees)
            if angle < 90:
                stage = "down"
            
            # Pushup UP: Angle at elbow is close to straight (e.g., > 160 degrees)
            if angle > 160 and stage == 'down':
                stage = "up"
                count += 1
                
        except:
            pass # Handle cases where landmarks aren't fully detected

        # Display Counter and Stage
        cv2.rectangle(image, (0,0), (225,73), (245,117,16), -1)
        
        # Rep Count
        cv2.putText(image, 'REPS', (15,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, str(count), (10,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)
        
        # Stage Status
        cv2.putText(image, 'STAGE', (65,12), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
        cv2.putText(image, stage, (60,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

        # Draw landmarks and connections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                                )

        cv2.imshow('MediaPipe Pose Estimation', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()