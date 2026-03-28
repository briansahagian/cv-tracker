import cv2
from ultralytics import YOLO


def main():

    model = YOLO("yolo26n.pt") #load the 26 nano model
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera could not open")
        exit()

    print("Camera opened successfully. Press 'q' to quit.")
    
    while True: # loop indefinitely
        # cap is a VideoCapture object
        # Returns true if frame is read correctly, otherwise false
        # false means the end of the video
        success, frame = cap.read()

        if not success: # if frame cannot be read
            print("Can't receive frame (stream end?). Exiting ...")
            break

        results = model(frame, classes=0, stream=True)
        # classes=0 only looks for persons, stream=True is efficient for memoru
        
        for r in results: #r is object representing frame, containing a information on each
            boxes = r.boxes
            for box in boxes:
                # coordinates in form top left, bottom right
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                conf = round(float(box.conf[0]), 2) #round confidence to 2 dec

                cv2.rectangle(frame, (x1, y2), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Person {conf}", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                body_center_x = int(x1 + (x2-x1)/2)
                body_center_y = int(y1 + (y2-y1)/2)
                cv2.circle(frame, (body_center_x, body_center_y), 3, (255, 255, 0), -1) # centerpoint of the person

        cv2.imshow('YOLO26 Nano detection', frame)
        
        k = cv2.waitKey(1)

        if k & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()