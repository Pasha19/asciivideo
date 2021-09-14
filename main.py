import pathlib

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


def main():
    wd = pathlib.Path().resolve()
    image_path = pathlib.Path(wd).parent.parent.resolve()
    image_file = "{0}\\{1}".format(image_path, "fr.jpg")
    image = cv2.imread(image_file)

    data = img_to_ascii(image, 200)
    print(data)


main()
