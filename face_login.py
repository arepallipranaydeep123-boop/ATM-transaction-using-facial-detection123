import cv2
import os


script_dir = os.path.dirname(os.path.abspath(__file__))
trainer_dir = os.path.join(script_dir, 'trainer')
trainer_path = os.path.join(trainer_dir, 'trainer.yml')
cascadePath = os.path.join(script_dir, 'haarcascade_frontalface_default.xml')
dataset_dir = os.path.join(script_dir, 'dataset')

if os.path.exists(trainer_dir) and not os.path.isdir(trainer_dir):
    raise FileExistsError(
        f"Invalid trainer path: {trainer_dir} exists and is not a directory. "
        "Remove or rename that file before running face_login.py."
    )

if not os.path.exists(trainer_path):
    raise FileNotFoundError(f"Model file not found: {trainer_path}. Run train_model.py first.")

user_ids = set()
for dirpath, _, files in os.walk(dataset_dir):
    for filename in files:
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        rel = os.path.relpath(dirpath, dataset_dir)
        first_part = rel.split(os.sep)[0]
        if first_part.isdigit():
            user_ids.add(int(first_part))
            continue

        if filename.lower().startswith('user.'):
            tokens = filename.split('.')
            if len(tokens) >= 3 and tokens[1].isdigit():
                user_ids.add(int(tokens[1]))
                continue

        tokens = filename.replace('-', '_').split('_')
        if len(tokens) >= 2 and tokens[0].isdigit():
            user_ids.add(int(tokens[0]))

if not user_ids:
    raise ValueError(
        "Cannot login without any trained users. "
        "At least 1 user must be trained before running face_login.py."
    )

default_names = {0: 'User0', 1: 'Pranay', 2: 'User2', 3: 'User3'}
max_id = max(user_ids)
names = [''] * (max_id + 1)
for uid in sorted(user_ids):
    names[uid] = default_names.get(uid, f'User{uid}')

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read(trainer_path)

faceCascade = cv2.CascadeClassifier(cascadePath)
if faceCascade.empty():
    raise FileNotFoundError(f"Unable to load Haar Cascade XML file: {cascadePath}")

font = cv2.FONT_HERSHEY_SIMPLEX
THRESHOLD = 50
MIN_CONFIDENCE_SCORE = 75
MIN_CONSECUTIVE_MATCHES = 3

expected_input = input('Enter expected user ID or username: ').strip()
if not expected_input:
    raise ValueError('Expected user ID or username must not be empty.')

expected_id = None
expected_name = None
if expected_input.isdigit():
    expected_id = int(expected_input)
    if expected_id < 0 or expected_id >= len(names) or not names[expected_id]:
        print(f'Warning: expected user ID {expected_id} is not a known dataset user.')
    expected_name = names[expected_id] if 0 <= expected_id < len(names) else None
else:
    expected_name = expected_input.lower()

print(f"\nExpecting user: {expected_name or expected_id}")
print("Point your face at the camera. Press ESC to exit.\n")

cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)

minW = 0.1 * cam.get(3)
minH = 0.1 * cam.get(4)

authenticated = False
current_match_id = None
consecutive_matches = 0

while True:
    ret, img = cam.read()
    if not ret:
        print('Failed to access camera')
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.3,
        minNeighbors=6,
        minSize=(int(minW), int(minH)),
    )

    for (x, y, w, h) in faces:
        face_area = w * h
        img_area = img.shape[0] * img.shape[1]
        if face_area < img_area * 0.05 or face_area > img_area * 0.45:
            print(f"DEBUG: Ignoring face with abnormal size {face_area} px2")
            continue

        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        confidence_score = max(0, min(100, round(100 - confidence)))

        print(
            f"DEBUG: Detected ID={id}, confidence={confidence:.2f}, "
            f"score={confidence_score}%, threshold={THRESHOLD}, min_score={MIN_CONFIDENCE_SCORE}"
        )

        valid_label = 0 <= id < len(names) and names[id]
        is_confident = confidence < THRESHOLD and confidence_score >= MIN_CONFIDENCE_SCORE

        if valid_label and is_confident:
            name = names[id]
            confidence_text = f"{confidence_score}%"

            cv2.putText(img, str(name), (x + 5, y - 5), font, 1, (0, 255, 0), 2)
            cv2.putText(img, confidence_text, (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)

            expected_match = False
            if expected_id is not None:
                expected_match = expected_id == id
            elif expected_name is not None:
                expected_match = name.lower() == expected_name

            if expected_match:
                if current_match_id != id:
                    current_match_id = id
                    consecutive_matches = 1
                else:
                    consecutive_matches += 1

                print(
                    f"✓ Match: {name} (ID={id}) on frame "
                    f"({consecutive_matches}/{MIN_CONSECUTIVE_MATCHES})"
                )

                if consecutive_matches >= MIN_CONSECUTIVE_MATCHES:
                    print(
                        f"✓ AUTHENTICATED: {name} (ID={id}) with confidence {confidence:.2f}"
                    )
                    authenticated = True
                    cam.release()
                    cv2.destroyAllWindows()

                    try:
                    
                        import atm_system
                        atm_system.run(name)
                    except ModuleNotFoundError:
                        print("atm_system.py not found. Login completed.")
                    break
            else:
                current_match_id = None
                consecutive_matches = 0
                print(
                    f"✗ REJECTED: Recognized {name} (ID={id}) but expected '{expected_input}'"
                )
        else:
            current_match_id = None
            consecutive_matches = 0
            print("✗ UNKNOWN: Not confident enough or invalid label")
            cv2.putText(img, "UNKNOWN", (x + 5, y - 5), font, 1, (0, 0, 255), 2)

    if authenticated:
        break

    cv2.imshow('camera', img)

    k = cv2.waitKey(10) & 0xff
    if k == 27:
        break

cam.release()
cv2.destroyAllWindows()