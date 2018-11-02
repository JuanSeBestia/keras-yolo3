#! /usr/bin/env python
import os
import argparse
import json
import cv2
import numpy as np
import xml.etree.ElementTree as ET
import pickle
import csv

max_count = 0
objects_counts = 0
annots_counts = 0


def mod_image(edit_image, minsize, maxsize, autofill=False):
    minx = 0
    miny = 0
    # make square
    if (autofill):
        height, width, _ = edit_image.shape
        maxpixels = width if width >= height else height
        square = np.zeros((maxpixels, maxpixels, 3), np.uint8)
        miny = int((maxpixels-height)/2)
        maxy = int(maxpixels-(maxpixels-height)/2)
        minx = int((maxpixels-width)/2)
        maxx = int(maxpixels-(maxpixels-width)/2)
        square[miny:maxy, minx:maxx] = edit_image
        edit_image = square

    # scale to min
    height, width, _ = edit_image.shape
    minpixels = height if width >= height else width
    scale1 = 1
    if minpixels < minsize:
        scale1 = minsize/minpixels
        edit_image = cv2.resize(edit_image, (0, 0),
                                fx=(scale1), fy=(scale1))

    # scale to max
    height, width, _ = edit_image.shape
    maxpixels = width if width >= height else height
    scale2 = 1
    if maxpixels > maxsize:
        scale2 = maxsize/maxpixels
        edit_image = cv2.resize(edit_image, (0, 0),
                                fx=(scale2), fy=(scale2))

    return [edit_image, minx, miny, scale1*scale2]


def mod_annot(tree, xscale=1, yscale=1, outsetx=0, outsety=0, height=False, width=False):
    global max_count
    global objects_counts
    global annots_counts
    for elem in tree.iter():
        if 'width' in elem.tag and width:
            elem.text = str(width)
        if 'height' in elem.tag and height:
            elem.text = str(height)
        if 'object' in elem.tag or 'part' in elem.tag:
            for attr in list(elem):
                if 'bndbox' in attr.tag:
                    for dim in list(attr):
                        if 'xmin' in dim.tag:
                            dim.text = str(int(outsetx + int(dim.text)))
                            dim.text = str(int(xscale * int(dim.text)))
                        if 'xmax' in dim.tag:
                            dim.text = str(int(outsetx + int(dim.text)))
                            dim.text = str(int(xscale * int(dim.text)))
                        if 'ymin' in dim.tag:
                            dim.text = str(int(outsety + int(dim.text)))
                            dim.text = str(int(yscale * int(dim.text)))
                        if 'ymax' in dim.tag:
                            dim.text = str(int(outsety + int(dim.text)))
                            dim.text = str(int(yscale * int(dim.text)))
    count_objects = len(tree.findall(".//object"))
    count = ET.SubElement(tree.getroot(), 'count')
    count.text = str(count_objects)
    if max_count < count_objects:
        max_count = count_objects
    objects_counts += count_objects
    annots_counts += 1
    return [tree, count_objects]


def _main_(args):
    input_path = args.input
    images_path = args.jpgimages
    minsize = int(args.minsize)
    maxsize = int(args.maxsize)
    autofill = args.autofill
    image_paths = []

    if os.path.isdir(input_path):
        for inp_file in os.listdir(input_path):
            image_paths += [(input_path, inp_file)]
    else:
        image_paths += [input_path]

    image_paths = [(input_path, inp_file) for (input_path, inp_file) in image_paths if (
        inp_file[-4:] in ['.xml', '.XML'])]

    # the main loop
    for (input_path, inp_file) in image_paths:
        try:
            tree = ET.parse(input_path + inp_file)

            image_file = tree.find(".//filename").text
            image_path = images_path + image_file
            image = cv2.imread(image_path)
            original_height, original_width, original__ = image.shape

            edit_image, outsetx, outsety, scale = mod_image(
                image, minsize, maxsize, autofill)

            height, width, _ = edit_image.shape
            xscale = width/original_width
            yscale = height/original_height

            edit_tree, count_objs = mod_annot(tree, scale, scale,
                                  outsetx, outsety, height, width)

            if not os.path.exists(args.output+'JPEGImages/'):
                os.makedirs(args.output+'JPEGImages/')
            if not os.path.exists(args.output+'Annotations/'):
                os.makedirs(args.output+'Annotations/')

            image_path_out = args.output+'JPEGImages/' + image_file
            annot_path_out = args.output+'Annotations/' + inp_file

            edit_tree.write(annot_path_out, encoding='UTF-8')
            cv2.imwrite(image_path_out, edit_image)
            csvFile = open("annots.csv", 'a')
            with csvFile:
                writer = csv.writer(csvFile)
                writer.writerow([image_file,str(count_objs)])

        except Exception as e:
            print(e)
            print('error in: ' + input_path + inp_file)
            continue
    print("{} Annots edited with {} objects, max objects per file {}".format(annots_counts,objects_counts,max_count))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='resize images')
    argparser.add_argument('-i', '--input', default='/home/inkremental-3/gitKraken/dipstick/VOC_dipstick_512/Annotations/',
                           help='path to annotations, a directory of annotations')
    argparser.add_argument('-j', '--jpgimages', default='/home/inkremental-3/gitKraken/dipstick/VOC_dipstick_512/JPEGImages/',
                           help='a directory of images')
    argparser.add_argument(
        '-o', '--output', default='output/', help='path to output directory')
    argparser.add_argument(
        '-a', '--autofill', default='true', help='generate square imgs')
    argparser.add_argument(
        '-m', '--maxsize', default='512', help='resize to 512')
    argparser.add_argument(
        '-n', '--minsize', default='512', help='min size allow')

    args = argparser.parse_args()
    _main_(args)
