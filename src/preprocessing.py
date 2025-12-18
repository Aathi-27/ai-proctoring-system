import numpy as np
import scipy.signal as signal
from src.config import SAMPLE_RATE, AUDIO_NORMALIZATION_ENABLED, NOISE_REDUCTION_ENABLED


class AudioPreprocessor:
    """
    Audio preprocessing pipeline for noise reduction and normalization.
    """

    def __init__(self):
        """Initialize the preprocessor."""
        self.noise_profile = None

    def preprocess(self, audio_chunk: np.ndarray) -> np.ndarray:
        """
        Preprocess audio chunk with noise reduction and normalization.

        Args:
            audio_chunk: Raw audio data

        Returns:
            Preprocessed audio data
        """
        processed = audio_chunk.copy()

        if NOISE_REDUCTION_ENABLED:
            processed = self._reduce_noise(processed)

        if AUDIO_NORMALIZATION_ENABLED:
            processed = self._normalize(processed)

        return processed

    def _reduce_noise(self, audio: np.ndarray) -> np.ndarray:
        """
        Reduce noise using spectral subtraction.

        Args:
            audio: Audio data

        Returns:
            Noise-reduced audio
        """
        # Simple high-pass filter to remove low-frequency noise
        sos = signal.butter(4, 80, "hp", fs=SAMPLE_RATE, output="sos")
        filtered = signal.sosfilt(sos, audio)

        return filtered

    def _normalize(self, audio: np.ndarray) -> np.ndarray:
        """
        Normalize audio to consistent dB level.

        Args:
            audio: Audio data

        Returns:
            Normalized audio
        """
        # Avoid division by zero
        if np.max(np.abs(audio)) == 0:
            return audio

        # Normalize to [-1, 1] range
        audio = audio / np.max(np.abs(audio))

        return audio

    def extract_mfcc_features(self, audio: np.ndarray, n_mfcc: int = 13) -> np.ndarray:
        """
        Extract MFCC features from audio.

        Args:
            audio: Audio data
            n_mfcc: Number of MFCC coefficients

        Returns:
            MFCC features
        """
        import librosa

        mfcc = librosa.feature.mfcc(y=audio, sr=SAMPLE_RATE, n_mfcc=n_mfcc)
        return mfcc

    def extract_spectral_features(self, audio: np.ndarray) -> dict:
        """
        Extract spectral features from audio.

        Args:
            audio: Audio data

        Returns:
            Dictionary with spectral features
        """
        import librosa

        # Compute spectrogram
        stft = np.abs(librosa.stft(audio))
        magnitude = np.abs(stft)

        # Spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(S=stft, sr=SAMPLE_RATE)[0]

        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(S=stft, sr=SAMPLE_RATE)[0]

        # Spectral energy
        spectral_energy = np.sqrt(np.sum(magnitude**2, axis=0))

        # Zero crossing rate
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio)[0]

        return {
            "spectral_centroid": np.mean(spectral_centroid),
            "spectral_rolloff": np.mean(spectral_rolloff),
            "spectral_energy": np.mean(spectral_energy),
            "zero_crossing_rate": np.mean(zero_crossing_rate),
        }

    def get_rms_energy(self, audio: np.ndarray) -> float:
        """
        Get RMS energy of audio.

        Args:
            audio: Audio data

        Returns:
            RMS energy
        """
        return float(np.sqrt(np.mean(audio**2)))

    def audio_to_db(self, amplitude: float, ref: float = 1.0) -> float:
        """
        Convert amplitude to dB.

        Args:
            amplitude: Amplitude value
            ref: Reference value

        Returns:
            dB value
        """
        if amplitude <= 0:
            return -np.inf
        return 20 * np.log10(amplitude / ref)
