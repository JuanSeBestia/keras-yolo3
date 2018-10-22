#!/bin/bash  
# Prepare dataset
mkdir -p dataset/train/Annotations -p dataset/train/JPEGImages -p dataset/valid/Annotations -p dataset/valid/JPEGImages
# Copy train
ArrayName=$(cat dipstick/VOC_dipstick_512/ImageSets/Main/train.txt)
for var in $ArrayName
do
cp "dipstick/VOC_dipstick_512/JPEGImages/${var}.jpg" dataset/train/JPEGImages/
cp "dipstick/VOC_dipstick_512/Annotations/${var}.xml" dataset/train/Annotations/
done
# Copy valid
ArrayName=$(cat dipstick/VOC_dipstick_512/ImageSets/Main/valid.txt)
for var in $ArrayName
do
cp "dipstick/VOC_dipstick_512/JPEGImages/${var}.jpg" dataset/valid/JPEGImages/
cp "dipstick/VOC_dipstick_512/Annotations/${var}.xml" dataset/valid/Annotations/
done