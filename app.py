import os
import numpy as np
from flask import Flask, flash, request, redirect, url_for, send_from_directory
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from embeddings import create_embeddings

from werkzeug.utils import secure_filename

###############################################################################

UPLOAD_FOLDER = 'data/previews'
ALLOWED_EXTENSIONS = {'ogg'}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/database.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

api = Api(app)

db = SQLAlchemy(app)

###############################################################################

class ProductModel(db.Model):
    id          = db.Column(db.String(36), primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    image_url   = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Prduct(id={id}, name = {name}, image_url={image_url})"

class SoundModel(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    uuid        = db.Column(db.String(36), primary_key=True)
    upid        = db.Column(db.String(36), nullable=False)
    name        = db.Column(db.String(100), nullable=False)
    preview     = db.Column(db.String, nullable=True)
    snd_info    = db.Column(db.String, nullable = False)
    embeddings  = db.Column(db.Binary)

    def __repr__(self):
        return f"Sound(id={id}, name = {name}, snd_info={snd_info})"

resource_fields = {
    'id': fields.Integer,
    'uuid' : fields.String,
    'upid' : fields.String,
    'name' : fields.String,
    'snd_info' : fields.String,
}

db.create_all()

################################

sound_put_args = reqparse.RequestParser()
sound_put_args.add_argument("name",type=str,help="Name of the sound", required=True)
sound_put_args.add_argument("snd_info",type=str,help="Info of the sound", required=True)
sound_put_args.add_argument("uuid",type=str,help="UUID  of the sound", required=True)
sound_put_args.add_argument("upid",type=str,help="UPID of the sound", required=True)

sound_update_args = reqparse.RequestParser()
sound_update_args.add_argument("name",type=str,help="Name of the sound", required=False)
sound_update_args.add_argument("snd_info",type=str,help="Views of the sound", required=False)
sound_put_args.add_argument("uuid",type=str,help="UUID  of the sound", required=False)
sound_put_args.add_argument("upid",type=str,help="UPID of the sound", required=False)

class Sound(Resource):

    @marshal_with(resource_fields)
    def get(self, sound_id):
        result = SoundModel.query.filter_by(id=sound_id).first()
        if not result:
            abort(404, message="Could not find sound with id=" + str(sound_id)  )
        return result
    
    @marshal_with(resource_fields)
    def put(self, sound_id):



        result = SoundModel.query.filter_by(id=sound_id).first()
        ##if result:
        ##    abort(409, message="Sound with id=" + str(sound_id) + " already exists.")

        # check if preview exists


        # calculate embeddings
        embeddings = create_embeddings()
        print(embeddings)
    
        # create sound
        args = sound_put_args.parse_args()
        sound = SoundModel(id=sound_id, 
                           name=args['name'], 
                           snd_info=args['snd_info'], 
                           uuid = args['uuid'],
                           upid = args['upid'],
                           embeddings=np.getbuffer(embeddings))
        db.session.add(sound)
        db.session.commit()

        return sound, 201

    @marshal_with(resource_fields)
    def patch(self, sound_id):
        sound = SoundModel.query.filter_by(id=sound_id).first()
        if not sound:
            abort(404, message="Could not find sound with id=" + str(sound_id)  )
        args = sound_put_args.parse_args()

        if args['name']:
            sound.name = args['name']
        if args['snd_info']:
            sound.snd_info = args['snd_info']

        db.session.commit()
        return sound, 201


    def delete(self, sound_id):
        sound = SoundModel.query.filter_by(id=sound_id).first()
        if not sound:
            abort(404, message="Could not find sound with id=" + str(sound_id)  )
        db.session.delete(sound)
        return '', 204


api.add_resource(Sound,"/sounds/<int:sound_id>")

###############################################################################


app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route("/upload", methods = ["GET", "POST"])
def upload_file():
    if request.method == 'POST':
        
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        print(request.files)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return '', 201 #redirect(url_for('download_file', name=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

###############################################################################

if __name__ == "__main__":
    app.run(debug=True)