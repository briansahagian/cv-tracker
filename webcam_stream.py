import cv2 as cv

def main():
    cap = cv.VideoCapture(0);
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

        cv.imshow('webcam stream', frame)
        
        k = cv.waitKey(1)

        if k == ord('q'):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()