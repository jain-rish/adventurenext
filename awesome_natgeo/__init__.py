#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 13 09:55:13 2018

@author: rishabh
"""


from flask import Flask

app = Flask(__name__)
app.config.from_object(__name__) 
app.config.update(dict(

        UPLOAD_FOLDER = "awesome_natgeo/static/img/tmp/",
        DATA_FOLDER = "awesome_natgeo/models/",
        ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
))

#from awesome_natgeo import views
from awesome_natgeo import validation