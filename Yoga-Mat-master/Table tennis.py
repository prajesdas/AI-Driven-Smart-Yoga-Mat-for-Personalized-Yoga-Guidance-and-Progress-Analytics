import cv2
import mediapipe as mp
import numpy as np
import time
from collections import deque

# Initialize MediaPipe Hands (not used now but kept for future)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Background subtractor for motion detection
back_sub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=50, detectShadows=False)

# Parameters
min_ball_area = 50
max_ball_area = 1500
toss_height_threshold_cm = 16
pixel_to_cm = 0.5

# Variables for tracking
ball_positions = deque(maxlen=10)
toss_start_time = None
toss_max_height = None
status_message = "Waiting for serve..."
show_debug = True

# Toss detection states
STATE_WAITING = 0
STATE_TOSS_UP = 1
STATE_TOSS_DOWN = 2

toss_state = STATE_WAITING
toss_height_cm = None
last_toss_height_cm = None
last_toss_status = None

# Variables for ball detection consistency
last_ball_center = None
last_ball_radius = None
max_radius_change = 10
max_position_change = 50


def detect_ball(frame, fg_mask):
    global last_ball_center, last_ball_radius

    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ball_center = None
    ball_radius = 0

    valid_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_ball_area or area > max_ball_area:
            continue

        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue

        circularity = 4 * np.pi * (area / (perimeter * perimeter))
        if circularity < 0.7:
            continue

        valid_contours.append(cnt)

    if not valid_contours:
        last_ball_center = None
        last_ball_radius = None
        return None

    c = max(valid_contours, key=cv2.contourArea)
    ((x, y), radius) = cv2.minEnclosingCircle(c)

    if last_ball_radius is not None:
        if abs(radius - last_ball_radius) > max_radius_change:
            return None

    if last_ball_center is not None:
        dist = np.linalg.norm(np.array([x, y]) - np.array(last_ball_center))
        if dist > max_position_change:
            return None

    ball_center = (int(x), int(y))
    ball_radius = int(radius)

    last_ball_center = ball_center
    last_ball_radius = ball_radius

    cv2.circle(frame, ball_center, ball_radius, (0, 255, 0), 2)

    return ball_center


def draw_status_panel(frame, status, toss_height_cm, last_toss_height_cm, last_toss_status, ball_center, end_line_x, end_line_y):
    overlay = frame.copy()
    panel_width = 300
    panel_color = (50, 50, 50)
    alpha = 0.7
    cv2.rectangle(overlay, (frame.shape[1]-panel_width, 0), (frame.shape[1], frame.shape[0]), panel_color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    x_start = frame.shape[1] - panel_width + 20
    y_start = 40
    line_height = 30

    cv2.putText(frame, "Serve Fault Detection", (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    y_start += line_height * 2

    cv2.putText(frame, f"Status:", (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    y_start += line_height
    cv2.putText(frame, status, (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    y_start += line_height * 2

    cv2.putText(frame, f"Toss Height (cm):", (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    y_start += line_height
    toss_text = f"{toss_height_cm:.1f}" if toss_height_cm is not None else "N/A"
    color = (0, 255, 0) if toss_height_cm and toss_height_cm >= toss_height_threshold_cm else (0, 0, 255)
    cv2.putText(frame, toss_text, (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    y_start += line_height * 2

    cv2.putText(frame, f"Last Toss Height (cm):", (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    y_start += line_height
    last_text = f"{last_toss_height_cm:.1f}" if last_toss_height_cm is not None else "N/A"
    cv2.putText(frame, last_text, (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    y_start += line_height * 2

    cv2.putText(frame, f"Last Toss Status:", (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
    y_start += line_height
    if last_toss_status is None:
        cv2.putText(frame, "N/A", (x_start, y_start),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 180, 180), 2)
    else:
        color = (0, 255, 0) if last_toss_status == "Valid" else (0, 0, 255)
        cv2.putText(frame, last_toss_status, (x_start, y_start),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    y_start += line_height * 2

    cv2.putText(frame, "Controls:", (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
    y_start += line_height
    cv2.putText(frame, "D - Toggle Debug Info", (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
    y_start += line_height
    cv2.putText(frame, "R - Reset", (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)
    y_start += line_height
    cv2.putText(frame, "ESC - Quit", (x_start, y_start),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 1)

    # Vertical End Line (moved to 70% width)
    cv2.line(frame, (end_line_x, 0), (end_line_x, frame.shape[0]), (0, 0, 255), 2)
    cv2.putText(frame, "End Line", (end_line_x + 5, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Horizontal marker line (20% from bottom = 80% of height)
    cv2.line(frame, (0, end_line_y), (frame.shape[1], end_line_y), (255, 0, 0), 2)
    cv2.putText(frame, "Min Contact Height", (10, end_line_y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Ball position checks
    if ball_center:
        ball_x, ball_y = ball_center

        pos_text = "Behind End Line" if ball_x < end_line_x else "Past End Line"
        color = (0, 255, 0) if ball_x < end_line_x else (0, 0, 255)
        cv2.putText(frame, pos_text, (frame.shape[1] - 280, 150),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if ball_y > end_line_y:
            cv2.putText(frame, "Fault: Below Contact Line", (frame.shape[1] - 280, 180),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)


def main():
    global toss_start_time, toss_max_height, status_message, show_debug
    global toss_state, toss_height_cm, last_toss_height_cm, last_toss_status
    global last_ball_center, last_ball_radius

    cap = cv2.VideoCapture(0)

    toss_state = STATE_WAITING
    toss_height_cm = None
    last_toss_height_cm = None
    last_toss_status = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_width = frame.shape[1]
        frame_height = frame.shape[0]

        # New line positions
        end_line_x = int(0.70 * frame_width)   # vertical
        end_line_y = int(0.80 * frame_height)  # horizontal (20% from bottom)

        fg_mask = back_sub.apply(frame)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8))

        ball_center = detect_ball(frame, fg_mask)

        if ball_center:
            ball_positions.append(ball_center)

            if len(ball_positions) >= 5:
                y_positions = [pos[1] for pos in ball_positions]
                velocity = y_positions[-1] - y_positions[0]

                if toss_state == STATE_WAITING:
                    if velocity < -3:
                        toss_state = STATE_TOSS_UP
                        toss_start_time = time.time()
                        toss_max_height = ball_center[1]
                        status_message = "Toss started"
                elif toss_state == STATE_TOSS_UP:
                    if ball_center[1] < toss_max_height:
                        toss_max_height = ball_center[1]
                    if velocity > 3:
                        toss_state = STATE_TOSS_DOWN
                elif toss_state == STATE_TOSS_DOWN:
                    toss_duration = time.time() - toss_start_time
                    toss_height_pixels = abs(ball_positions[0][1] - toss_max_height)
                    toss_height_cm = toss_height_pixels * pixel_to_cm
                    last_toss_height_cm = toss_height_cm

                    if toss_height_cm < toss_height_threshold_cm:
                        status_message = "Fault: Toss height < 16cm"
                        last_toss_status = "Fault"
                    elif ball_center[1] > end_line_y:
                        status_message = "Fault: Below contact line"
                        last_toss_status = "Fault"
                    else:
                        status_message = "Toss height OK"
                        last_toss_status = "Valid"

                    if toss_duration > 3 or len(ball_positions) < 3:
                        toss_state = STATE_WAITING
                        toss_start_time = None
                        toss_max_height = None
                        ball_positions.clear()
        else:
            if toss_state != STATE_WAITING:
                if toss_start_time and (time.time() - toss_start_time) > 2:
                    toss_state = STATE_WAITING
                    toss_start_time = None
                    toss_max_height = None
                    ball_positions.clear()
                    toss_height_cm = None
                    status_message = "Waiting for serve..."

        draw_status_panel(frame, status_message, toss_height_cm, last_toss_height_cm,
                          last_toss_status, ball_center, end_line_x, end_line_y)

        if show_debug:
            fg_small = cv2.resize(fg_mask, (160, 120))
            cv2.imshow("Motion Mask (Debug)", fg_small)

        cv2.imshow("Table Tennis Serve Fault Detection", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break
        elif key == ord('d'):
            show_debug = not show_debug
        elif key == ord('r'):
            ball_positions.clear()
            toss_start_time = None
            toss_max_height = None
            status_message = "Reset done"
            toss_height_cm = None
            toss_state = STATE_WAITING
            last_ball_center = None
            last_ball_radius = None
            last_toss_height_cm = None
            last_toss_status = None

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    ball_positions = deque(maxlen=10)
    main()
