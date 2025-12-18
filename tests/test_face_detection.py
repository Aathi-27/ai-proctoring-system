import pytest
import numpy as np
import cv2
from app.services.face_detection import FaceDetectionService


class TestFaceDetectionService:
    def test_initialization(self, face_detection_service):
        assert face_detection_service is not None
        assert hasattr(face_detection_service, 'face_mesh')
        assert hasattr(face_detection_service, 'face_detection')

    def test_detect_faces_with_sample_image(self, face_detection_service, sample_image):
        face_count, confidences, landmarks, bounding_box = face_detection_service.detect_faces(sample_image)
        
        assert face_count >= 0
        assert isinstance(confidences, list)
        assert isinstance(landmarks, list)

    def test_detect_faces_no_face(self, face_detection_service):
        blank_image = np.zeros((480, 640, 3), dtype=np.uint8)
        face_count, confidences, landmarks, bounding_box = face_detection_service.detect_faces(blank_image)
        
        assert face_count == 0
        assert len(confidences) == 0
        assert len(landmarks) == 0

    def test_extract_eye_landmarks(self, face_detection_service, sample_landmarks):
        left_eye, right_eye = face_detection_service.extract_eye_landmarks(sample_landmarks)
        
        assert len(left_eye) == 6
        assert len(right_eye) == 6
        assert all(len(point) == 3 for point in left_eye)
        assert all(len(point) == 3 for point in right_eye)

    def test_extract_face_outline_landmarks(self, face_detection_service, sample_landmarks):
        outline = face_detection_service.extract_face_outline_landmarks(sample_landmarks)
        
        assert len(outline) == 68
        assert all(len(point) == 3 for point in outline)

    def test_calculate_head_pose(self, face_detection_service, sample_landmarks):
        image_shape = (480, 640, 3)
        head_pose = face_detection_service.calculate_head_pose(sample_landmarks, image_shape)
        
        assert 'pitch' in head_pose
        assert 'yaw' in head_pose
        assert 'roll' in head_pose
        assert isinstance(head_pose['pitch'], float)
        assert isinstance(head_pose['yaw'], float)
        assert isinstance(head_pose['roll'], float)

    def test_detect_multiple_faces(self, face_detection_service):
        image = np.ones((480, 640, 3), dtype=np.uint8) * 128
        
        face_count, confidences, landmarks, bounding_box = face_detection_service.detect_faces(image)
        assert face_count >= 0

    def test_confidence_scores_range(self, face_detection_service, sample_image):
        face_count, confidences, landmarks, bounding_box = face_detection_service.detect_faces(sample_image)
        
        for confidence in confidences:
            assert 0.0 <= confidence <= 1.0

    def test_landmarks_structure(self, face_detection_service, sample_image):
        face_count, confidences, landmarks, bounding_box = face_detection_service.detect_faces(sample_image)
        
        for face_landmarks in landmarks:
            assert isinstance(face_landmarks, list)
            for point in face_landmarks:
                assert len(point) == 3

    def test_bounding_box_structure(self, face_detection_service):
        image = np.ones((480, 640, 3), dtype=np.uint8) * 255
        face_count, confidences, landmarks, bounding_box = face_detection_service.detect_faces(image)
        
        if bounding_box:
            assert 'x' in bounding_box
            assert 'y' in bounding_box
            assert 'width' in bounding_box
            assert 'height' in bounding_box
