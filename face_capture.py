import cv2
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
cascade_path = os.path.join(script_dir, 'haarcascade_frontalface_default.xml')
face_detector = cv2.CascadeClassifier(cascade_path)
if face_detector.empty():
    raise FileNotFoundError(f"Unable to load Haar Cascade XML file: {cascade_path}")

# Start webcam
cam = cv2.VideoCapture(0)
cam.set(3, 640)  # Width
cam.set(4, 480)  # Height

# Ask user ID
face_id = input('Enter numeric User ID: ').strip()
if not face_id:
    raise ValueError('User ID must not be empty.')
if not face_id.isdigit():
    raise ValueError('User ID must be numeric.')

sample_count_input = input('Enter number of face samples to capture [8]: ').strip()
if sample_count_input:
    if not sample_count_input.isdigit() or int(sample_count_input) <= 0:
        raise ValueError('Sample count must be a positive integer.')
    sample_count = int(sample_count_input)
else:
    sample_count = 8

print(f"Capturing {sample_count} face sample(s). Look at the camera...")

dataset_dir = os.path.join(script_dir, 'dataset')
if os.path.exists(dataset_dir) and not os.path.isdir(dataset_dir):
    raise FileExistsError(
        f"Cannot create dataset folder because a file exists at {dataset_dir}. "
        "Remove or rename that file and try again."
    )
os.makedirs(dataset_dir, exist_ok=True)

user_dir = os.path.join(dataset_dir, str(face_id))
os.makedirs(user_dir, exist_ok=True)

existing_images = [f for f in os.listdir(user_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
existing_count = 0
if existing_images:
    existing_numbers = []
    for filename in existing_images:
        name, _ = os.path.splitext(filename)
        tokens = name.replace('-', '_').split('_')
        if tokens and tokens[0].isdigit():
            try:
                existing_numbers.append(int(tokens[0]))
            except ValueError:
                pass
    if existing_numbers:
        existing_count = max(existing_numbers)

if existing_count:
    print(f"Found {existing_count} existing sample(s) for user {face_id}. New samples will start from {existing_count + 1}.")

count = existing_count
target_count = existing_count + sample_count
print(f"Saving face samples to {user_dir}")

while True:
    # Read camera frame
    ret, img = cam.read()

    if not ret:
        print("Failed to access camera")
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Loop through detected faces
    for (x, y, w, h) in faces:
        # Draw rectangle around face
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        count += 1

        # Save face image in per-user dataset folder
        file_name = os.path.join(user_dir, f"{face_id}_{count}.jpg")
        cv2.imwrite(file_name, gray[y:y + h, x:x + w])

        # Show count on screen
        cv2.putText(img, f"Image {count}/{target_count}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show camera window
    cv2.imshow('Face Capture', img)

    # Press ESC to stop
    k = cv2.waitKey(100) & 0xff
    if k == 27:
        break

    # Stop after capturing the requested number of images
    elif count >= target_count:
        break

print("Face samples taken successfully")

# Release camera and close windows
cam.release()
cv2.destroyAllWindows()