import cv2
from ultralytics import YOLO
import openai
import time

# Initialize OpenAI API (Replace with your actual API key)
openai.api_key = 'AIzaSyCs820hbDlCWSZuSue5KyFLO22-IkKISiA'

# Load the YOLOv8 model
model = YOLO('yolov8n.pt')  # You can choose other variants like yolov8s.pt, yolov8m.pt, etc.

# Initialize webcam
cap = cv2.VideoCapture(0)

# Define a set of objects that will trigger AI actions
trigger_objects = {'person', 'cell phone', 'book'}

# To prevent repeated triggers, maintain a cooldown
last_trigger_time = 0
cooldown = 10  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Perform object detection
    results = model(frame)

    # Extract detected class names
    detected_classes = set()
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            detected_classes.add(cls_name)

            # Draw bounding box and label
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, cls_name, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    # Check for trigger objects and cooldown
    current_time = time.time()
    if trigger_objects & detected_classes and (current_time - last_trigger_time) > cooldown:
        last_trigger_time = current_time
        prompt = f"I see a {', '.join(trigger_objects & detected_classes)}. What should I do?"
        print(f"Triggering AI action for detected objects: {prompt}")

        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an assistant that provides helpful suggestions based on detected objects."},
                    {"role": "user", "content": prompt}
                ]
            )
            ai_response = response['choices'][0]['message']['content']
            print(f"AI Response: {ai_response}")
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")

    # Display the resulting frame
    cv2.imshow('YOLOv8 Object Detection', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
