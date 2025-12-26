import cv2
import mediapipe as md

md_drawing = md.solutions.drawing_utils
md_drawing_styles = md.solutions.drawing_styles
md_pose = md.solutions.pose

count = 0
position = None
cap = cv2.VideoCapture(0)

with md_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as pose:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("empty camera")
            break

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        result = pose.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        imlist = []

        if result.pose_landmarks:
            md_drawing.draw_landmarks(
                image, result.pose_landmarks, md_pose.POSE_CONNECTIONS)
            for id, im in enumerate(result.pose_landmarks.landmark):
                h, w, _ = image.shape
                X, Y = int(im.x * w), int(im.y * h)
                imlist.append([id, X, Y])

        if len(imlist) != 0:
            # Squat detection logic (using hip and knee landmarks)
            left_hip_y = imlist[23][2]  # Landmark 23: Left hip
            left_knee_y = imlist[25][2] # Landmark 25: Left knee
            right_hip_y = imlist[24][2] # Landmark 24: Right hip
            right_knee_y = imlist[26][2] # Landmark 26: Right knee

            if left_knee_y > left_hip_y + 50 and right_knee_y > right_hip_y + 50: #Adjust the 50 to fit your need.
                position = "down"
            if left_knee_y < left_hip_y + 10 and right_knee_y < right_hip_y + 10 and position == "down": #Adjust the 10 to fit your need.
                position = "up"
                count += 1
                print(count)

        cv2.imshow("Squat counter", cv2.flip(image, 1)) #changed window name.
        key = cv2.waitKey(1)
        if key == ord('q') or count >= 10:
            break

cap.release()