from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import io
from typing import Tuple, Dict, Any, Optional, Union
from src.audio_pipeline import AudioAnalysisPipeline
from src.config import FLASK_ENV, DEBUG, HOST, PORT, SAMPLE_RATE


app = Flask(__name__)
CORS(app)

# Global pipelines (one per exam)
pipelines = {}


def get_pipeline(exam_id: str) -> AudioAnalysisPipeline:
    """
    Get or create pipeline for exam.

    Args:
        exam_id: Exam ID

    Returns:
        Audio analysis pipeline
    """
    if exam_id not in pipelines:
        pipelines[exam_id] = AudioAnalysisPipeline(exam_id)
    return pipelines[exam_id]


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/exams/<exam_id>/analyze-audio", methods=["POST"])
def analyze_audio(exam_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Analyze audio chunk from exam.

    Expected request format:
    - audio/wav content with 16 kHz sample rate
    OR
    - JSON with base64 encoded audio

    Returns:
        JSON with VAD results and detected events
    """
    try:
        # Get audio data
        audio_data = _extract_audio_data(request)
        if audio_data is None:
            return jsonify({"error": "Invalid audio data"}), 400

        # Get pipeline
        pipeline = get_pipeline(exam_id)

        # Process audio
        result = pipeline.process_audio_chunk(audio_data)

        # Log events to database
        if result["events"]:
            pipeline.log_events_to_db()

        return jsonify({
            "exam_id": exam_id,
            "vad_score": result["vad_score"],
            "background_speech_detected": result["background_speech_detected"],
            "background_speech_confidence": result["background_speech_confidence"],
            "multiple_voices_detected": result["multiple_voices_detected"],
            "speaker_count": result["speaker_count"],
            "multiple_voices_confidence": result["multiple_voices_confidence"],
            "events": result["events"],
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/exams/<exam_id>/analyze-buffer", methods=["GET"])
def analyze_buffer(exam_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Analyze the current audio buffer for detailed statistics.

    Returns:
        JSON with buffer analysis
    """
    try:
        pipeline = get_pipeline(exam_id)
        result = pipeline.analyze_buffer()

        return jsonify({
            "exam_id": exam_id,
            **result,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/exams/<exam_id>/statistics", methods=["GET"])
def get_statistics(exam_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get statistics for exam.

    Returns:
        JSON with statistics
    """
    try:
        pipeline = get_pipeline(exam_id)
        stats = pipeline._calculate_statistics()

        return jsonify({
            "exam_id": exam_id,
            "statistics": stats,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/exams/<exam_id>/events", methods=["GET"])
def get_events(exam_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get events from database.

    Query parameters:
    - event_type: Optional event type filter
    - limit: Maximum number of events (default: 100)

    Returns:
        JSON with events
    """
    try:
        event_type = request.args.get("event_type", None)
        limit = int(request.args.get("limit", 100))

        pipeline = get_pipeline(exam_id)
        events = pipeline.get_events_from_db(event_type)

        return jsonify({
            "exam_id": exam_id,
            "event_type_filter": event_type,
            "events": events[:limit],
            "count": len(events[:limit]),
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/exams/<exam_id>/reset", methods=["POST"])
def reset_analysis(exam_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Reset analysis for exam.

    Returns:
        JSON confirmation
    """
    try:
        if exam_id in pipelines:
            pipelines[exam_id].reset()

        return jsonify({
            "exam_id": exam_id,
            "status": "reset",
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/exams/<exam_id>/shutdown", methods=["POST"])
def shutdown_analysis(exam_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Shutdown analysis for exam and cleanup.

    Returns:
        JSON confirmation
    """
    try:
        if exam_id in pipelines:
            pipeline = pipelines[exam_id]
            pipeline.log_statistics_to_db()
            pipeline.shutdown()
            del pipelines[exam_id]

        return jsonify({
            "exam_id": exam_id,
            "status": "shutdown",
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _extract_audio_data(req) -> Optional[np.ndarray]:
    """
    Extract audio data from request.

    Supports:
    - WAV file (audio/wav)
    - Base64 encoded audio in JSON

    Args:
        req: Flask request object

    Returns:
        Audio data as numpy array or None if invalid
    """
    try:
        # Try to read as WAV file
        if request.content_type and "audio/wav" in request.content_type:
            import scipy.io.wavfile as wavfile

            audio_file = io.BytesIO(request.data)
            sample_rate, audio_data = wavfile.read(audio_file)

            # Resample if necessary
            if sample_rate != SAMPLE_RATE:
                import librosa
                audio_data = librosa.resample(
                    audio_data.astype(np.float32), orig_sr=sample_rate, target_sr=SAMPLE_RATE
                )

            return audio_data.astype(np.float32)

        # Try to read as JSON with base64 encoded audio
        if request.is_json:
            import base64
            data = request.get_json()

            if "audio_base64" in data:
                audio_bytes = base64.b64decode(data["audio_base64"])
                audio_file = io.BytesIO(audio_bytes)

                import scipy.io.wavfile as wavfile
                sample_rate, audio_data = wavfile.read(audio_file)

                # Resample if necessary
                if sample_rate != SAMPLE_RATE:
                    import librosa
                    audio_data = librosa.resample(
                        audio_data.astype(np.float32),
                        orig_sr=sample_rate,
                        target_sr=SAMPLE_RATE,
                    )

                return audio_data.astype(np.float32)

        return None

    except Exception as e:
        print(f"Error extracting audio: {e}")
        return None


def run_server(host: str = HOST, port: int = PORT, debug: bool = DEBUG):
    """
    Run Flask server.

    Args:
        host: Host address
        port: Port number
        debug: Debug mode
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_server()
