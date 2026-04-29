import cv2
import numpy as np
import mediapipe as mp
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Global gesture state
gesture_state = {
    'x': 0.0,
    'y': 0.0,
    'strength': 0.0,
    'gesture_type': 'none',
    'particle_count': 0
}

camera = None
gesture_thread = None
running = False

def process_gestures():
    """Process camera feed for gestures in a separate thread"""
    global gesture_state, running, camera
    
    while running:
        ret, frame = camera.read()
        if not ret:
            continue
            
        # Flip the image horizontally for mirror view
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        results = hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Get palm center (average of key points)
                landmarks = hand_landmarks.landmark
                
                # Calculate palm center (approximate)
                palm_x = (landmarks[9].x + landmarks[0].x) / 2
                palm_y = (landmarks[9].y + landmarks[0].y) / 2
                
                # Check if fist is closed (finger tips close to palm)
                thumb_tip = landmarks[4]
                index_tip = landmarks[8]
                middle_tip = landmarks[12]
                ring_tip = landmarks[16]
                pinky_tip = landmarks[20]
                wrist = landmarks[0]
                
                # Calculate distances from wrist to finger tips
                finger_distances = [
                    np.sqrt((thumb_tip.x - wrist.x)**2 + (thumb_tip.y - wrist.y)**2),
                    np.sqrt((index_tip.x - wrist.x)**2 + (index_tip.y - wrist.y)**2),
                    np.sqrt((middle_tip.x - wrist.x)**2 + (middle_tip.y - wrist.y)**2),
                    np.sqrt((ring_tip.x - wrist.x)**2 + (ring_tip.y - wrist.y)**2),
                    np.sqrt((pinky_tip.x - wrist.x)**2 + (pinky_tip.y - wrist.y)**2),
                ]
                
                # Determine gesture type
                avg_distance = np.mean(finger_distances)
                
                if avg_distance < 0.3:  # Fist closed
                    gesture_state['gesture_type'] = 'attract'
                    gesture_state['strength'] = 500.0
                elif avg_distance > 0.5:  # Open hand
                    gesture_state['gesture_type'] = 'repel'
                    gesture_state['strength'] = 300.0
                else:  # Partial open
                    gesture_state['gesture_type'] = 'move'
                    gesture_state['strength'] = 200.0
                
                # Normalize coordinates to canvas size (will be adjusted by frontend)
                gesture_state['x'] = palm_x
                gesture_state['y'] = palm_y
                
                # Draw landmarks on frame for visualization
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS
                )
        else:
            gesture_state['gesture_type'] = 'none'
            gesture_state['strength'] = 0.0
        
        time.sleep(0.03)  # ~30 FPS

@app.route('/api/gesture', methods=['GET'])
def get_gesture():
    """Get current gesture state"""
    return jsonify(gesture_state)

@app.route('/api/start_camera', methods=['POST'])
def start_camera():
    """Start camera and gesture detection"""
    global camera, running, gesture_thread
    
    if camera is None:
        camera = cv2.VideoCapture(0)
        running = True
        gesture_thread = threading.Thread(target=process_gestures, daemon=True)
        gesture_thread.start()
        return jsonify({'status': 'started'})
    
    return jsonify({'status': 'already_running'})

@app.route('/api/stop_camera', methods=['POST'])
def stop_camera():
    """Stop camera and gesture detection"""
    global camera, running
    
    running = False
    if camera is not None:
        camera.release()
        camera = None
    
    return jsonify({'status': 'stopped'})

@app.route('/api/set_particles', methods=['POST'])
def set_particles():
    """Set particle count from frontend"""
    data = request.json
    gesture_state['particle_count'] = data.get('count', 0)
    return jsonify({'status': 'updated'})

if __name__ == '__main__':
    print("Starting Gesture Detection Server...")
    print("Server will run on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
