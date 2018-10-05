#! /usr/bin/env python
import os
import argparse
import json
import cv2


def _main_(args):
    input_path = args.input
    minsize = int(args.minsize)
    maxsize = int(args.maxsize)
    image_paths = []

    if os.path.isdir(input_path):
        for inp_file in os.listdir(input_path):
            image_paths += [(input_path, inp_file)]
    else:
        image_paths += [input_path]

    image_paths = [(input_path, inp_file) for (input_path, inp_file) in image_paths if (
        inp_file[-4:] in ['.jpg', '.png', 'JPEG'])]

    # the main loop
    for (input_path, inp_file) in image_paths:
        image_path = input_path + inp_file
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        edit_image = image

        # scale to min
        minpixels = height if width >= height else width
        if minpixels < minsize:
            edit_image = cv2.resize(edit_image, (0, 0), fx=(
                minsize/minpixels), fy=(minsize/minpixels))
            height, width = edit_image.shape[:2]
        # scale to max
        maxpixels = width if width >= height else height
        if maxpixels > maxsize:
            edit_image = cv2.resize(edit_image, (0, 0), fx=(
                maxsize/maxpixels), fy=(maxsize/maxpixels))
        cv2.imwrite(args.output+inp_file,edit_image)


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='resize images')
    argparser.add_argument('-i', '--input', default='examples/dipstick/images/',
                           help='path to an image, a directory of images')
    argparser.add_argument(
        '-o', '--output', default='output/', help='path to output directory')
    argparser.add_argument(
        '-a', '--autofill', default='false', help='generate square imgs')
    argparser.add_argument(
        '-m', '--maxsize', default='1024', help='resize to 512')
    argparser.add_argument(
        '-n', '--minsize', default='512', help='min size allow')

    args = argparser.parse_args()
    _main_(args)
