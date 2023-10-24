import os
import numpy as np
from flask import Flask, flash, request, redirect, url_for, send_from_directory, jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from embeddings import create_embeddings, create_embeddings_from_text
import time
import urllib.parse

import werkzeug
from werkzeug.utils import secure_filename
from milvus_db import clap_db, search_milvus_db, insert_items 
from flask import Flask
from flask_cors import CORS
import logging

###############################################################################

UPLOAD_FOLDER = 'data_5k'
ASSET_FOLDER = 'Assets'
TEMP_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = {'ogg','wav'}
latency_fmt = "latency = {:.4f}s"

app = Flask(__name__)
cors = CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'

app.config['ASSET_FOLDER'] = ASSET_FOLDER
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMP_FOLDER'] = TEMP_FOLDER
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

#sound_put_args = reqparse.RequestParser()
#sound_put_args.add_argument("basename",type=str,help="Name of the sound", required=True)
#sound_put_args.add_argument("snd_info",type=str,help="Info of the sound", required=True)
#sound_put_args.add_argument("uuid",type=str,help="UUID  of the sound", required=True)
#sound_put_args.add_argument("upid",type=str,help="UPID of the sound", required=True)

#sound_update_args = reqparse.RequestParser()
#sound_update_args.add_argument("basename",type=str,help="Name of the sound", required=False)
#sound_update_args.add_argument("snd_info",type=str,help="Views of the sound", required=False)

#sound_put_args.add_argument("uuid",type=str,help="UUID  of the sound", required=False)
#sound_put_args.add_argument("upid",type=str,help="UPID of the sound", required=False)

################################

@app.route('/similarity_search_uuid/<sound_uuid>')
def search_uuid(sound_uuid):

    sound = clap_db.query(expr=f"uuid in [\"{sound_uuid}\"]", limit=1, output_fields=['embeddings'])
    if not sound:
        abort(404, message="Could not find sound with uuid=" + str(sound_uuid)  )

    # get embeddings
    vectors_to_search = [sound[0]['embeddings']]

    # search for embeddings
    result = search_milvus_db(vectors_to_search)[0]

    return jsonify(result)

################################

@app.route('/similarity_search_text/<text>')
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

@app.route('/search_by_sound', methods=['GET', 'POST'])
def search_sound():

    if request.method == 'POST':

        print ("search_sound started")
        start_time = time.time()
    
        print(request.files)

        f = request.files['file[]']
        filename = secure_filename(f.filename)
        f.save(app.config['TEMP_FOLDER'] + "/" + filename)
        #file = open(app.config['TEMP_FOLDER'] + filename,"rb")

        filename2 = os.path.join(app.root_path, app.config['TEMP_FOLDER'], filename)
      
        clap_db.load()

        # get embeddings
        vectors_to_search = create_embeddings({filename2})

        print(len(vectors_to_search[0]))

        # search for embeddings
        result = search_milvus_db(vectors_to_search)[0]

        end_time = time.time()
        print(latency_fmt.format(end_time - start_time))
        print ("search_sound done")
        return jsonify(result)
    
    return ''

################################

@app.route('/sound_info', methods=['GET', 'POST'])
def sound_info():

    if request.method == 'GET':

        clap_db.load()
        result = clap_db.query(expr="uuid != \"\" ", 
                               output_fields=["uuid","upid","product","name","preview","vendor","bank1","bank2","category","subcategory","mode"])
        
        return jsonify(result)

    return ''

###############################################################################

@app.route('/previews/<folder>/<filename>')
def get_preview(folder, filename):
    return send_from_directory(directory=app.config['UPLOAD_FOLDER'] + "/" + folder, filename=filename)

###############################################################################

@app.route('/assets/<folder>')
def get_asset(folder):
    return send_from_directory(directory=app.config['ASSET_FOLDER'] + "/" + folder, filename='NKS2_hardware_tile.webp')

###############################################################################

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


###############################################################################

if __name__ == "__main__":
    app.run(debug=True)
