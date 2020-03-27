import numpy as np
from PIL import Image

from random import randint, choice

# im = Image.open('./data/bank-2.png')

# a = np.asarray(im)

# print(a.shape)

colors = [
    [222, 193, 158],
    [206, 181, 146],
    [195, 174, 137],
    [185, 168, 131],
    [199, 179, 139],
    [212, 193, 135],
    [212, 208, 159],
    [185, 170, 123],
    [211, 196, 139],
    [212, 196, 148],
    [181, 172, 143],
    [196, 182, 146],
    [234, 229, 196],
    [223, 217, 184],
    [214, 198, 153],
    [219, 198, 146],
    [206, 184, 136],
    [218, 204, 160],
    [206, 184, 136],
    [216, 196, 153],
]

array = np.zeros((360, 640, 4), dtype=np.uint8)
array[:, :, 0:3] = 5

print(array.shape)
print(array)

array[:, :, 3] = 255

step = 2
for row in range(0, 720, step):
    curr_col = 0

    while curr_col < 1280:
        width = randint(4, 8)

        color = choice(colors) + [255]

        array[row: row + step, curr_col: curr_col + width, :] = color

        curr_col += width

print(array.shape)
print(array)

im = Image.fromarray(array)

im.save('./data/background.png')
