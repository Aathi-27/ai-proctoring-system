import pytest
import numpy as np
import cv2
import base64
from app.utils.image_processing import (
    decode_base64_image,
    encode_image_to_base64,
    resize_image,
    validate_image_format
)


class TestImageProcessing:
    def test_decode_base64_image_valid(self):
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        frame_data = f"data:image/jpeg;base64,{image_base64}"
        
        decoded_image = decode_base64_image(frame_data)
        
        assert decoded_image is not None
        assert len(decoded_image.shape) == 3
        assert decoded_image.shape[2] == 3

    def test_decode_base64_image_without_prefix(self):
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        _, buffer = cv2.imencode('.jpg', image)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        decoded_image = decode_base64_image(image_base64)
        
        assert decoded_image is not None
        assert len(decoded_image.shape) == 3

    def test_decode_base64_image_invalid(self):
        with pytest.raises(Exception):
            decode_base64_image("invalid_base64_string")

    def test_encode_image_to_base64(self):
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        encoded = encode_image_to_base64(image)
        
        assert encoded.startswith("data:image/jpeg;base64,")
        assert len(encoded) > 50

    def test_resize_image_large(self):
        image = np.ones((1080, 1920, 3), dtype=np.uint8) * 128
        
        resized = resize_image(image, max_width=640, max_height=480)
        
        assert resized.shape[0] <= 480
        assert resized.shape[1] <= 640

    def test_resize_image_small(self):
        image = np.ones((200, 300, 3), dtype=np.uint8) * 128
        
        resized = resize_image(image, max_width=640, max_height=480)
        
        assert resized.shape == image.shape

    def test_resize_image_maintains_aspect_ratio(self):
        image = np.ones((1000, 2000, 3), dtype=np.uint8) * 128
        
        resized = resize_image(image, max_width=640, max_height=480)
        
        original_aspect = image.shape[1] / image.shape[0]
        resized_aspect = resized.shape[1] / resized.shape[0]
        
        assert abs(original_aspect - resized_aspect) < 0.01

    def test_validate_image_format_valid(self):
        image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        is_valid, message = validate_image_format(image)
        
        assert is_valid is True
        assert message == "Valid"

    def test_validate_image_format_none(self):
        is_valid, message = validate_image_format(None)
        
        assert is_valid is False
        assert "None" in message

    def test_validate_image_format_grayscale(self):
        image = np.ones((100, 100), dtype=np.uint8) * 128
        
        is_valid, message = validate_image_format(image)
        
        assert is_valid is False
        assert "3-channel" in message

    def test_validate_image_format_too_small(self):
        image = np.ones((30, 30, 3), dtype=np.uint8) * 128
        
        is_valid, message = validate_image_format(image)
        
        assert is_valid is False
        assert "too small" in message

    def test_validate_image_format_wrong_channels(self):
        image = np.ones((100, 100, 4), dtype=np.uint8) * 128
        
        is_valid, message = validate_image_format(image)
        
        assert is_valid is False
        assert "3 channels" in message

    def test_encode_decode_roundtrip(self):
        original_image = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        encoded = encode_image_to_base64(original_image)
        decoded = decode_base64_image(encoded)
        
        assert decoded.shape == original_image.shape
