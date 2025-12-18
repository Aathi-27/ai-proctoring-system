import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional, Dict
from app.core.config import settings


class FaceDetectionService:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=settings.MAX_NUM_FACES,
            refine_landmarks=True,
            min_detection_confidence=settings.FACE_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.FACE_DETECTION_CONFIDENCE
        )
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=settings.FACE_DETECTION_CONFIDENCE
        )

    def detect_faces(self, image: np.ndarray) -> Tuple[int, List[float], List[List[float]], Optional[Dict[str, float]]]:
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        detection_results = self.face_detection.process(rgb_image)
        mesh_results = self.face_mesh.process(rgb_image)
        
        face_count = 0
        confidences = []
        all_landmarks = []
        bounding_box = None
        
        if detection_results.detections:
            face_count = len(detection_results.detections)
            confidences = [detection.score[0] for detection in detection_results.detections]
            
            if face_count > 0:
                detection = detection_results.detections[0]
                bbox = detection.location_data.relative_bounding_box
                h, w, _ = image.shape
                bounding_box = {
                    "x": bbox.xmin * w,
                    "y": bbox.ymin * h,
                    "width": bbox.width * w,
                    "height": bbox.height * h
                }
        
        if mesh_results.multi_face_landmarks:
            for face_landmarks in mesh_results.multi_face_landmarks:
                landmarks = []
                for landmark in face_landmarks.landmark:
                    landmarks.append([landmark.x, landmark.y, landmark.z])
                all_landmarks.append(landmarks)
        
        return face_count, confidences, all_landmarks, bounding_box

    def extract_eye_landmarks(self, landmarks: List[List[float]]) -> Tuple[List[List[float]], List[List[float]]]:
        LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        
        left_eye = [landmarks[i] for i in LEFT_EYE_INDICES]
        right_eye = [landmarks[i] for i in RIGHT_EYE_INDICES]
        
        return left_eye, right_eye

    def extract_face_outline_landmarks(self, landmarks: List[List[float]]) -> List[List[float]]:
        FACE_OUTLINE_INDICES = [
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
            397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
            172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109,
            10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
            397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
            172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109
        ]
        
        outline_landmarks = []
        for idx in FACE_OUTLINE_INDICES[:68]:
            if idx < len(landmarks):
                outline_landmarks.append(landmarks[idx])
        
        if len(outline_landmarks) < 68:
            step = len(landmarks) // 68
            outline_landmarks = [landmarks[i * step] for i in range(68)]
        
        return outline_landmarks

    def calculate_head_pose(self, landmarks: List[List[float]], image_shape: Tuple[int, int, int]) -> Dict[str, float]:
        h, w, _ = image_shape
        
        nose_tip = landmarks[1]
        chin = landmarks[152]
        left_eye = landmarks[33]
        right_eye = landmarks[263]
        left_mouth = landmarks[61]
        right_mouth = landmarks[291]
        
        model_points = np.array([
            (0.0, 0.0, 0.0),
            (0.0, -330.0, -65.0),
            (-225.0, 170.0, -135.0),
            (225.0, 170.0, -135.0),
            (-150.0, -150.0, -125.0),
            (150.0, -150.0, -125.0)
        ], dtype=np.float64)
        
        image_points = np.array([
            (nose_tip[0] * w, nose_tip[1] * h),
            (chin[0] * w, chin[1] * h),
            (left_eye[0] * w, left_eye[1] * h),
            (right_eye[0] * w, right_eye[1] * h),
            (left_mouth[0] * w, left_mouth[1] * h),
            (right_mouth[0] * w, right_mouth[1] * h)
        ], dtype=np.float64)
        
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        dist_coeffs = np.zeros((4, 1))
        
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        
        angles = self._rotation_matrix_to_euler_angles(rotation_matrix)
        
        return {
            "pitch": float(angles[0]),
            "yaw": float(angles[1]),
            "roll": float(angles[2])
        }

    def _rotation_matrix_to_euler_angles(self, R: np.ndarray) -> np.ndarray:
        sy = np.sqrt(R[0, 0] * R[0, 0] + R[1, 0] * R[1, 0])
        singular = sy < 1e-6
        
        if not singular:
            x = np.arctan2(R[2, 1], R[2, 2])
            y = np.arctan2(-R[2, 0], sy)
            z = np.arctan2(R[1, 0], R[0, 0])
        else:
            x = np.arctan2(-R[1, 2], R[1, 1])
            y = np.arctan2(-R[2, 0], sy)
            z = 0
        
        return np.degrees(np.array([x, y, z]))

    def __del__(self):
        if hasattr(self, 'face_mesh'):
            self.face_mesh.close()
        if hasattr(self, 'face_detection'):
            self.face_detection.close()
