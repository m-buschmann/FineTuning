# -*- coding: utf-8 -*-
"""REsNetpy.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jxZz8skQdsgeTB5gM72nuxYgwx7V2BkB
"""

import tensorflow as tf
import numpy as np
import datetime
import os
import matplotlib.pyplot as plt
from PIL import Image
import matplotlib.image as mpimg
import urllib.request
from keras.models import Model
from keras.layers import Dense, Flatten, BatchNormalization, Dropout
from keras.optimizers import Adam
import random


def image_preprocessing(path, images, augment=False):
    """Preprocesses a set of images located in the specified directory.

    Args:
    - path (str): Path to the directory containing the images
    - images (list): List to which the preprocessed images will be appended
    - augment (bool, optional): Whether to apply data augmentation to the images. Defaults to False

    Returns:
    - None

    Raises:
    - IOError: If the specified directory does not exist or cannot be accessed

    """
    file_list = os.listdir(path)
    for file in file_list:
        img = Image.open(path + file)
        img = img.resize((224, 224))
        if augment:
            img = tf.image.random_flip_left_right(img)
            img = tf.image.random_brightness(img, max_delta=0.2)
            img = tf.image.random_contrast(img, lower=0.5, upper=1.5)
        images.append(np.array(img))
        
@tf.autograph.experimental.do_not_convert
def dataset(path, label, augment=False):
  """Creates a TensorFlow dataset from a set of images located in the specified directory.

    Args:
    - path (str): Path to the directory containing the images
    - label (int): Label to assign to the images
    - augment (bool, optional): Whether to apply data augmentation to the images. Defaults to False

    Returns:
    - A TensorFlow dataset object containing the preprocessed images and their labels

    Raises:
    - IOError: If the specified directory does not exist or cannot be accessed
  """
  images = []
  image_preprocessing(path, images, augment=augment)
  labels = np.full(len(images), label)
  images = tf.convert_to_tensor(images)
  dataset = tf.data.Dataset.from_tensor_slices((images, labels))
  dataset = dataset.map(lambda img, label: (tf.cast(img, tf.float32), label))
  dataset = dataset.map(lambda img, label: ((img/128.)-1., label))
  dataset = dataset.map(lambda img, label: (img, tf.cast(label, tf.int32)))
  dataset = dataset.map(lambda img, label: (img, tf.one_hot(label, depth=4)))
  dataset = dataset.cache()

  return dataset
