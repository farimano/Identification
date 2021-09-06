# Import all required libraries
import os
from os.path import dirname, abspath
import dlib

def face_recog(orig_path, check_path):
	error = None
	distance = None
	number_of_people = None
	
	# Define path to learned models of box-prediction and recognition
	current_directory = dirname(abspath(__file__))
	db_directory = os.path.join(current_directory, "db")
	predictor_path = os.path.join(db_directory, "preinstalled_models", "shape.dat")
	face_rec_model_path = os.path.join(db_directory, "preinstalled_models", "recognition.dat")

	# Define all required models
	detector = dlib.get_frontal_face_detector()
	sp = dlib.shape_predictor(predictor_path)
	facerec = dlib.face_recognition_model_v1(face_rec_model_path)

	# Preprocessing of original image
	# Preprocessing of images contains three steps:
	# 1. Detect face
	# 2. Bound shape for detected face
	# 3. Using detected region and prelearned model, calclulate its features representation
	orig_img = dlib.load_rgb_image(orig_path)
	orig_det = detector(orig_img, 1)
	orig_shp = sp(orig_img, orig_det[0])
	orig_descriptor = facerec.compute_face_descriptor(orig_img, orig_shp)

	# Preprocessing of the image from camera
	check_img = dlib.load_rgb_image(check_path)
	check_det = detector(check_img, 1)
	face_num = len(check_det)
	if face_num > 1:
		error = "Fail. Too many people!"
		return error, distance, face_num
	if face_num < 1:
		error = "Fail. No faces!"
		return error, distance, face_num
	check_shp = sp(check_img, check_det[0])
	check_descriptor = facerec.compute_face_descriptor(check_img, check_shp)

	# Calculate euclidean distance between representations of images to compute the difference between faces
	distance = sum([(check_descriptor[i]-orig_descriptor[i])**2 for i in range(128)])**0.5
	return error, distance, face_num
