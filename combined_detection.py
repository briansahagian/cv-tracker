import cv2


def main():

    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
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

        bodies, body_weights = hog.detectMultiScale(frame, winStride=(6,6), padding=(32, 32), scale=1.2)

        faces, _, face_weights = face_cascade.detectMultiScale3(gray, 1.3, 5, minSize=(30,30),outputRejectLevels=True)

        for i, (bx, by, bw, bh) in enumerate(bodies):
            # for every body, set to not confirmed
            is_confirmed = False
            body_confidence = body_weights[i]

            # lower limit of the upper 30% of the body
            head_lower_limit = by + (0.30 * bh)

            for j, (fx, fy, fw, fh) in enumerate(faces):
                # for every detected face, look for center of face coords
                face_center_x = fx + (fw // 2)
                face_center_y = fy + (fh // 2)

                # check if the center of the face is in the top 30% of body
                # if it is, confirm the person, change display color
                if (by < face_center_y < head_lower_limit) and (bx < face_center_x < bx + bw):
                    is_confirmed = True
                    total_score = body_confidence + (face_weights[j] / 10.0)
                    break
                
            # If confirmed, green, else red
            if is_confirmed: color = (0, 255, 0) 
            else: color = (255, 0, 0)
            label = "Person (Confirmed)" if is_confirmed else "Body?"

            cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), color, 2)
            cv2.putText(frame, label, (bx, by - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        cv2.imshow('Combined Detection', frame)
        k = cv2.waitKey(1)

        if k == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()