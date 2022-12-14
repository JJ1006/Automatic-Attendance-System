# Import libraries.
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from datetime import date

# Set a few important variables.
TodayDate = date.today()
path = 'Training_images'
images = []
classNames = []
myList = os.listdir(path)
PresentStudentsForNow = []

# To be implemented.
def AddNewStudent():
    print("[!] Please ensure a clear picture of the face of a student. Press the SPACE key to capture the face.")
    NewStudentName = input("[+] Enter the name of the student: ").replace(" ", "_")
    cam = cv2.VideoCapture(0)
    while True:
        ret, frame = cam.read()
        cv2.imshow("AddNewStudent", frame)
        k = cv2.waitKey(1)
        if k%256 == 32:
            cv2.imwrite(f"{path}/{NewStudentName}.jpg", frame)
            cv2.destroyAllWindows()
            break
    print(f"[+] Student {NewStudentName} is added!")
    if(input("[?] Do you want to add a new student? [y/n]: ") == 'y'):
        AddNewStudent()

# To be implemented.
def GenerateReportOnEnd():
    print(f"[!] These student's attendance was recorded on {TodayDate}: ")
    for i in range(len(PresentStudentsForNow)):
        print(f'{i+1}) {PresentStudentsForNow[i]}')

# Welcome and configuration.
print("*** Welcome to our IOT project - Automatic Attendance System. ***")
if(input("[?] Do you want to add a new student? [y/n]: ") == 'y'):
    AddNewStudent()
print("[!] Loading the attendance system...")

# Get the student images.
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])

# Enroll faces.
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# Marking attendance in the csv database.
def markAttendance(name):
    PresentStudentsForNow.append(name)
    with open('Attendence.csv', 'r+') as f:
        myDataList = f.readlines()
        now = datetime.now()
        dtString = now.strftime('%H:%M:%S')
        f.writelines(f'\n{name},{dtString}')


encodeListKnown = findEncodings(images)

print("[!] Starting the attendance system. Press the ESC key to exit.")

# Open the camera stream.
cap = cv2.VideoCapture(0)

# looped face recognition engine.
while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
            if name not in PresentStudentsForNow:  # Every student should be marked only once per execution of this program.
                markAttendance(name)

    cv2.imshow('Attendance', img)   # Keep showing the webcam feed.
    k = cv2.waitKey(1)
    if k%256 == 27:
        print("Escape hit, closing...")
        break

GenerateReportOnEnd()