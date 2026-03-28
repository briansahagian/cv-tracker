import cv2
import imutils


def main():

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    cap = cv2.VideoCapture(0);

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

        # frame = imutils.resize(frame, width=400) # Resize for faster processing
        
        (rects, weights) = hog.detectMultiScale(frame, winStride=(4,4), padding=(8,8), scale=1.05)

        for (x, y, w, h) in rects:
            cv2.rectangle(frame, (x,y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow('Body detection', frame)
        
        k = cv2.waitKey(1)

        if k == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()