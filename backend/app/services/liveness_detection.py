import numpy as np
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
from app.core.config import settings


class LivenessDetectionService:
    def __init__(self):
        self.blink_history = {}
        self.movement_history = {}
        self.previous_poses = {}
        self.ear_history = {}
        self.last_blink_time = {}
        
    def calculate_eye_aspect_ratio(self, eye_landmarks: List[List[float]]) -> float:
        if len(eye_landmarks) < 6:
            return 0.3
        
        p1 = np.array(eye_landmarks[0][:2])
        p2 = np.array(eye_landmarks[1][:2])
        p3 = np.array(eye_landmarks[2][:2])
        p4 = np.array(eye_landmarks[3][:2])
        p5 = np.array(eye_landmarks[4][:2])
        p6 = np.array(eye_landmarks[5][:2])
        
        vertical_1 = np.linalg.norm(p2 - p6)
        vertical_2 = np.linalg.norm(p3 - p5)
        horizontal = np.linalg.norm(p1 - p4)
        
        if horizontal == 0:
            return 0.3
        
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
        return ear

    def detect_blink(self, exam_id: str, left_eye: List[List[float]], right_eye: List[List[float]]) -> Tuple[bool, Optional[float], Optional[str]]:
        left_ear = self.calculate_eye_aspect_ratio(left_eye)
        right_ear = self.calculate_eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        if exam_id not in self.ear_history:
            self.ear_history[exam_id] = []
        
        self.ear_history[exam_id].append({
            'ear': avg_ear,
            'left_ear': left_ear,
            'right_ear': right_ear,
            'timestamp': datetime.utcnow()
        })
        
        if len(self.ear_history[exam_id]) > 10:
            self.ear_history[exam_id] = self.ear_history[exam_id][-10:]
        
        if len(self.ear_history[exam_id]) >= 3:
            recent_ears = [h['ear'] for h in self.ear_history[exam_id][-5:]]
            
            below_threshold = [ear < settings.BLINK_EAR_THRESHOLD for ear in recent_ears[-3:]]
            
            if any(below_threshold) and len(recent_ears) >= 5:
                if recent_ears[-1] > settings.BLINK_EAR_THRESHOLD and min(recent_ears[-3:-1]) < settings.BLINK_EAR_THRESHOLD:
                    current_time = datetime.utcnow()
                    if exam_id not in self.last_blink_time or (current_time - self.last_blink_time[exam_id]).total_seconds() > 0.3:
                        self.last_blink_time[exam_id] = current_time
                        
                        if exam_id not in self.blink_history:
                            self.blink_history[exam_id] = []
                        self.blink_history[exam_id].append({
                            'timestamp': current_time,
                            'ear': avg_ear
                        })
                        
                        if len(self.blink_history[exam_id]) > 50:
                            self.blink_history[exam_id] = self.blink_history[exam_id][-50:]
                        
                        eye_type = "both"
                        if abs(left_ear - right_ear) > 0.05:
                            eye_type = "left" if left_ear < right_ear else "right"
                        
                        return True, avg_ear, eye_type
        
        return False, avg_ear, None

    def detect_movement(self, exam_id: str, head_pose: Dict[str, float]) -> Tuple[bool, Optional[Dict[str, float]]]:
        if exam_id not in self.previous_poses:
            self.previous_poses[exam_id] = head_pose
            return False, None
        
        prev_pose = self.previous_poses[exam_id]
        
        pitch_diff = abs(head_pose['pitch'] - prev_pose['pitch'])
        yaw_diff = abs(head_pose['yaw'] - prev_pose['yaw'])
        roll_diff = abs(head_pose['roll'] - prev_pose['roll'])
        
        total_change = pitch_diff + yaw_diff + roll_diff
        
        movement_detected = total_change > settings.MOVEMENT_THRESHOLD
        
        if movement_detected:
            if exam_id not in self.movement_history:
                self.movement_history[exam_id] = []
            
            self.movement_history[exam_id].append({
                'timestamp': datetime.utcnow(),
                'change': total_change,
                'pose': head_pose
            })
            
            if len(self.movement_history[exam_id]) > 50:
                self.movement_history[exam_id] = self.movement_history[exam_id][-50:]
            
            pose_change = {
                'pitch_change': pitch_diff,
                'yaw_change': yaw_diff,
                'roll_change': roll_diff,
                'total_change': total_change
            }
            
            self.previous_poses[exam_id] = head_pose
            return True, pose_change
        
        self.previous_poses[exam_id] = head_pose
        return False, None

    def calculate_liveness_score(self, exam_id: str) -> Tuple[float, int, int, bool]:
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=settings.LIVENESS_WINDOW_SECONDS)
        
        blink_count = 0
        if exam_id in self.blink_history:
            blink_count = len([
                b for b in self.blink_history[exam_id]
                if b['timestamp'] > window_start
            ])
        
        movement_count = 0
        if exam_id in self.movement_history:
            movement_count = len([
                m for m in self.movement_history[exam_id]
                if m['timestamp'] > window_start
            ])
        
        blink_score = min(blink_count * 10, 50)
        
        movement_score = min(movement_count * 5, 50)
        
        total_score = blink_score + movement_score
        
        is_live = blink_count > 0 and movement_count > 0
        
        return total_score, blink_count, movement_count, is_live

    def get_blink_count(self, exam_id: str, window_seconds: int = 30) -> int:
        if exam_id not in self.blink_history:
            return 0
        
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=window_seconds)
        
        return len([
            b for b in self.blink_history[exam_id]
            if b['timestamp'] > window_start
        ])

    def get_movement_count(self, exam_id: str, window_seconds: int = 30) -> int:
        if exam_id not in self.movement_history:
            return 0
        
        current_time = datetime.utcnow()
        window_start = current_time - timedelta(seconds=window_seconds)
        
        return len([
            m for m in self.movement_history[exam_id]
            if m['timestamp'] > window_start
        ])

    def clear_history(self, exam_id: str):
        if exam_id in self.blink_history:
            del self.blink_history[exam_id]
        if exam_id in self.movement_history:
            del self.movement_history[exam_id]
        if exam_id in self.previous_poses:
            del self.previous_poses[exam_id]
        if exam_id in self.ear_history:
            del self.ear_history[exam_id]
        if exam_id in self.last_blink_time:
            del self.last_blink_time[exam_id]
