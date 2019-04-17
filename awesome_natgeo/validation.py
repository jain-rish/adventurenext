#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:56:53 2018

@author: rishabh
"""

import os
import datetime
import json

import flask
import numpy as np
import tensorflow as tf
import pandas as pd

from werkzeug.utils import secure_filename
from PIL import ExifTags, Image
from keras.applications import VGG16
from keras.preprocessing import image as kimage

from awesome_natgeo import app
from awesome_natgeo.models.similarity import find_matches


collection_features = np.load(os.path.join(app.config['DATA_FOLDER'],
                                           'fnumpy_rish.npy'))
files_and_titles=pd.read_csv(os.path.join(app.config['DATA_FOLDER'],
                                          'files_and_titles_rish.csv'))
size = collection_features.shape[0]
files_and_titles = files_and_titles.head(size)


app.secret_key = 'adam'


distance_metric = 'hamming'

if distance_metric == 'hamming':
    collection_features[collection_features>0]=1

#I was getting an error because the model was losing track of the graph
#defining graph here lets me keep track of it later as things move around
graph = tf.get_default_graph()

if collection_features.shape[1]==4096:
    model = VGG16(include_top=True, weights='imagenet')
    #remove the classification layer (fc8)
    model.layers.pop()
    #remove the next fully connected layer (fc7)
    model.layers.pop()
    #fix the output of the model
    model.outputs = [model.layers[-1].output]
else:
    model = VGG16(include_top=False, weights='imagenet')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def autorotate_image(filepath):
    
    '''Phones rotate images by changing exif data, 
    but we really need to rotate them for processing'''
    
    image=Image.open(filepath)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
            exif=dict(image._getexif().items())
    
        if exif[orientation] == 3:
            print('ROTATING 180')
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            print('ROTATING 270')
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            print('ROTATING 90')
            image=image.rotate(90, expand=True)
        image.save(filepath)
        image.close()
    except (AttributeError, KeyError, IndexError):
    # cases: image don't have getexif   
        pass
#    return(image)
    
def save_validation_result(result,user_image):
    '''loads json and saves results of validation test'''
    
    json_path = os.path.join(app.config['DATA_FOLDER'],'validation_results.json')

    newdata=[{'time':str(datetime.datetime.now()),
                                'result':result,
                                'user_image':user_image}]  
    with open(json_path, 'a') as fp:
        json.dump(newdata, fp, sort_keys=True, indent=4)
        
def show_results(imgurl, rotate_image=True):           
    #check and rotate cellphone images
    if rotate_image:
        autorotate_image(imgurl)
        
    #remove the first part of the file name
    img_name='/'.join(imgurl.rsplit('/')[1:])
    #load image for processing through the model
    img = kimage.load_img(imgurl, target_size=(224, 224))
    img = kimage.img_to_array(img)
    img = np.expand_dims(img, axis=0)  
    
    #there's an issue with the model losing track of the graph
    #I found this fix by searching for the error I was getting
    #see above
    global graph
    with graph.as_default():
        pred=model.predict(img)
    matches=find_matches(pred, collection_features, 
                         files_and_titles['imgfile'],dist=distance_metric)
    
    showresults=files_and_titles.set_index('imgfile',drop=False).join(matches.set_index('imgfile'))
    showresults.sort_values(by='simscore',ascending=True,inplace=True)

    original_url = img_name
    return flask.render_template('gallery.html',matches=showresults,original=original_url)

def show_results_validation(imgurl, rotate_image=True):
    if rotate_image:
        autorotate_image(imgurl)
        
    #load image for processing through the model
    img = kimage.load_img(imgurl, target_size=(224, 224))
    img = kimage.img_to_array(img)
    img = np.expand_dims(img, axis=0)  
    
    #there's an issue with the model losing track of the graph
    #I found this fix by searching for the error I was getting
    #see above
    global graph
    with graph.as_default():
        pred=model.predict(img)
    matches=find_matches(pred, collection_features, 
                         files_and_titles['imgfile'],dist='cosine')
    
    showresults=files_and_titles.set_index('imgfile',drop=False).join(matches.set_index('imgfile'))
    showresults.sort_values(by='simscore',ascending=True,inplace=True)
    
    randoms=np.random.randint(0,len(showresults),(50,1))
#            original_url = img_name
    original_url='/'.join(imgurl.rsplit('/')[1:])

    print('Rendering Validation Page')
    return flask.render_template('validate_results.html',
                                 matches=showresults,
                                 randoms=randoms.flatten().tolist(),
                                 original=original_url)
    
@app.route('/',  methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
        # Get method type
    method = flask.request.method
    print(method)


    if method == 'GET':
        return flask.render_template('index.html')
    
    if method == 'POST':
        # No file found in the POST submission
        if 'file' not in flask.request.files:
            print("FAIL")
            return flask.redirect(flask.request.url)

        # File was found
        file = flask.request.files['file']
        if file and allowed_file(file.filename):


            img_file = flask.request.files.get('file')
            #secure file name so stop hackers
            img_name = secure_filename(img_file.filename)

            # Write image to tmp folder so it can be shown on the next page 
            imgurl=os.path.join(app.config['UPLOAD_FOLDER'], img_name)
            file.save(imgurl)
            return(show_results(imgurl))     
        return flask.redirect(flask.request.url)

@app.route('/validate', methods=['GET', 'POST'])
def validation():
        # Get method type
    method = flask.request.method
    print(method)

    if method == 'GET':
        return flask.render_template('validate.html')
    
    if method == 'POST':
        # No file found in the POST submission
        if 'file' not in flask.request.files:
            print("FAIL")
            return flask.redirect(flask.request.url)

        # File was found
        file = flask.request.files['file']
        if file and allowed_file(file.filename):


            img_file = flask.request.files.get('file')            
            #secure file name so stop hackers
            img_name = secure_filename(img_file.filename)

            # Write image to tmp folder so it can be shown on the next page 
            imgurl=os.path.join(app.config['UPLOAD_FOLDER'], img_name)
            file.save(imgurl)
            return(show_results_validation(imgurl))
        return flask.redirect(flask.request.url)
    
       
@app.route('/random', methods=['GET', 'POST'])
def chose_random():
    method = flask.request.method
    if method == 'GET':
        return flask.render_template('validate.html')
    
    if method == 'POST':
        user_image = flask.request.form['submit']
        save_validation_result(0,user_image)
        return flask.render_template('validate.html')
    
@app.route('/algorithm', methods=['GET', 'POST'])
def chose_mine():
    method = flask.request.method
    if method == 'GET':
        return flask.render_template('validate.html')
    
    if method == 'POST':
        user_image = flask.request.form['submit']
        save_validation_result(1,user_image)
        return flask.render_template('validate.html')
