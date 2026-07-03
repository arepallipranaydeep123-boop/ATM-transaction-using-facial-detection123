import cv2
import numpy as np
from PIL import Image
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
dataset_dir = os.path.join(script_dir, 'dataset')
trainer_dir = os.path.join(script_dir, 'trainer')
cascade_path = os.path.join(script_dir, 'haarcascade_frontalface_default.xml')

if os.path.exists(dataset_dir) and not os.path.isdir(dataset_dir):
    raise FileExistsError(
        f"Invalid dataset path: {dataset_dir} exists and is not a directory. "
        "Remove or rename that file before training."
    )

if os.path.exists(trainer_dir) and not os.path.isdir(trainer_dir):
    raise FileExistsError(
        f"Invalid trainer path: {trainer_dir} exists and is not a directory. "
        "Remove or rename that file before training."
    )

recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cascade_path)
if detector.empty():
    raise FileNotFoundError(f"Unable to load Haar Cascade XML file: {cascade_path}")


def get_id_from_path(root, imagePath):
    relpath = os.path.relpath(imagePath, root)
    parts = relpath.split(os.sep)

    # Prefer the parent folder name as user ID if it is numeric
    if len(parts) >= 2 and parts[0].isdigit():
        return int(parts[0])

    # Fallback to filename pattern User.<id>.<count>.jpg or <id>_<count>.jpg
    filename = os.path.basename(imagePath)
    tokens = filename.split('.')
    if len(tokens) >= 3 and tokens[0].lower().startswith('user'):
        return int(tokens[1])

    tokens = filename.replace('-', '_').split('_')
    if len(tokens) >= 2 and tokens[0].isdigit():
        return int(tokens[0])

    raise ValueError(f"Unable to determine user ID from filename: {imagePath}")


def getImagesAndLabels(path):
    imagePaths = []
    for dirpath, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                imagePaths.append(os.path.join(dirpath, f))

    if not imagePaths:
        raise FileNotFoundError(f"No image files found in dataset folder: {path}")

    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')

        user_id = get_id_from_path(path, imagePath)

        faces = detector.detectMultiScale(img_numpy)

        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y+h, x:x+w])
            ids.append(user_id)

    return faceSamples, ids

print("Training faces. Please wait...")
faces, ids = getImagesAndLabels(dataset_dir)
recognizer.train(faces, np.array(ids))

os.makedirs(trainer_dir, exist_ok=True)
recognizer.write(os.path.join(trainer_dir, 'trainer.yml'))

print("Model trained successfully")