import numpy as np
from collections import deque
from src.config import SAMPLE_RATE, BUFFER_WINDOW_DURATION_S


class AudioBuffer:
    """
    Manages a rolling window of audio data for analysis.
    """

    def __init__(self, duration_seconds: float = BUFFER_WINDOW_DURATION_S):
        """
        Initialize audio buffer.

        Args:
            duration_seconds: Duration of rolling window in seconds
        """
        self.duration_seconds = duration_seconds
        self.max_samples = int(SAMPLE_RATE * duration_seconds)
        self.buffer = deque(maxlen=self.max_samples)

    def add_audio(self, audio_chunk: np.ndarray) -> None:
        """
        Add audio chunk to buffer.

        Args:
            audio_chunk: Audio data to add
        """
        for sample in audio_chunk:
            self.buffer.append(sample)

    def get_buffer(self) -> np.ndarray:
        """
        Get current buffer content as numpy array.

        Returns:
            Current buffer as numpy array
        """
        return np.array(list(self.buffer), dtype=np.float32)

    def get_buffer_duration_s(self) -> float:
        """
        Get current buffer duration in seconds.

        Returns:
            Buffer duration in seconds
        """
        return len(self.buffer) / SAMPLE_RATE

    def clear(self) -> None:
        """Clear the buffer."""
        self.buffer.clear()

    def is_full(self) -> bool:
        """
        Check if buffer is full.

        Returns:
            True if buffer has reached max capacity
        """
        return len(self.buffer) == self.max_samples
