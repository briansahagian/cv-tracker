# Main loop, runs camera and calls other functions, passing to Arduino
# Runs person detection
# Calculates x & y error
# Passes those errors to PID functions
# PID functions return motor inputs
# Main script sends to those inputs to servo motors
# Includes angle limits for the motors

import cv2
from ultralytics import YOLO

from controller import PIDController
from servo_command import send_to_arduino

def clamp_angle(angle, min_angle = 0, max_angle = 270):
    # Ensures we never go out of angle range for servo
    return max(min_angle, min(angle, max_angle))

def main():

    model = YOLO("yolo26n.pt") #load the 26 nano model
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera could not open")
        exit()

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    center_x = frame_width // 2
    center_y = frame_height // 2
    print("Camera opened successfully.")

    pan_pid = PIDController(kp=0.01, ki=0.0, kd=0.0, deadband=25, integral_limit=50)
    tilt_pid = PIDController(kp=0.008, ki=0.0, kd=0.0, deadband=10, integral_limit=50)

    current_pan_angle = 90.0
    current_tilt_angle = 55.0

    print("System armed, 'q' to quit.")

     # --- FULLSCREEN SETUP ---
    # cv2.namedWindow('Gimbal Tracker', cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty('Gimbal Tracker', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    

    while True: # loop indefinitely
        # cap is a VideoCapture object
        # Returns true if frame is read correctly, otherwise false
        # false means the end of the video
        success, frame = cap.read()

        if not success: # if frame cannot be read
            print("Can't receive frame (stream end?). Exiting ...")
            break

        results = model(frame, classes=0, stream=True, verbose=False)
        # classes=0 only looks for persons, stream=True is efficient for memory
        
        person_detected = False

        for r in results: #r is object representing frame, containing a information on each
            boxes = r.boxes
            if len(boxes) > 0:
                person_detected = True
                box = boxes[0]
                 # coordinates in form top left, bottom right
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = round(float(box.conf[0]), 2) #round confidence to 2 dec

                body_center_x = int(x1 + (x2-x1)/2)
                body_center_y = int(y1 + (y2-y1)/2)

                pan_effort = pan_pid.calculate(setpoint=center_x, current_value=body_center_x)
                tilt_effort = tilt_pid.calculate(setpoint=center_y, current_value=body_center_y)

                # may need to subtract effort depending on servo direction
                current_pan_angle += pan_effort
                current_tilt_angle += tilt_effort

                current_pan_angle = clamp_angle(current_pan_angle)
                current_tilt_angle = clamp_angle(current_tilt_angle)

                send_to_arduino(current_pan_angle, current_tilt_angle)

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Person {conf}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                cv2.circle(frame, (body_center_x, body_center_y), 3, (255, 255, 0), -1) # centerpoint of the person

                cv2.line(frame, (center_x, center_y), (body_center_x, body_center_y), (0, 0, 255), 2)

        if not person_detected:
            pan_pid.reset()
            tilt_pid.reset()

        cv2.drawMarker(frame, (center_x, center_y), (255, 0, 0), cv2.MARKER_CROSS, 20, 2)

        cv2.imshow('YOLO26 Nano detection', frame)
        
        k = cv2.waitKey(1)

        if k & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()