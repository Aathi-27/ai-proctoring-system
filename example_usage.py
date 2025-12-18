import asyncio
from datetime import datetime, timedelta
from app.models.events import DetectionEvent, EventType
from app.services.risk_scoring import RiskScoringEngine
from app.database.mongodb import connect_to_mongo, close_mongo_connection


async def example_scenario():
    print("=" * 80)
    print("Exam Proctoring Risk Scoring Engine - Example Scenarios")
    print("=" * 80)
    
    await connect_to_mongo()
    
    engine = RiskScoringEngine()
    exam_id = "demo_exam_001"
    session_id = "demo_session_001"
    current_time = datetime.utcnow()
    
    print("\n" + "=" * 80)
    print("SCENARIO 1: Single Phone Detection")
    print("=" * 80)
    
    event1 = DetectionEvent(
        exam_id=exam_id,
        session_id=session_id,
        event_type=EventType.MOBILE_DETECTED,
        confidence=0.95,
        timestamp=current_time
    )
    await engine.save_detection_event(event1)
    
    risk_score = await engine.compute_risk_score(exam_id, session_id, current_time)
    print(f"\nEvent: {event1.event_type.value}")
    print(f"Confidence: {event1.confidence}")
    print(f"Weight: {engine.get_event_weight(event1.event_type.value)}")
    print(f"\nRisk Score: {risk_score.score}/100")
    print(f"Risk Level: {risk_score.risk_level}")
    print(f"Alert Level: {engine.get_alert_level(risk_score.score)}")
    
    print("\n" + "=" * 80)
    print("SCENARIO 2: Multiple Violations")
    print("=" * 80)
    
    exam_id_2 = "demo_exam_002"
    session_id_2 = "demo_session_002"
    
    events = [
        DetectionEvent(
            exam_id=exam_id_2,
            session_id=session_id_2,
            event_type=EventType.MOBILE_DETECTED,
            confidence=0.95,
            timestamp=current_time
        ),
        DetectionEvent(
            exam_id=exam_id_2,
            session_id=session_id_2,
            event_type=EventType.TAB_SWITCHED,
            confidence=1.0,
            timestamp=current_time
        ),
        DetectionEvent(
            exam_id=exam_id_2,
            session_id=session_id_2,
            event_type=EventType.FACE_NOT_DETECTED,
            confidence=0.85,
            timestamp=current_time - timedelta(minutes=1)
        ),
    ]
    
    for event in events:
        await engine.save_detection_event(event)
        print(f"\n- {event.event_type.value}")
        print(f"  Confidence: {event.confidence}")
        print(f"  Weight: {engine.get_event_weight(event.event_type.value)}")
    
    risk_score = await engine.compute_risk_score(exam_id_2, session_id_2, current_time)
    print(f"\nTotal Risk Score: {risk_score.score}/100")
    print(f"Risk Level: {risk_score.risk_level}")
    print(f"Alert Level: {engine.get_alert_level(risk_score.score)}")
    
    print("\nContribution Breakdown:")
    for contrib in risk_score.contribution_breakdown:
        print(f"  - {contrib.event}: {contrib.contribution:.2f} points")
        print(f"    (weight: {contrib.weight}, confidence: {contrib.confidence})")
    
    print("\n" + "=" * 80)
    print("SCENARIO 3: Time Decay Effect")
    print("=" * 80)
    
    exam_id_3 = "demo_exam_003"
    session_id_3 = "demo_session_003"
    
    old_event = DetectionEvent(
        exam_id=exam_id_3,
        session_id=session_id_3,
        event_type=EventType.MOBILE_DETECTED,
        confidence=1.0,
        timestamp=current_time - timedelta(minutes=4)
    )
    await engine.save_detection_event(old_event)
    
    recent_event = DetectionEvent(
        exam_id=exam_id_3,
        session_id=session_id_3,
        event_type=EventType.MOBILE_DETECTED,
        confidence=1.0,
        timestamp=current_time
    )
    await engine.save_detection_event(recent_event)
    
    risk_score = await engine.compute_risk_score(exam_id_3, session_id_3, current_time)
    
    print("\nTwo identical events (MOBILE_DETECTED, confidence=1.0):")
    for contrib in risk_score.contribution_breakdown:
        time_diff = (current_time - contrib.timestamp).total_seconds() / 60
        print(f"\n  Event at t-{time_diff:.1f} minutes:")
        print(f"    Contribution: {contrib.contribution:.2f} points")
        decay = contrib.contribution / 25.0
        print(f"    Decay factor: {decay:.2f}")
    
    print(f"\nTotal Risk Score: {risk_score.score}/100")
    print(f"Notice how the older event contributes less due to time decay!")
    
    print("\n" + "=" * 80)
    print("SCENARIO 4: Critical Risk Level")
    print("=" * 80)
    
    exam_id_4 = "demo_exam_004"
    session_id_4 = "demo_session_004"
    
    critical_events = [
        DetectionEvent(
            exam_id=exam_id_4,
            session_id=session_id_4,
            event_type=EventType.MULTIPLE_PERSONS,
            confidence=1.0,
            timestamp=current_time
        ),
        DetectionEvent(
            exam_id=exam_id_4,
            session_id=session_id_4,
            event_type=EventType.MOBILE_DETECTED,
            confidence=1.0,
            timestamp=current_time
        ),
        DetectionEvent(
            exam_id=exam_id_4,
            session_id=session_id_4,
            event_type=EventType.TABLET_DETECTED,
            confidence=0.9,
            timestamp=current_time
        ),
        DetectionEvent(
            exam_id=exam_id_4,
            session_id=session_id_4,
            event_type=EventType.MULTIPLE_VOICES,
            confidence=0.95,
            timestamp=current_time
        ),
    ]
    
    print("\nMultiple serious violations detected:")
    for event in critical_events:
        await engine.save_detection_event(event)
        weight = engine.get_event_weight(event.event_type.value)
        contrib = event.confidence * weight
        print(f"  - {event.event_type.value}: +{contrib:.1f} points")
    
    risk_score = await engine.compute_risk_score(exam_id_4, session_id_4, current_time)
    print(f"\nTotal Risk Score: {risk_score.score}/100 (capped at 100)")
    print(f"Risk Level: {risk_score.risk_level}")
    print(f"Alert Level: {engine.get_alert_level(risk_score.score)}")
    print("\n⚠️  CRITICAL ALERT - Immediate invigilator attention required!")
    
    await close_mongo_connection()
    
    print("\n" + "=" * 80)
    print("Example scenarios completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(example_scenario())
