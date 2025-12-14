import time
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from app.models.events import FrameAnalysisRequest, FrameAnalysisResponse
from app.services.face_detection import FaceDetectionService
from app.services.liveness_detection import LivenessDetectionService
from app.services.event_manager import EventManager
from app.utils.image_processing import decode_base64_image, validate_image_format

router = APIRouter()

face_detection_service = FaceDetectionService()
liveness_detection_service = LivenessDetectionService()
event_manager = EventManager()


@router.post("/exams/{exam_id}/analyze-frame", response_model=FrameAnalysisResponse)
async def analyze_frame(exam_id: str, request: FrameAnalysisRequest):
    start_time = time.time()
    
    try:
        image = decode_base64_image(request.frame_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode image: {str(e)}")
    
    is_valid, message = validate_image_format(image)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    face_count, confidences, all_landmarks, bounding_box = face_detection_service.detect_faces(image)
    
    events = []
    liveness_score = 0.0
    is_live = False
    head_pose = None
    
    if face_count == 0:
        event = await event_manager.emit_face_not_detected(exam_id)
        if event:
            events.append(event.event_type)
    elif face_count == 1:
        await event_manager.emit_face_detected(
            exam_id=exam_id,
            face_count=face_count,
            confidence=confidences[0],
            landmarks=all_landmarks,
            bounding_box=bounding_box
        )
        events.append("FACE_DETECTED")
        
        if all_landmarks and len(all_landmarks) > 0:
            landmarks = all_landmarks[0]
            
            left_eye, right_eye = face_detection_service.extract_eye_landmarks(landmarks)
            
            blink_detected, ear, eye_type = liveness_detection_service.detect_blink(
                exam_id, left_eye, right_eye
            )
            
            if blink_detected:
                await event_manager.emit_blink_detected(exam_id, ear, eye_type)
                events.append("BLINK_DETECTED")
            
            head_pose = face_detection_service.calculate_head_pose(landmarks, image.shape)
            
            movement_detected, pose_change = liveness_detection_service.detect_movement(
                exam_id, head_pose
            )
            
            if movement_detected:
                await event_manager.emit_movement_detected(exam_id, pose_change)
                events.append("MOVEMENT_DETECTED")
            
            liveness_score, blink_count, movement_count, is_live = \
                liveness_detection_service.calculate_liveness_score(exam_id)
            
            await event_manager.emit_liveness_score(
                exam_id, liveness_score, blink_count, movement_count, is_live
            )
            events.append("LIVENESS_SCORE")
    else:
        await event_manager.emit_multiple_persons(exam_id, face_count, confidences)
        events.append("MULTIPLE_PERSONS")
    
    processing_time_ms = (time.time() - start_time) * 1000
    
    landmarks_68 = []
    if all_landmarks and len(all_landmarks) > 0:
        for face_landmarks in all_landmarks:
            outline = face_detection_service.extract_face_outline_landmarks(face_landmarks)
            landmarks_68.append(outline)
    
    return FrameAnalysisResponse(
        face_count=face_count,
        landmarks=landmarks_68,
        liveness_score=liveness_score,
        is_live=is_live,
        events=events,
        confidence_scores=confidences,
        head_pose=head_pose,
        processing_time_ms=processing_time_ms
    )


@router.get("/exams/{exam_id}/events")
async def get_exam_events(exam_id: str, event_type: str = None, limit: int = 100):
    events = await event_manager.get_events(exam_id, event_type, limit)
    return {"exam_id": exam_id, "events": events, "count": len(events)}


@router.delete("/exams/{exam_id}/clear-history")
async def clear_exam_history(exam_id: str):
    liveness_detection_service.clear_history(exam_id)
    if exam_id in event_manager.face_not_detected_start:
        del event_manager.face_not_detected_start[exam_id]
    return {"message": f"History cleared for exam {exam_id}"}


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "face_detection": "active",
            "liveness_detection": "active",
            "event_manager": "active"
        }
    }
