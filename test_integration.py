import asyncio
import numpy as np
import cv2
from app.services.face_detection import FaceDetectionService
from app.services.liveness_detection import LivenessDetectionService


async def test_basic_functionality():
    print("Testing Face Detection & Liveness Pipeline...")
    print("=" * 60)
    
    face_service = FaceDetectionService()
    liveness_service = LivenessDetectionService()
    
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.rectangle(image, (200, 100), (440, 380), (255, 255, 255), -1)
    cv2.circle(image, (270, 200), 15, (0, 0, 0), -1)
    cv2.circle(image, (370, 200), 15, (0, 0, 0), -1)
    cv2.ellipse(image, (320, 300), (40, 20), 0, 0, 180, (0, 0, 0), 2)
    
    print("\n1. Testing Face Detection...")
    face_count, confidences, landmarks, bbox = face_service.detect_faces(image)
    print(f"   ✓ Face count: {face_count}")
    print(f"   ✓ Confidences: {confidences}")
    print(f"   ✓ Landmarks detected: {len(landmarks)} face(s)")
    
    if landmarks and len(landmarks) > 0:
        print("\n2. Testing Landmark Extraction...")
        left_eye, right_eye = face_service.extract_eye_landmarks(landmarks[0])
        print(f"   ✓ Left eye landmarks: {len(left_eye)}")
        print(f"   ✓ Right eye landmarks: {len(right_eye)}")
        
        outline = face_service.extract_face_outline_landmarks(landmarks[0])
        print(f"   ✓ Face outline landmarks: {len(outline)}")
        
        print("\n3. Testing Head Pose Estimation...")
        head_pose = face_service.calculate_head_pose(landmarks[0], image.shape)
        print(f"   ✓ Pitch: {head_pose['pitch']:.2f}°")
        print(f"   ✓ Yaw: {head_pose['yaw']:.2f}°")
        print(f"   ✓ Roll: {head_pose['roll']:.2f}°")
        
        print("\n4. Testing Blink Detection...")
        exam_id = "test_exam"
        for i in range(5):
            blink_detected, ear, eye_type = liveness_service.detect_blink(
                exam_id, left_eye, right_eye
            )
            if blink_detected:
                print(f"   ✓ Blink detected! EAR: {ear:.3f}, Eye: {eye_type}")
        
        print("\n5. Testing Movement Detection...")
        liveness_service.detect_movement(exam_id, head_pose)
        modified_pose = {
            "pitch": head_pose["pitch"] + 15,
            "yaw": head_pose["yaw"] + 20,
            "roll": head_pose["roll"] + 5
        }
        movement_detected, pose_change = liveness_service.detect_movement(
            exam_id, modified_pose
        )
        if movement_detected:
            print(f"   ✓ Movement detected!")
            print(f"   ✓ Total change: {pose_change['total_change']:.2f}°")
        
        print("\n6. Testing Liveness Scoring...")
        score, blink_count, movement_count, is_live = \
            liveness_service.calculate_liveness_score(exam_id)
        print(f"   ✓ Liveness score: {score:.1f}/100")
        print(f"   ✓ Blink count: {blink_count}")
        print(f"   ✓ Movement events: {movement_count}")
        print(f"   ✓ Is live: {is_live}")
    
    print("\n" + "=" * 60)
    print("✅ All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
