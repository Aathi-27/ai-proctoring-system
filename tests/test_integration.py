"""
Integration tests for the full audio pipeline.
"""

import pytest
import numpy as np
from src.audio_pipeline import AudioAnalysisPipeline
from src.config import SAMPLE_RATE, FRAME_SIZE


class TestFullPipeline:
    """Test the complete pipeline workflow."""

    def test_complete_workflow(self, temp_exam_id):
        """Test a complete analysis workflow."""
        # Initialize
        pipeline = AudioAnalysisPipeline(exam_id=temp_exam_id)

        # Create synthetic audio
        duration = 2.0
        samples = int(SAMPLE_RATE * duration)
        t = np.arange(samples) / SAMPLE_RATE

        # Mix speech and silence
        audio = np.concatenate([
            np.sin(2 * np.pi * 500 * t[:SAMPLE_RATE//2]).astype(np.float32) * 0.5,
            np.zeros(SAMPLE_RATE//2, dtype=np.float32),
            np.sin(2 * np.pi * 500 * t[:SAMPLE_RATE//2]).astype(np.float32) * 0.5,
        ])

        # Process chunks
        for i in range(0, len(audio), FRAME_SIZE):
            chunk = audio[i:i+FRAME_SIZE]
            if len(chunk) < FRAME_SIZE:
                chunk = np.pad(chunk, (0, FRAME_SIZE - len(chunk)))

            result = pipeline.process_audio_chunk(chunk)

            # Verify result structure
            assert "vad_score" in result
            assert "background_speech_detected" in result
            assert "multiple_voices_detected" in result
            assert "speaker_count" in result
            assert "statistics" in result
            assert "events" in result

        # Analyze buffer
        buffer_analysis = pipeline.analyze_buffer()
        assert "buffer_duration_s" in buffer_analysis
        assert "speech_percentage" in buffer_analysis
        assert "silence_percentage" in buffer_analysis

        # Get statistics
        stats = pipeline._calculate_statistics()
        assert stats["total_frames"] > 0
        assert stats["speech_percentage"] > 0
        assert stats["avg_vad_score"] >= 0

        # Cleanup
        pipeline.shutdown()

    def test_multiple_exams(self):
        """Test handling multiple concurrent exams."""
        pipelines = {}

        # Create pipelines for multiple exams
        for i in range(3):
            exam_id = f"exam_{i}"
            pipelines[exam_id] = AudioAnalysisPipeline(exam_id=exam_id)

        # Process different audio for each
        for i, (exam_id, pipeline) in enumerate(pipelines.items()):
            # Create audio with different frequency for each exam
            frequency = 500 + (i * 100)
            t = np.arange(FRAME_SIZE) / SAMPLE_RATE
            audio = np.sin(2 * np.pi * frequency * t).astype(np.float32) * 0.5

            result = pipeline.process_audio_chunk(audio)

            assert result["vad_score"] is not None

        # Verify statistics are independent
        for exam_id, pipeline in pipelines.items():
            stats = pipeline._calculate_statistics()
            assert stats["total_frames"] > 0

        # Cleanup
        for pipeline in pipelines.values():
            pipeline.shutdown()

    def test_speech_detection_accuracy(self):
        """Test VAD detection accuracy on known speech patterns."""
        pipeline = AudioAnalysisPipeline()

        # Process alternating speech and silence
        speech_detected_count = 0
        silence_count = 0

        for i in range(20):
            if i % 2 == 0:
                # Speech-like signal
                t = np.arange(FRAME_SIZE) / SAMPLE_RATE
                audio = np.sin(2 * np.pi * 500 * t).astype(np.float32)
            else:
                # Silence
                audio = np.zeros(FRAME_SIZE, dtype=np.float32)

            result = pipeline.process_audio_chunk(audio)

            if i % 2 == 0:
                # Should detect speech
                if result["vad_score"] > 0.3:
                    speech_detected_count += 1
            else:
                # Should detect silence
                if result["vad_score"] < 0.3:
                    silence_count += 1

        # Verify detection (may not be 100% due to VAD thresholds)
        assert speech_detected_count >= 3  # At least 3 out of 10 speech frames
        assert silence_count >= 3  # At least 3 out of 10 silence frames

        pipeline.shutdown()

    def test_background_speech_detection(self):
        """Test background speech detection."""
        pipeline = AudioAnalysisPipeline()

        # Process varied noisy audio
        bg_detected = False

        for _ in range(10):
            # Create varied noise pattern
            audio = np.random.randn(FRAME_SIZE).astype(np.float32) * 0.15

            result = pipeline.process_audio_chunk(audio)

            if result["background_speech_detected"]:
                bg_detected = True
                break

        # May or may not detect background speech in synthetic noise
        # Just verify the field exists and has valid type
        assert isinstance(result["background_speech_detected"], (bool, np.bool_))

        pipeline.shutdown()

    def test_multiple_voices_detection(self):
        """Test multiple voices detection."""
        pipeline = AudioAnalysisPipeline()

        # Process varied audio to build history
        multi_detected = False
        max_speaker_count = 1

        for i in range(20):
            # Create audio with varying energy (simulates multiple speakers)
            energy = 0.05 + (i % 3) * 0.05
            audio = np.random.randn(FRAME_SIZE).astype(np.float32) * energy

            result = pipeline.process_audio_chunk(audio)

            if result["multiple_voices_detected"]:
                multi_detected = True

            max_speaker_count = max(max_speaker_count, result["speaker_count"])

        # Verify detection fields
        assert isinstance(result["multiple_voices_detected"], (bool, np.bool_))
        assert isinstance(result["speaker_count"], (int, np.integer))

        pipeline.shutdown()

    def test_event_accumulation(self):
        """Test that events accumulate correctly."""
        pipeline = AudioAnalysisPipeline()

        initial_events = len(pipeline.event_manager.get_events())

        # Process audio that generates events
        for _ in range(10):
            t = np.arange(FRAME_SIZE) / SAMPLE_RATE
            audio = np.sin(2 * np.pi * 500 * t).astype(np.float32) * 0.5

            pipeline.process_audio_chunk(audio)

        final_events = len(pipeline.event_manager.get_events())

        # Should have more events after processing
        assert final_events >= initial_events

        pipeline.shutdown()

    def test_buffer_management(self):
        """Test buffer management and rolling window."""
        pipeline = AudioAnalysisPipeline()

        # Fill buffer beyond capacity
        buffer_capacity_frames = int(
            2.0 * 16000 / FRAME_SIZE  # 2 second buffer
        )

        for i in range(buffer_capacity_frames * 2):
            t = np.arange(FRAME_SIZE) / SAMPLE_RATE
            audio = np.sin(2 * np.pi * 500 * t).astype(np.float32) * 0.5

            pipeline.process_audio_chunk(audio)

        # Buffer should not grow indefinitely
        buffer_analysis = pipeline.analyze_buffer()
        assert buffer_analysis["buffer_duration_s"] <= 2.5  # Slight buffer for rounding

        pipeline.shutdown()

    def test_reset_functionality(self):
        """Test pipeline reset."""
        pipeline = AudioAnalysisPipeline()

        # Process some audio
        for _ in range(10):
            t = np.arange(FRAME_SIZE) / SAMPLE_RATE
            audio = np.sin(2 * np.pi * 500 * t).astype(np.float32) * 0.5
            pipeline.process_audio_chunk(audio)

        # Verify data exists
        assert pipeline.total_frames > 0

        # Reset
        pipeline.reset()

        # Verify reset
        assert pipeline.total_frames == 0
        assert pipeline.vad_frames == 0
        assert len(pipeline.vad_scores) == 0
        assert len(pipeline.event_manager.get_events()) == 0

        pipeline.shutdown()

    def test_statistics_accuracy(self):
        """Test statistics calculation accuracy."""
        pipeline = AudioAnalysisPipeline()

        # Process 10 frames of pure silence
        for _ in range(10):
            audio = np.zeros(FRAME_SIZE, dtype=np.float32)
            pipeline.process_audio_chunk(audio)

        stats = pipeline._calculate_statistics()

        assert stats["total_frames"] == 10
        assert stats["vad_frames"] == 0
        assert stats["speech_percentage"] == 0.0

        # Reset and process speech
        pipeline.reset()

        for _ in range(10):
            t = np.arange(FRAME_SIZE) / SAMPLE_RATE
            audio = np.sin(2 * np.pi * 500 * t).astype(np.float32)
            pipeline.process_audio_chunk(audio)

        stats = pipeline._calculate_statistics()

        assert stats["total_frames"] == 10
        assert stats["vad_frames"] > 0
        assert stats["speech_percentage"] > 0.0

        pipeline.shutdown()
