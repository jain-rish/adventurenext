"""
 Find similar images in a database by using transfer learning
 via a pre-trained VGG image classifier. 

@author: rishabh

"""
import sys, os
import numpy as np
from keras.preprocessing import image
from keras.models import Model
sys.path.append("src")

from vgg19 import VGG19
from imagenet_utils import preprocess_input


def main():
    # ================================================
    # Load pre-trained model and remove higher level layers
    # ================================================
    print("Loading VGG19 pre-trained model...")
    #base_model = VGG19(weights='imagenet')
    #model = Model(input=base_model.input, output=base_model.get_layer('block4_pool').output)

    model = VGG19(include_top=True, weights='imagenet')
    #remove the classification layer (fc8)
    model.layers.pop()
    #remove the next fully connected layer (fc7)
    model.layers.pop()
    #fix the output of the model
    model.outputs = [model.layers[-1].output]

    # ================================================
    # Read images and convert them to feature vectors
    # ================================================
    imgs, filename_heads, X = [], [], []
    path = "/Users/rishabh/Downloads/natgeo/test_data/"
    print("Reading images from '{}' directory...\n".format(path))
    images=sorted(os.listdir(path))
    print(images)
    for f in images:
        
        print(f)
        # Process filename
        filename = os.path.splitext(f)  # filename in directory
        filename_full = os.path.join(path,f)  # full path filename
        head, ext = filename[0], filename[1]
        if ext.lower() not in [".jpg", ".jpeg"]:
            continue

        # Read image file
        img = image.load_img(filename_full, target_size=(224, 224))  # load
        imgs.append(np.array(img))  # image
        filename_heads.append(head)  # filename head

        # Pre-process for model input
        img = image.img_to_array(img)  # convert to array
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        features = model.predict(img).flatten()  # features
        X.append(features)  # append feature extractor

    X = np.array(X)  # feature vectors
    imgs = np.array(imgs)  # images
    print("imgs.shape = {}".format(imgs.shape))
    print("X_features.shape = {}\n".format(X.shape))
    np.save('fnumpy_rish_57.npy',X)

# Driver
if __name__ == "__main__":
    main()