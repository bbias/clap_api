import os
import numpy as np
from flask import Flask, flash, request, redirect, url_for, send_from_directory, jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from embeddings import create_embeddings, create_embeddings_from_text
import time

import werkzeug
from werkzeug.utils import secure_filename
from milvus_db import clap_db, snd_info_db, search_milvus_db, insert_items 

###############################################################################

UPLOAD_FOLDER = 'data/previews'
ALLOWED_EXTENSIONS = {'ogg'}
latency_fmt = "latency = {:.4f}s"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 10000 * 10000

api = Api(app)


###############################################################################

resource_fields = {
    'id': fields.Integer,
    'uuid' : fields.String,
    'upid' : fields.String,
    'basename' : fields.String,
    'snd_info' : fields.String,
}

################################

sound_put_args = reqparse.RequestParser()
sound_put_args.add_argument("basename",type=str,help="Name of the sound", required=True)
sound_put_args.add_argument("snd_info",type=str,help="Info of the sound", required=True)
sound_put_args.add_argument("uuid",type=str,help="UUID  of the sound", required=True)
sound_put_args.add_argument("upid",type=str,help="UPID of the sound", required=True)

sound_update_args = reqparse.RequestParser()
sound_update_args.add_argument("basename",type=str,help="Name of the sound", required=False)
sound_update_args.add_argument("snd_info",type=str,help="Views of the sound", required=False)

sound_put_args.add_argument("uuid",type=str,help="UUID  of the sound", required=False)
sound_put_args.add_argument("upid",type=str,help="UPID of the sound", required=False)

################################

@app.route('/search_id/<int:sound_id>')
def search_sound(sound_id):

    sound = clap_db.query(expr=f"pk in [{sound_id}]", limit=1, output_fields=["embeddings"])
    if not sound:
        abort(404, message="Could not find sound with id=" + str(sound_id)  )

    # get embeddings
    vectors_to_search = [sound[0]['embeddings']]

    # search for embeddings
    result = search_milvus_db(vectors_to_search)[0]

    return jsonify(result)

################################

@app.route('/search_text/<text>')
def search_text(text):

    print ("search_sound(text) started")
    print(text)
    start_time = time.time()
    
    clap_db.load()

    print ([text,text])


    # get embeddings
    vectors_to_search = create_embeddings_from_text([text,text])

    print(len(vectors_to_search[0]))

    # search for embeddings
    result = search_milvus_db(vectors_to_search)[0]

    end_time = time.time()
    print(latency_fmt.format(end_time - start_time))
    print ("search_sound(text) done")
    return jsonify(result)

################################

@app.route('/sound_info', methods=['GET', 'POST'])
def sound_info():

    if request.method == 'GET':
        snd_info_db.load()

        result = snd_info_db.query(expr="uuid != \"\" ", output_fields=["uuid","upid","basename"])
        return jsonify(result)

    if request.method == 'POST':
        data = request.json

        entities = [
            [data['uuid']],  
            [data['upid']],  
            [data['basename']], 
            [np.random.randn(2)],    # field embeddings, supports numpy.ndarray and list
        ]

        insert_result = snd_info_db.insert(entities)

    return ''

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

        base = []
        uuids = []

        print ("Uploading started")
        start_time = time.time()


        audio_files = []
        for key, file in request.files.items() :

            if file and allowed_file(file.filename):

                basename = file.filename[:-4]
                base.append(basename)

                uuids.append(key)

                # save file    
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                
                audio_files.append(os.path.join(app.root_path,app.config['UPLOAD_FOLDER'], filename))

        # calc embeddings
        embeddings = create_embeddings(audio_files)

        end_time = time.time()
        print(latency_fmt.format(end_time - start_time))

        # add database
        entities = [
            uuids,
            base,
            embeddings,
        ]
        insert_items(entities)

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
