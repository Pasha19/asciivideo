import time
import sys

import cv2


ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']


def ascii_char_to_int():
    chars_map = {'=' : 0}
    for i in range(len(ASCII_CHARS)):
        chars_map[ASCII_CHARS[i]] = i + 1
    return chars_map


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

    data = ""
    d = 255 // len(ASCII_CHARS) + 1 if 255 % len(ASCII_CHARS) != 0 else 0
    for i in range(height):
        row = ""
        for j in range(width):
            row += ASCII_CHARS[gray[i, j] // d]
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

    ascii_map = ascii_char_to_int()
    c = 0
    row = b""
    for i in range(height):
        prev = frame[c]
        c += 1
        seq = 1
        for j in range(1, width + 1):
            s = frame[c]
            c += 1
            if s == prev:
                seq += 1
            else:
                symbol = ascii_map[prev]
                if seq < 16:
                    symbol |= (seq << 4)
                row += symbol.to_bytes(1, 'big')
                if seq >= 16:
                    row += seq.to_bytes(1, 'big')
                seq = 1
                prev = s
    return row


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
        read = int.from_bytes(file.read(2), "big")
        if not read:
            break
        frame_data = file.read(read)
        yield frame_data


def restore_frame(frame, width):
    result = ""
    size = len(frame)
    i = 0
    read = 0
    symbols = ['='] + ASCII_CHARS
    while i < size:
        sym = symbols[frame[i] & 0xf]
        seq = frame[i] >> 4
        if seq == 0:
            i += 1
            seq = frame[i]
        result += sym * seq
        read += seq
        if read % width == 0:
            result += '\n'
        i += 1
    return result


def restore_frame_diff(frame1, frame2):
    result = ""
    for i in range(len(frame2)):
        c = frame2[i]
        result += frame1[i] if c == "=" else c
    return result


def encode(video_input, output, width):
    video = cv2.VideoCapture(video_input)
    ascii = open(output, "wb")
    ascii.write(width.to_bytes(2, "big"))
    prev_frame = None
    for img in extract_frames(video):
        frame = img_to_ascii(img, width)
        if prev_frame is None:
            encoded = encode_single_frame(frame)
        else:
            encoded = encode_single_frame(encode_frame_diff(prev_frame, frame))
        ascii.write(len(encoded).to_bytes(2, "big"))
        ascii.write(encoded)
        prev_frame = frame
    ascii.close()
    video.release()


def play(ascii_input):
    frame0 = ""
    with open(ascii_input, "rb") as f:
        width = int.from_bytes(f.read(2), "big")
        for frame in read_by_frames(f):
            print("\n"*100)
            frame = restore_frame(frame, width)
            frame = restore_frame_diff(frame0, frame)
            print(frame)
            frame0 = frame
            time.sleep(0.04)


def main():
    args = sys.argv[1:]
    if args[0] == "encode":
        encode(args[1], args[2], int(args[3]))
    elif args[0] == "play":
        play(args[1])


if __name__ == '__main__':
    main()
