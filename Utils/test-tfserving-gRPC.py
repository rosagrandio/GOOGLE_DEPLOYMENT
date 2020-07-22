import argparse
import numpy as np
import tensorflow as tf

from grpc.beta import implementations
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2

from tensorflow.keras.preprocessing import image

# Args
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Image PATH is required.")
ap.add_argument("-m", "--model", required=True, help="Model NAME is required.")
ap.add_argument("-v", "--version", required=True, help="Model VERSION is required.")
ap.add_argument("-p", "--port", required=True, help="Model PORT number is required.")
args = vars(ap.parse_args())

global image_path = args['image']
global model_name = args['model']
global model_version = args['version']
global port = args['port']

print("\nModel:",model_name)
print("\nModel version:",model_version)
print("Image:",image_path)
print("Port:",port)

# # Flags
# tf.app.flags.DEFINE_string("host", "127.0.0.1", "gRPC server host")
# tf.app.flags.DEFINE_integer("port", port, "gRPC server port")
# tf.app.flags.DEFINE_string("model_name", model, "TensorFlow model name")
# tf.app.flags.DEFINE_integer("model_version", version, "TensorFlow model version")
# tf.app.flags.DEFINE_float("request_timeout", 10.0, "Timeout of gRPC request")
# FLAGS = tf.app.flags.FLAGS


def main():
  host = "127.0.0.1"
  port = int(port)
  model_name = model_name
  model_version = model_version
  request_timeout = float(10)
  image_filepaths = [image_path]

  for index, image_filepath in enumerate(image_filepaths):
    image_ndarray = image.img_to_array(image.load_img(image_filepaths[0], target_size=(224, 224)))
    image_ndarray = image_ndarray / 255.

  # Create gRPC client and request
  channel = implementations.insecure_channel(host, port)
  stub = prediction_service_pb2.beta_create_PredictionService_stub(channel)
  request = predict_pb2.PredictRequest()
  request.model_spec.name = model_name
  request.model_spec.version.value = model_version
  request.inputs['input_image'].CopyFrom(tf.contrib.util.make_tensor_proto(image_ndarray, shape=[1] + list(image_ndarray.shape)))

  # Send request
  predictions = str(stub.Predict(request, request_timeout))
  print(predictions)
  mylist = predictions.split('\n')[-8:-3]
  finallist = []
  for element in mylist:
      element = element.split(':')[1]
      finallist.append(float("{:.6f}".format(float(element))))

  index = finallist.index(max(finallist))
  CLASSES = ['Daisy', 'Dandelion', 'Rosa', 'Sunflower', 'Tulip']

  ClassPred = CLASSES[index]
  ClassProb = finallist[index]

  print(finallist)
  print(ClassPred)
  print(ClassProb)

if __name__ == '__main__':
  main()
