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


def encode_single_frame(frame):
    width = frame.find('\n')
    height = len(frame) // (width + 1)

    encoded_frame = ""
    c = 0
    for i in range(height):
        prev = frame[c]
        c += 1
        row = ""
        seq = 1
        for j in range(1, width + 1):
            s = frame[c]
            c += 1
            if s == prev:
                seq += 1
            else:
                row += prev
                if seq == 2:
                    row += prev
                elif seq > 2:
                    row += str(seq)
                seq = 1
                prev = s
        encoded_frame += row + "\n"
    return encoded_frame


def encode_frame_diff(frame1, frame2):
    result = ""
    for i in range(len(frame1)):
        if frame1[i] != "\n" and frame1[i] == frame2[i]:
            result += "="
        else:
            result += frame2[i]
    return result


def read_by_frames(file):
    while True:
        read = file.read(7)
        if not read:
            break
        size_to_read = int(read.strip().lstrip("0"))  # 6 + LF
        frame_data = file.read(size_to_read)
        yield frame_data


def restore_frame(frame):
    result = ""
    digits = list(map(str, range(0, 10)))
    cnt = 0
    p = frame[0]
    for i in range(1, len(frame)):
        c = frame[i]
        if c in digits:
            cnt = cnt * 10 + int(c)
        else:
            result += p if cnt == 0 else cnt * p
            p = c
            cnt = 0
    return result


def restore_frame_diff(frame1, frame2):
    result = ""
    for i in range(len(frame2)):
        c = frame2[i]
        result += frame1[i] if c == "=" else c
    return result


def main():
    wd = pathlib.Path().resolve()
    image_path = pathlib.Path(wd).parent.parent.resolve()
    #
    # video_file = "{0}\\{1}".format(image_path, "Me-at-the-zoo-YouTube.mp4")
    # video = cv2.VideoCapture(video_file)
    #
    # output = open("{0}\\{1}".format(image_path, "result_diff.txt"), "w")
    # prev_frame = None
    # width = 100
    # for img in extract_frames(video):
    #     frame = img_to_ascii(img, width)
    #     if prev_frame is None:
    #         encoded = encode_single_frame(frame)
    #     else:
    #         encoded = encode_single_frame(encode_frame_diff(prev_frame, frame))
    #     output.write("{:06d}\n".format(len(encoded)))
    #     output.write(encoded)
    #     prev_frame = frame
    # output.close()
    # video.release()

    text_path = "{0}\\{1}".format(image_path, "result_diff.txt")
    frame0 = ""
    with open(text_path) as f:
        for frame in read_by_frames(f):
            os.system('cls')
            frame = restore_frame(frame)
            frame = restore_frame_diff(frame0, frame)
            print(frame)
            frame0 = frame
            time.sleep(0.04)


main()
