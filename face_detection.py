import cv2


def main():

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

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

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, 
            minNeighbors=5, minSize=(30,30))
        
        for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        cv2.imshow('face detection', frame)
        
        k = cv2.waitKey(1)

        if k == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()