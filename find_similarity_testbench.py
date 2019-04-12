import numpy as np
import pandas as pd
from scipy.spatial import distance

from keras.preprocessing import image

from vgg19 import VGG19
from imagenet_utils import preprocess_input


model = VGG19(include_top=True, weights='imagenet')
#remove the classification layer (fc8)
model.layers.pop()
#remove the next fully connected layer (fc7)
model.layers.pop()
#fix the output of the model
model.outputs = [model.layers[-1].output]

def find_matches(pred, #features from user selected image
                 collection_features,  #list of features in the collection
                 images, #list of filenames associated with the features
                 dist='cosine' #distance metric - only cosine is good
                 ): 
    '''
    Finds matches for the features of the selected image, 
    according to the distance metric specified.
    Distance metrics use the scipy package
    '''   
    pred = pred.flatten()
    
    nimages = len(collection_features)
    sims = []
    for i in range(0,nimages):
        if dist=='euclidean':
            sims.append(distance.euclidean(pred.flatten(),
                                           collection_features[i].flatten()))
        elif dist=='hamming':
            pred[pred>0]=1
            sims.append(distance.hamming(pred.flatten(),
                                         collection_features[i].flatten()))
        else: #default to cosine
            sims.append(distance.cosine(pred.flatten(),
                                        collection_features[i].flatten()))
    print('max sim = ' +str(max(sims)))
    print('min sim = ' +str(min(sims)))
    print('top5_matches=', sorted(sims)[0:5])
    similar_images=pd.DataFrame({'imgfile':images,
                                 'simscore':sims})
    return(similar_images)
    
# TEST ...
collection_features= np.load('awesome_natgeo/models/fnumpy_rish.npy')
files_and_titles= pd.read_csv('awesome_natgeo/models/files_and_titles_rish.csv')

#load image for processing through the model
imgurl= '/Users/rishabh/Downloads/instagram_natgeo/natgeotravel/Bv9yGeODL9i.jpg'

# Read image file
img = image.load_img(imgurl, target_size=(224, 224))  # load


# Pre-process for model input
img = image.img_to_array(img)  # convert to array
img = np.expand_dims(img, axis=0)
img = preprocess_input(img)
pred = model.predict(img).flatten()  # features    

matches =find_matches(pred, collection_features, files_and_titles['imgfile'], dist='hamming')

