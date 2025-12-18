import numpy as np
import torch
from silero_vad import load_silero_vad, get_speech_timestamps
from typing import Tuple, List, Dict
from src.config import (
    SAMPLE_RATE,
    FRAME_SIZE,
    VAD_THRESHOLD,
    FRAME_DURATION_MS,
)


class VoiceActivityDetector:
    """
    Real-time Voice Activity Detection using Silero VAD.
    
    Detects speech presence with minimal latency and CPU overhead.
    """

    def __init__(self):
        """Initialize the Silero VAD model."""
        self.model = load_silero_vad()
        self.device = torch.device("cpu")
        self.model.to(self.device)
        self.model.eval()

    def detect_voice_activity(self, audio_chunk: np.ndarray) -> float:
        """
        Detect voice activity in an audio chunk.

        Args:
            audio_chunk: Audio data (16 kHz, mono, PCM 16-bit)

        Returns:
            VAD score (0-1): Probability of speech presence
        """
        if len(audio_chunk) == 0:
            return 0.0

        # Normalize audio to float32 in range [-1, 1]
        audio_float = self._normalize_audio(audio_chunk)

        # Convert to torch tensor
        audio_tensor = torch.FloatTensor(audio_float).to(self.device)

        # Get VAD output
        with torch.no_grad():
            vad_prob = self.model(audio_tensor, SAMPLE_RATE).item()

        return max(0.0, min(1.0, vad_prob))

    def get_speech_timestamps(self, audio_data: np.ndarray) -> List[Dict]:
        """
        Get timestamps of speech segments in audio data.

        Args:
            audio_data: Full audio data (16 kHz, mono, PCM 16-bit)

        Returns:
            List of dicts with 'start' and 'end' keys (in milliseconds)
        """
        if len(audio_data) == 0:
            return []

        # Normalize audio
        audio_float = self._normalize_audio(audio_data)

        # Convert to torch tensor
        audio_tensor = torch.FloatTensor(audio_float).to(self.device)

        # Get speech timestamps
        speech_timestamps = get_speech_timestamps(
            audio_tensor,
            self.model,
            sampling_rate=SAMPLE_RATE,
            threshold=VAD_THRESHOLD,
            return_seconds=False,  # Return in samples
        )

        # Convert from samples to milliseconds
        result = []
        for ts in speech_timestamps:
            result.append(
                {
                    "start": int(ts["start"] / SAMPLE_RATE * 1000),
                    "end": int(ts["end"] / SAMPLE_RATE * 1000),
                }
            )

        return result

    def _normalize_audio(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
        Normalize audio from PCM 16-bit to float32 in range [-1, 1].

        Args:
            audio_chunk: Audio data

        Returns:
            Normalized audio data
        """
        # Convert to float if not already
        if audio_chunk.dtype != np.float32:
            audio_chunk = audio_chunk.astype(np.float32)

        # If values are in PCM 16-bit range, normalize
        if np.max(np.abs(audio_chunk)) > 1.0:
            audio_chunk = audio_chunk / 32768.0

        return audio_chunk
