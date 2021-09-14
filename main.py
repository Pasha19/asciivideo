import os
import pathlib
import time

import cv2


def img_to_ascii(image, width):
    orig_width = image.shape[1]
    orig_height = image.shape[0]
    ratio = orig_height / orig_width / 1.65  # magic number 1.65
    height = int(width * ratio)
    resized = cv2.resize(image, (width, height))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    del resized

    width = gray.shape[1]
    height = gray.shape[0]
    ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

    data = ""
    for i in range(height):
        row = ""
        for j in range(width):
            row += ASCII_CHARS[gray[i, j] // 25]
        data += row + "\n"
    return data


def extract_frames(video):
    while True:
        success, image = video.read()
        if not success:
            break
        yield image


def main():
    wd = pathlib.Path().resolve()
    image_path = pathlib.Path(wd).parent.parent.resolve()

    video_file = "{0}\\{1}".format(image_path, "Me-at-the-zoo-YouTube.mp4")
    print(video_file)
    video = cv2.VideoCapture(video_file)
    for img in extract_frames(video):
        os.system("cls")
        print(img_to_ascii(img, 100))
        time.sleep(0.02)
    print("end")


main()
