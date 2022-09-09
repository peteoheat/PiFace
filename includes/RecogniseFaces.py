from threading import Thread
import face_recognition
import numpy
import pickle
import cv2

class RecogniseFaces:
    """Class that receives a frame and tries to recognise faces in it"""

    def __init__(self, frame=None):
        self.frame = frame
        self.stopped = False
        # Load the known faces and embeddings
        self.encodings_file = "encodings.pickle"
        self.knownfacedata = pickle.loads(open(self.encodings_file, "rb").read())

    def start(self):
        Thread(target=self.recognise, args=()).start()
        return self

    def recognise(self):
        # Scale the frame down to 50% size for performance
        self.small_frame = cv2.resize(self.frame, (0, 0), fx=0.5, fy=0.5)
        self.boxes = face_recognition.face_locations(self.small_frame)
        self.encodings = face_recognition.face_encodings(self.small_frame, self.boxes)
        self.names = []
        self.matches = []
        self.name = "Unknown"
        # loop over the facial embeddings
        for encoding in self.encodings:
            # attempt to match each face in the input image to our known
            # encodings
            self.matches = face_recognition.compare_faces(self.knownfacedata["encodings"], encoding)
            self.name = "Unknown"  # if face is not recognized, then print Unknown

        # check to see if we have found a match
        if True in self.matches:
            # find the indexes of all matched faces then initialize a
            # dictionary to count the total number of times each face
            # was matched
            self.matchedIdxs = [i for (i, b) in enumerate(self.matches) if b]
            self.counts = {}

            # loop over the matched indexes and maintain a count for
            # each recognized face face
            for i in self.matchedIdxs:
                self.name = self.knownfacedata["names"][i]
                self.counts[self.name] = self.counts.get(self.name, 0) + 1

            # determine the recognized face with the largest number
            # of votes (note: in the event of an unlikely tie Python
            # will select first entry in the dictionary)
            self.name = max(self.counts, key=self.counts.get)
        # update the list of names
        self.names.append(self.name)
        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(self.boxes, self.names):
            # Scale the numbers back up for drawing the box on fullsize image
            top *= 2
            right *= 2
            bottom *= 2
            left *= 2
            # draw the predicted face name on the image - color is in BGR
            cv2.rectangle(self.frame, (left, top), (right, bottom),
                          (0, 255, 225), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(self.frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        .8, (0, 255, 255), 2)
        return self.frame

    def stop(self):
        self.stopped = True
