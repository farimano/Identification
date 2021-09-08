import os
from os.path import dirname, abspath
from flask import Flask, request, render_template, flash
from werkzeug.utils import secure_filename
import json
import time


def create_app(test_config=None):
	from . import db
	from .model import face_recog
	
	# Current directory
	cur_dir = dirname(abspath(__file__))
	
	# Create app and configure it
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_mapping(
		SECRET_KEY='dev',
		DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
		UPLOAD_FOLDER=os.path.join(cur_dir, "db/faces/check"),
		ORIG_FOLDER=os.path.join(cur_dir, "db/faces/orig"),
	)
	
	# Allowed extensions for photo
	ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
	
	# Try to load test configuration or usual configuration, if it exists
	if test_config is None:
		app.config.from_pyfile('config.py', silent=True)
	else:
		app.config.from_mapping(test_config)
	
	# If the instance folder doesn't exist, create it
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass
	
	# Check whether photo has allowed type or not
	def allowed_photo(name):
		is_dot = '.' in name
		is_allow = name.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
		return is_dot and is_allow
	
	# Save the selected id_event as json file
	def save_json(id_event, cursor):
		cursor.execute(
			"""
			SELECT e.error, e.error_description, e.recognition_degree,
			e.number_faces, u.name, p.title, p.id_pos
			FROM events e
			LEFT JOIN users u
			ON u.id_user = e.id_user
			LEFT JOIN positions p
			ON u.id_pos = p.id_pos
			WHERE e.id_event = ?""", 
			(id_event,)
		)
		row = cursor.fetchone()
		e, e_d, r_d, f_n, n, t, i_p = row
		if e:
			error_data = {'description':e_d}
		else:
			error_data = False
		result_data = {'N_faces':f_n, 'recognition_details':{'recognition_degree':r_d, 'threshold':0.6}}
		employ_data = {'name':n, 'position':{'id_pos':i_p, 'title':t} }
		data = {'error':error_data, 'result':result_data, 'employer':employ_data}
		
		pth = os.path.join(cur_dir, f"db/json/{id_event}.json")
		with open(pth, "w") as write_file:
			json.dump(data, write_file)
		
	
	# The "body" of app
	@app.route("/", methods=["GET", "POST"])
	def start():
		error, distance = None, None
		event_id = 0
		if request.method == "POST":
			# Load user_id and photo from request
			user_id = request.form.get('user_id')
			photo = request.files["user_photo"]
			
			# Check whether user_id is number or not
			try:
				user_id = int(user_id)
			except:
				error = "The id is not number!"
				flash(error)
				return render_template('base.html', out=None)
			
			# Check whether photo has allowed type or not
			if not allowed_photo(photo.filename):
				error = "This type of photo is not allowed!"
				flash(error)
				return render_template('base.html', out=None)

			# Make sure, that filename is safe
			name = secure_filename(photo.filename)
			
			# Get id of this event, so we can save all our data using this id
			con = db.get_db()
			cursor = con.cursor()
			cursor.execute(
				'INSERT INTO events (id_user) VALUES(?)', (user_id,))
			event_id = int(cursor.lastrowid)
			
			# Save the image
			name = str(event_id) + '.' + name.rsplit('.', 1)[1].lower()
			check_path = os.path.join(app.config['UPLOAD_FOLDER'], name)
			photo.save(check_path)
			
			# Check whether user_id is in database or not
			cursor.execute('SELECT * FROM users WHERE id_user=?', (user_id,))
			if not len(cursor.fetchall()):
				error = "This id does not exist in database."
				cursor.execute("UPDATE events SET (error, error_description)=(?, ?) WHERE id_event=?", (1, error, event_id))
				save_json(event_id, cursor)
				con.commit()
				return render_template('base.html', out=error)
			orig_path = os.path.join(app.config['ORIG_FOLDER'], f"{user_id}.jpg")
			
			error, distance, face_num = face_recog(orig_path, check_path)
			if error is None:
				# With threshold 0.6 this recognition test has 99.13% accuracy
				result = int(distance<0.6)
				if not result:
					error = "Fail. This person is not the id-card holder."
					cursor.execute("UPDATE events SET (recognition_degree, error, error_description, number_faces)=(?, ?, ?, ?) WHERE id_event=?", (distance, 1, error, face_num, event_id))
				else:
					cursor.execute("UPDATE events SET (recognition_degree, error, number_faces)=(?, ?, ?) WHERE id_event=?", (distance, 0, face_num, event_id))
			else:
				cursor.execute("UPDATE events SET (error, error_description, number_faces)=(?, ?, ?) WHERE id_event=?", (1, error, face_num, event_id))
			save_json(event_id, cursor)
			con.commit()
			if error:
				time.sleep(5)
			return render_template('base.html', out=error or "The idendification has been finished successfully!")
		return render_template('base.html', out=None)
	
	# Close the existed connection of database
	db.init_app(app)
	
	return app
