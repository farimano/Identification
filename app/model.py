# Import all required libraries
import os
from os.path import dirname, abspath

import sys
import dlib

# Define path to learned models of box-prediction and recognition
parent = dirname(dirname(abspath(__file__)))
predictor_path = os.path.join(parent, "preinstalled_models/shape_predictor_5_face_landmarks.dat")
face_rec_model_path = os.path.join(parent, "preinstalled_models/dlib_face_recognition_resnet_model_v1.dat")

# Define filenames of original and checked images
orig = sys.argv[1]
check = sys.argv[2]

# Define all required models
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

# Make path for images
path_to_orig = os.path.join(parent, "db", "faces", "orig", f"{orig}.jpg")
path_to_check = os.path.join(parent, "db", "faces", "check", f"{check}.jpg")

# Preprocessing of original image
# Preprocessing of images contains three steps:
# 1. Detect face
# 2. Bound shape for detected face
# 3. Using detected region and prelearned model, calclulate its features representation
orig_img = dlib.load_rgb_image(path_to_orig)
orig_det = detector(orig_img, 1)
orig_shp = sp(orig_img, orig_det[0])
orig_descriptor = facerec.compute_face_descriptor(orig_img, orig_shp)

# Preprocessing of original image
check_img = dlib.load_rgb_image(path_to_check)
check_det = detector(check_img, 1)
if len(check_det)>1:
	print("Fail. Too many people!")
	exit()
check_shp = sp(check_img, check_det[0])
check_descriptor = facerec.compute_face_descriptor(check_img, check_shp)

# Calculate euclidean distance between representations of images and try to recognize face, such way gets 99.13% accuracy
distance = sum([(check_descriptor[i]-orig_descriptor[i])**2 for i in range(128)])**0.5
if distance < 0.6:
	print("Succeed! It is the same person!")
else:
	print("Fail. This person is not id-owner!")
