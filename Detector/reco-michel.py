import os
import sys
import click
import numpy as np
from copy import deepcopy
from PIL import Image, ImageDraw
from io import BytesIO
import requests

import tensorflow as tf
from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


# What model to download.
MODEL_1_NAME = 'modeles-mobile-ssd/object_detection_ok_V1/scanetiq'
MODEL_2_NAME = 'modeles-mobile-ssd/object_detection_ok_V2/scanetiq'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = os.path.join(MODEL_2_NAME, 'frozen_inference_graph.pb')
detection_graph = tf.Graph()
with detection_graph.as_default():
  od_graph_def = tf.compat.v1.GraphDef()
  with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
    serialized_graph = fid.read()
    od_graph_def.ParseFromString(serialized_graph)
    tf.import_graph_def(od_graph_def, name='')
    
# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = 'object_detection/data/mscoco_label_map.pbtxt'
NUM_CLASSES = 90
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


IMAGE_SIZE = (600, 800)

def load_image_into_numpy_array(image_path):
  # get image from url (parsed in Flask)
  res = requests.get(image_path)
  if res.status_code == 200:
    image_orig = Image.open(BytesIO(res.content))
    # resize img
    image = image_orig.resize(IMAGE_SIZE, resample=0)
    (im_width, im_height) = image.size
    # convert to np array
    img_arr = np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)
    return image_orig, img_arr
  else:
    return None

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
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            detection_masks, detection_boxes, image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(
            tf.greater(detection_masks_reframed, 0.5), tf.uint8)
        # Follow the convention by adding back the batch dimension
        tensor_dict['detection_masks'] = tf.expand_dims(
            detection_masks_reframed, 0)
      image_tensor = tf.compat.v1.get_default_graph().get_tensor_by_name('image_tensor:0')
      # Run inference
      output_dict = sess.run(tensor_dict,
                             feed_dict={image_tensor: np.expand_dims(image, 0)})
      # all outputs are float32 numpy arrays, so convert types as appropriate
      output_dict['num_detections'] = int(output_dict['num_detections'][0])
      output_dict['detection_classes'] = output_dict[
          'detection_classes'][0].astype(np.uint8)
      output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
      output_dict['detection_scores'] = output_dict['detection_scores'][0]
      if 'detection_masks' in output_dict:
        output_dict['detection_masks'] = output_dict['detection_masks'][0]
  return output_dict

@click.command()
@click.argument("image_url")
@click.option("-a", "apply", is_flag=True, help="Apply the mask if present")
def detect_label(image_url, apply):
  # the array based representation of the image will be used later in order to prepare the
  # result image with boxes and labels on it.
  image, image_np = load_image_into_numpy_array(image_url)
  # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
  image_np_expanded = np.expand_dims(image_np, axis=0)
  # Actual detection.
  output_dict = run_inference_for_single_image(image_np, detection_graph)

  #DEBUT AJOUT MICHEL
  detection_data = deepcopy(output_dict['detection_boxes']) #On crée une copie de l'aray d'array d'origine. c'est a lui qu'on va rajouter des trucs
  detection_data_size = len(detection_data)
  detection_data_tmp = np.zeros((detection_data_size, 5)) #Je peut pas rajouter les deux valeurs d'un coup, et je peut pas le faire dans le mêem tableau (il ne peut pas avoir des arrays a 4 entrée et des arrays a 5 entrée en même temps, par exemple. So, un tableau temporaire est utilisé
  detection_data_final = np.zeros((detection_data_size, 6)) #tableau final des résultats
  detection_data_end =  np.zeros((detection_data_size, 6)) #Test pour virer le retour a la ligne (?) du tableau)
  i = 0
  while i < detection_data_size:
    detection_data_tmp[i] = np.append(detection_data[i], output_dict['detection_classes'][i]) #on ajoute la classe au tableau
    detection_data_final[i] = np.append(detection_data_tmp[i], output_dict['detection_scores'][i]) #on ajoute le score au tableau
    detection_data_final[i] = detection_data_final[i].astype(np.float64)
    i += 1
  #FIN AJOUT MICHEL

  final_img = np.array(image)
  vis_util.visualize_boxes_and_labels_on_image_array(
      final_img,
      output_dict['detection_boxes'],
      output_dict['detection_classes'],
      output_dict['detection_scores'],
      category_index,
      instance_masks=output_dict.get('detection_masks'),
      use_normalized_coordinates=True,
      line_thickness=8)
  img = Image.fromarray(final_img)
  image_name = image_url.split("/")[-1].split(".j")[0]
  image_path = os.path.join("results", image_name)
  img.save(image_path + "_detect.jpg")
  with open(image_path + "_listbox.txt", 'w') as f:
    print(detection_data_final, file=f)

if __name__ == "__main__":
  detect_label()

