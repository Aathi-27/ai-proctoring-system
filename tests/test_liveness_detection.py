import pytest
from datetime import datetime, timedelta
from app.services.liveness_detection import LivenessDetectionService


class TestLivenessDetectionService:
    def test_initialization(self, liveness_detection_service):
        assert liveness_detection_service is not None
        assert hasattr(liveness_detection_service, 'blink_history')
        assert hasattr(liveness_detection_service, 'movement_history')

    def test_calculate_eye_aspect_ratio(self, liveness_detection_service, sample_eye_landmarks):
        left_eye, right_eye = sample_eye_landmarks
        
        left_ear = liveness_detection_service.calculate_eye_aspect_ratio(left_eye)
        right_ear = liveness_detection_service.calculate_eye_aspect_ratio(right_eye)
        
        assert 0.0 <= left_ear <= 1.0
        assert 0.0 <= right_ear <= 1.0

    def test_calculate_eye_aspect_ratio_invalid_input(self, liveness_detection_service):
        invalid_eye = [[0.1, 0.1, 0.0]]
        ear = liveness_detection_service.calculate_eye_aspect_ratio(invalid_eye)
        assert ear == 0.3

    def test_detect_blink_initial(self, liveness_detection_service, sample_eye_landmarks):
        left_eye, right_eye = sample_eye_landmarks
        exam_id = "test_exam_1"
        
        blink_detected, ear, eye_type = liveness_detection_service.detect_blink(
            exam_id, left_eye, right_eye
        )
        
        assert isinstance(blink_detected, bool)
        assert isinstance(ear, float)
        assert 0.0 <= ear <= 1.0

    def test_detect_blink_multiple_frames(self, liveness_detection_service, sample_eye_landmarks):
        left_eye, right_eye = sample_eye_landmarks
        exam_id = "test_exam_2"
        
        for _ in range(5):
            liveness_detection_service.detect_blink(exam_id, left_eye, right_eye)
        
        assert exam_id in liveness_detection_service.ear_history
        assert len(liveness_detection_service.ear_history[exam_id]) > 0

    def test_detect_blink_closed_eyes(self, liveness_detection_service):
        exam_id = "test_exam_3"
        
        open_eye = [
            [0.3, 0.3, 0.0],
            [0.32, 0.29, 0.0],
            [0.34, 0.29, 0.0],
            [0.36, 0.3, 0.0],
            [0.34, 0.31, 0.0],
            [0.32, 0.31, 0.0]
        ]
        
        closed_eye = [
            [0.3, 0.3, 0.0],
            [0.32, 0.3, 0.0],
            [0.34, 0.3, 0.0],
            [0.36, 0.3, 0.0],
            [0.34, 0.3, 0.0],
            [0.32, 0.3, 0.0]
        ]
        
        for _ in range(3):
            liveness_detection_service.detect_blink(exam_id, open_eye, open_eye)
        
        for _ in range(2):
            liveness_detection_service.detect_blink(exam_id, closed_eye, closed_eye)
        
        liveness_detection_service.detect_blink(exam_id, open_eye, open_eye)
        
        assert exam_id in liveness_detection_service.ear_history

    def test_detect_movement_initial(self, liveness_detection_service):
        exam_id = "test_exam_4"
        head_pose = {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
        
        movement_detected, pose_change = liveness_detection_service.detect_movement(
            exam_id, head_pose
        )
        
        assert movement_detected is False
        assert pose_change is None
        assert exam_id in liveness_detection_service.previous_poses

    def test_detect_movement_significant_change(self, liveness_detection_service):
        exam_id = "test_exam_5"
        head_pose_1 = {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
        head_pose_2 = {"pitch": 15.0, "yaw": 20.0, "roll": 5.0}
        
        liveness_detection_service.detect_movement(exam_id, head_pose_1)
        movement_detected, pose_change = liveness_detection_service.detect_movement(
            exam_id, head_pose_2
        )
        
        assert movement_detected is True
        assert pose_change is not None
        assert 'pitch_change' in pose_change
        assert 'yaw_change' in pose_change
        assert 'roll_change' in pose_change
        assert 'total_change' in pose_change

    def test_detect_movement_small_change(self, liveness_detection_service):
        exam_id = "test_exam_6"
        head_pose_1 = {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
        head_pose_2 = {"pitch": 1.0, "yaw": 1.0, "roll": 1.0}
        
        liveness_detection_service.detect_movement(exam_id, head_pose_1)
        movement_detected, pose_change = liveness_detection_service.detect_movement(
            exam_id, head_pose_2
        )
        
        assert movement_detected is False

    def test_calculate_liveness_score_no_activity(self, liveness_detection_service):
        exam_id = "test_exam_7"
        
        score, blink_count, movement_count, is_live = \
            liveness_detection_service.calculate_liveness_score(exam_id)
        
        assert score == 0.0
        assert blink_count == 0
        assert movement_count == 0
        assert is_live is False

    def test_calculate_liveness_score_with_activity(self, liveness_detection_service):
        exam_id = "test_exam_8"
        
        liveness_detection_service.blink_history[exam_id] = [
            {'timestamp': datetime.utcnow(), 'ear': 0.15},
            {'timestamp': datetime.utcnow(), 'ear': 0.18}
        ]
        liveness_detection_service.movement_history[exam_id] = [
            {'timestamp': datetime.utcnow(), 'change': 25.0, 'pose': {"pitch": 10, "yaw": 15, "roll": 0}}
        ]
        
        score, blink_count, movement_count, is_live = \
            liveness_detection_service.calculate_liveness_score(exam_id)
        
        assert score > 0.0
        assert blink_count == 2
        assert movement_count == 1
        assert is_live is True

    def test_calculate_liveness_score_window(self, liveness_detection_service):
        exam_id = "test_exam_9"
        
        old_time = datetime.utcnow() - timedelta(seconds=60)
        recent_time = datetime.utcnow()
        
        liveness_detection_service.blink_history[exam_id] = [
            {'timestamp': old_time, 'ear': 0.15},
            {'timestamp': recent_time, 'ear': 0.18}
        ]
        
        score, blink_count, movement_count, is_live = \
            liveness_detection_service.calculate_liveness_score(exam_id)
        
        assert blink_count == 1

    def test_get_blink_count(self, liveness_detection_service):
        exam_id = "test_exam_10"
        
        liveness_detection_service.blink_history[exam_id] = [
            {'timestamp': datetime.utcnow(), 'ear': 0.15},
            {'timestamp': datetime.utcnow(), 'ear': 0.18}
        ]
        
        count = liveness_detection_service.get_blink_count(exam_id)
        assert count == 2

    def test_get_movement_count(self, liveness_detection_service):
        exam_id = "test_exam_11"
        
        liveness_detection_service.movement_history[exam_id] = [
            {'timestamp': datetime.utcnow(), 'change': 25.0, 'pose': {"pitch": 10, "yaw": 15, "roll": 0}}
        ]
        
        count = liveness_detection_service.get_movement_count(exam_id)
        assert count == 1

    def test_clear_history(self, liveness_detection_service):
        exam_id = "test_exam_12"
        
        liveness_detection_service.blink_history[exam_id] = [{'timestamp': datetime.utcnow(), 'ear': 0.15}]
        liveness_detection_service.movement_history[exam_id] = [{'timestamp': datetime.utcnow(), 'change': 25.0, 'pose': {}}]
        liveness_detection_service.previous_poses[exam_id] = {"pitch": 0, "yaw": 0, "roll": 0}
        
        liveness_detection_service.clear_history(exam_id)
        
        assert exam_id not in liveness_detection_service.blink_history
        assert exam_id not in liveness_detection_service.movement_history
        assert exam_id not in liveness_detection_service.previous_poses
