import face_recognition
import cv2
import face_recognition
import numpy as np
from imageDb import search


def video_preprocessing():
    video_capture = cv2.VideoCapture(0)

    # initializing the variables
    # face_locations = []
    # face_encodings = []
    # face_names = []
    process_this_frame = True

    while (True):
        # grabbing a frame
        ret, frame = video_capture.read()
        # resizing the frame
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        if process_this_frame:
            # call the face_recognition_method
            best_match = face_recognition_method(rgb_small_frame)

        process_this_frame = not process_this_frame

        print(str(best_match))

        # if(len(best_match['face_locations']) != 0 and len(best_match['face_names']) != 0):
        #     face_identify(
        #         rgb_small_frame, best_match['face_locations'], best_match['face_names'])
        # else:
        #     print("no face detected")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()


def face_recognition_method(frame):
    face_locations = []
    face_encodings = []
    face_names = []

    face_locations = face_recognition.face_locations(frame)
    print(len(face_locations))
    if(len(face_locations) != 0):
        face_encodings = face_recognition.face_encodings(
            frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            # use the known face with the smallest distance to the new face
            face_distance = np.linalg.norm(face_encoding)
            best_match = search_best_fit(face_distance)
            face_names.append(best_match)

    #     d = {'face_locations': face_locations, 'face_names': face_names}
    #     return d
    # else:
    #     return {'face_locations': face_locations, 'face_names': face_names}

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, int(left, bottom - 35),
                          int(right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, int(left + 6, bottom - 6),
                        font, 1.0, (255, 255, 255), 1)

        # Display the resulting image
        cv2.imshow('Video', frame)


# def face_identify(frame, face_locations, face_names):
    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35),
                      (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6),
                    font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)


def search_best_fit(ref_distance):
    best_fit = search(ref_distance)
    return best_fit


def main():
    video_preprocessing()


if __name__ == "__main__":
    main()
