import cv2
import time

# Function to calculate the movement direction
def get_movement_direction(x, y, frame_center_x, frame_center_y, threshold=50):
    direction = ""
    if abs(x - frame_center_x) > threshold:
        if x < frame_center_x:
            direction += "Move Left "
        else:
            direction += "Move Right "
    if abs(y - frame_center_y) > threshold:
        if y < frame_center_y:
            direction += "Move Up"
        else:
            direction += "Move Down"
    if direction == "":
        direction = "Object is centered"
    return direction

# Function to adjust brightness and contrast of the image from the action cam
def adjust_brightness_contrast(image, brightness=30, contrast=30):
    brightness = int((brightness / 100.0) * 255)
    contrast = int(contrast / 100.0 * 127)
    return cv2.addWeighted(image, 1 + contrast/127.0, image, 0, brightness - contrast)

# Start video capture
cap = cv2.VideoCapture(0)  

if not cap.isOpened():
    print("Error: Could not open video stream")
    exit()


cap.set(cv2.CAP_PROP_BRIGHTNESS, 0.7)  
cap.set(cv2.CAP_PROP_CONTRAST, 0.7)   
cap.set(cv2.CAP_PROP_GAIN, 0.5)        
cap.set(cv2.CAP_PROP_EXPOSURE, -6)    


time.sleep(2)

# Read the first frame
ret, frame = cap.read()
if not ret:
    print("Failed to grab frame")
    cap.release()
    cv2.destroyAllWindows()
    exit()

frame = adjust_brightness_contrast(frame, brightness=50, contrast=40) 

bbox = cv2.selectROI("Frame", frame, False)
cv2.destroyWindow("Frame")

# Initialize the tracker
tracker = cv2.legacy.TrackerCSRT_create()
init_ok = tracker.init(frame, bbox)
print(f"Tracker initialized: {init_ok}")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    frame = adjust_brightness_contrast(frame, brightness=50, contrast=40)  # Adjust these values if needed

    ret, bbox = tracker.update(frame)
    print(f"Tracker update: {ret}, Bbox: {bbox}")

    if ret:
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, (0, 255, 0), 2, 1)

        box_center_x = int(bbox[0] + bbox[2] / 2)
        box_center_y = int(bbox[1] + bbox[3] / 2)

        frame_center_x = frame.shape[1] // 2
        frame_center_y = frame.shape[0] // 2

        direction = get_movement_direction(box_center_x, box_center_y, frame_center_x, frame_center_y)

        print(direction)
    else:
        cv2.putText(frame, "Tracking failure detected", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    cv2.imshow("Tracking", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()