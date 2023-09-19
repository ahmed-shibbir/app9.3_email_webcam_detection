import cv2
import time
from emailing import send_email
import glob
import os

from threading import Thread

# pip install opencv-python

video = cv2.VideoCapture(0)
# check, frame = video.read()
time.sleep(1)

# print(check)
# print(frame)
# print(frame.shape)

first_frame = None
status_list = []
count = 1


def clean_folder():
    print("Cleaning started")
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)
    print("Cleaning ended")


while True:
    status = 0
    check, frame = video.read()
    # time.sleep(1)

    # cv2.imwrite(f"images/{count}.png", frame)
    # count = count + 1

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    if first_frame is None:
        first_frame = gray_frame_gau
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]

    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
    print(thresh_frame)

    # cv2.imshow("My video", thresh_frame)
    # break
    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        print('contour', contour)

        if cv2.contourArea(contour) < 5000:  # can be 10000, 15000, 2000
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 5)
        if rectangle.any():
            status = 1
            cv2.imwrite(f"images/{count}.png", frame)
            count = count + 1

            all_images = glob.glob("images/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

            # send_email()
    status_list.append(status)
    # print(status_list)
    status_list = status_list[-2:]
    print(status_list)

    if status_list[0] == 1 and status_list[1] == 0:

        # send_email(image_with_object)
        email_thread = Thread(target=send_email, args=(image_with_object,))
        email_thread.daemon = True

        # clean_folder()
        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True

        email_thread.start()
        # clean_thread.start()


    cv2.imshow("Video", frame)

    key = cv2.waitKey(1)
    if key == ord("q"):
        break
video.release()

clean_thread.start()
time.sleep(1)
