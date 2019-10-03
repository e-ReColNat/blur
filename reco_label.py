# coding: utf-8

import os
import sys
import numpy as np
import json
from copy import deepcopy
from PIL import Image, ImageDraw, ImageEnhance
from io import BytesIO
import requests
from random import shuffle
import logging

import tensorflow as tf
# shut tensorflow's mouth
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)  # or any {DEBUG, INFO, WARN, ERROR, FATAL}

from modeles_mobile_ssd.utils import ops as utils_ops
from modeles_mobile_ssd.utils import label_map_util
from modeles_mobile_ssd.utils import visualization_utils as vis_util


# models to use.
MODELS = ['modeles_mobile_ssd/object_detection_ok_V1/scanetiq',
          'modeles_mobile_ssd/object_detection_ok_V2/scanetiq']
graphes = []
for model_name in MODELS:
    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    path_to_ckpt = os.path.join(model_name, 'frozen_inference_graph.pb')
    detection_graph = tf.Graph()
    with detection_graph.as_default():
      od_graph_def = tf.compat.v1.GraphDef()
      with tf.io.gfile.GFile(path_to_ckpt, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')
    graphes.append(detection_graph)

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = 'modeles_mobile_ssd/utils/mscoco_label_map.pbtxt'
NUM_CLASSES = 90
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)

IMAGE_SIZE = (720, 1280)

def load_image_into_numpy_array(image_path):
  # get image from url (parsed in Flask)
  res = requests.get(image_path)
  if res.status_code == 200:
    try:
      image_orig = Image.open(BytesIO(res.content))
    except:
      if debug:
        logging.error("error reading image")
      exit(0)
    # rotate if needed
    (or_im_width, or_im_height) = image_orig.size
    if or_im_width > or_im_height:
      image_orig = image_orig.rotate(3*90, expand=True)    
    # resize img
    image = ImageEnhance.Contrast(image_orig).enhance(3.0)
    image = image.resize(IMAGE_SIZE, resample=Image.LANCZOS)
    (im_width, im_height) = image.size
    # convert to np array
    img_arr = np.array(image.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
    return image_orig, img_arr
  else:
    if debug:
        logging.error("error loading image")
    exit(0)

def draw_and_save(image, image_url, output_dict, detection_data_final, threshold, fileout, debug):
  image_name = image_url.split("/")[-1].split(".")[0]
  image_path = os.path.join("/var/www/detect_label/results", image_name)
  results = {}
  # save data
  results["detection_data"] = detection_data_final
  detection_data_final
  if debug:
    # draw detection zones with confidences
    detect_img = np.array(image)
    vis_util.visualize_boxes_and_labels_on_image_array(
        detect_img,
        output_dict['detection_boxes'],
        output_dict['detection_classes'],
        output_dict['detection_scores'],
        category_index,
        use_normalized_coordinates=True,
        min_score_thresh = threshold,
        #max_boxes_to_draw=2,
        skip_labels=True,
        line_thickness=8)
    detect_img = Image.fromarray(detect_img)
    detect_img.save(image_path + "_detect.jpg")
    results["detected_image"] = image_name + "_detect.jpg"
    image.save(image_path + "_original.jpg")
    results["original_image"] = image_name + "_original.jpg"
    with open(image_path + "_listbox.json", 'w') as f:
      json.dump(detection_data_final, f)
    results["result_data"] = image_name + "_listbox.json"
  # blank zones
  (im_width, im_height) = image.size
  for zone in output_dict['detection_boxes']:
    xy = [(zone[1] * im_width, zone[0] * im_height),
          (zone[3] * im_width, zone[2] * im_height)]
    drawer = ImageDraw.Draw(image)
    drawer.rectangle(xy, fill=0XFFFFFF, outline=None)
    del drawer
  image.save(image_path + "_censored.jpg")
  if fileout or debug:
    results["censored_image"] = image_name + "_censored.jpg"
  return results

def run_inference_for_single_image(image, graph):
  with graph.as_default():
    with tf.compat.v1.Session() as sess:
      # Get handles to input and output tensors
      ops = tf.compat.v1.get_default_graph().get_operations()
      all_tensor_names = {output.name for op in ops for output in op.outputs}
      tensor_dict = {}
      for key in ['num_detections', 'detection_boxes', 'detection_scores',
          'detection_classes', 'detection_masks']:
        tensor_name = key + ':0'
        if tensor_name in all_tensor_names:
          tensor_dict[key] = tf.compat.v1.get_default_graph().get_tensor_by_name(tensor_name)
      if 'detection_masks' in tensor_dict:
        # The following processing is only for single image
        detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
        detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
        # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
        real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
        detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
        detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(detection_masks, detection_boxes, image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(tf.greater(detection_masks_reframed, 0.5), tf.uint8)
        # Follow the convention by adding back the batch dimension
        tensor_dict['detection_masks'] = tf.expand_dims(detection_masks_reframed, 0)
      image_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name('image_tensor:0')
      # Run inference
      output_dict = sess.run(tensor_dict, feed_dict={image_tensor: np.expand_dims(image, 0)})
      # all outputs are float32 numpy arrays, so convert types as appropriate
      output_dict['num_detections'] = int(output_dict['num_detections'][0])
      output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(np.uint8)
      output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
      output_dict['detection_scores'] = output_dict['detection_scores'][0]
  return output_dict

def detect_label(image_url, threshold=65, fileout=True, debug=False):
  if debug:
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info("Loading image")
  # the array based representation of the image will be used later in order to prepare the
  # result image with boxes and labels on it.
  image, image_np = load_image_into_numpy_array(image_url)
  # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
  image_np_expanded = np.expand_dims(image_np, axis=0)
  # run inference on both models
  if debug:
    logging.info("Prediction")
  output_dict = {}
  for detection_graph in graphes:
    # Actual detection.
    tmp_out = run_inference_for_single_image(image_np, detection_graph)
    # concat results for both models
    for key in tmp_out:        
      if key in output_dict:
          if key == "num_detections":
            output_dict[key] += tmp_out[key]
          else:
            output_dict[key] = np.concatenate((output_dict[key], tmp_out[key]))
      else:
        output_dict[key] = tmp_out[key]
  if debug:
    logging.info("Saving data")
  # sort scores and boxes accordingly
  indexes = list(range(len(output_dict['detection_scores'])))
  indexes.sort(key=output_dict['detection_scores'].__getitem__, reverse=True)
  # filter over threshold
  for i, idx in enumerate(indexes):
    if debug:
      threshold = 0.05
    elif threshold > 1:
      threshold /= 100
    if output_dict['detection_scores'][idx] < threshold:
      break
  indexes = indexes[:i]
  output_dict['detection_scores'] = np.array(list(map(output_dict['detection_scores'].__getitem__, indexes)))
  output_dict['detection_boxes'] = np.array(list(map(output_dict['detection_boxes'].__getitem__, indexes)))
  # merge boxes data and confidence
  detection_data_final = []
  for i, score in enumerate(output_dict['detection_scores']):
    box_data = {}
    box_data[str(score)] = list(output_dict['detection_boxes'][i].astype(float))
    detection_data_final.append(box_data)
  if debug:
    logging.info("Saving images")
  # save images
  results = draw_and_save(image, image_url, output_dict, detection_data_final, threshold, fileout, debug)
  return results

if __name__ == "__main__":
  if len(sys.argv) > 1:
    if len(sys.argv[1]) > 0:
      image_url = str(sys.argv[1])
    else:
      print("error: no url")
      exit(-1)
  threshold = 65
  if len(sys.argv) > 2:
    threshold = float(sys.argv[2])    
  print(detect_label(image_url, threshold=threshold, fileout=True, debug=True))
