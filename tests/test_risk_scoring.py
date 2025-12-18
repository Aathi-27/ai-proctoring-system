import pytest
from datetime import datetime, timedelta
from app.services.risk_scoring import RiskScoringEngine
from app.models.events import DetectionEvent, EventType
from app.database.mongodb import MongoDB, get_database
import math


@pytest.fixture
def risk_engine():
    return RiskScoringEngine()


@pytest.fixture
async def setup_test_db(test_db):
    MongoDB.database = test_db
    await test_db.detection_events.delete_many({})
    await test_db.risk_score_history.delete_many({})
    yield test_db
    await test_db.detection_events.delete_many({})
    await test_db.risk_score_history.delete_many({})


class TestTimeDecay:
    def test_time_decay_at_zero_minutes(self, risk_engine, current_time):
        decay = risk_engine.calculate_time_decay(current_time, current_time)
        assert decay == 1.0
    
    def test_time_decay_at_window_end(self, risk_engine, current_time):
        event_time = current_time - timedelta(minutes=5)
        decay = risk_engine.calculate_time_decay(event_time, current_time)
        assert decay == pytest.approx(math.exp(-0.5), rel=1e-5)
    
    def test_time_decay_beyond_window(self, risk_engine, current_time):
        event_time = current_time - timedelta(minutes=6)
        decay = risk_engine.calculate_time_decay(event_time, current_time)
        assert decay == 0.0
    
    def test_time_decay_future_event(self, risk_engine, current_time):
        future_time = current_time + timedelta(minutes=1)
        decay = risk_engine.calculate_time_decay(future_time, current_time)
        assert decay == 1.0


class TestEventWeights:
    def test_get_mobile_detected_weight(self, risk_engine):
        weight = risk_engine.get_event_weight("MOBILE_DETECTED")
        assert weight == 25
    
    def test_get_multiple_persons_weight(self, risk_engine):
        weight = risk_engine.get_event_weight("MULTIPLE_PERSONS")
        assert weight == 30
    
    def test_get_face_not_detected_weight(self, risk_engine):
        weight = risk_engine.get_event_weight("FACE_NOT_DETECTED")
        assert weight == 20
    
    def test_get_tab_switched_weight(self, risk_engine):
        weight = risk_engine.get_event_weight("TAB_SWITCHED")
        assert weight == 10
    
    def test_get_unknown_event_weight(self, risk_engine):
        weight = risk_engine.get_event_weight("UNKNOWN_EVENT")
        assert weight == 0


class TestContributionCalculation:
    def test_full_confidence_no_decay(self, risk_engine, current_time):
        event = DetectionEvent(
            exam_id="exam_1",
            session_id="session_1",
            event_type=EventType.MOBILE_DETECTED,
            confidence=1.0,
            timestamp=current_time
        )
        contribution = risk_engine.calculate_contribution(event, current_time)
        
        assert contribution.event == "MOBILE_DETECTED"
        assert contribution.confidence == 1.0
        assert contribution.weight == 25
        assert contribution.contribution == 25.0
    
    def test_partial_confidence(self, risk_engine, current_time):
        event = DetectionEvent(
            exam_id="exam_1",
            session_id="session_1",
            event_type=EventType.MOBILE_DETECTED,
            confidence=0.8,
            timestamp=current_time
        )
        contribution = risk_engine.calculate_contribution(event, current_time)
        
        assert contribution.contribution == 20.0
    
    def test_with_time_decay(self, risk_engine, current_time):
        event_time = current_time - timedelta(minutes=2.5)
        event = DetectionEvent(
            exam_id="exam_1",
            session_id="session_1",
            event_type=EventType.MOBILE_DETECTED,
            confidence=1.0,
            timestamp=event_time
        )
        contribution = risk_engine.calculate_contribution(event, current_time)
        
        expected_decay = math.exp(-0.5 * (2.5 / 5.0))
        expected_contribution = 25.0 * expected_decay
        
        assert contribution.contribution == pytest.approx(expected_contribution, rel=1e-2)


@pytest.mark.asyncio
class TestRiskScoreComputation:
    async def test_zero_events(self, risk_engine, setup_test_db, sample_exam_id, sample_session_id, current_time):
        risk_score = await risk_engine.compute_risk_score(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            current_time=current_time
        )
        
        assert risk_score.score == 0.0
        assert risk_score.risk_level == "Low"
        assert len(risk_score.contribution_breakdown) == 0
    
    async def test_single_event(self, risk_engine, setup_test_db, sample_exam_id, sample_session_id, current_time):
        event = DetectionEvent(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            event_type=EventType.MOBILE_DETECTED,
            confidence=1.0,
            timestamp=current_time
        )
        await risk_engine.save_detection_event(event)
        
        risk_score = await risk_engine.compute_risk_score(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            current_time=current_time
        )
        
        assert risk_score.score == 25.0
        assert risk_score.risk_level == "Low"
        assert len(risk_score.contribution_breakdown) == 1
    
    async def test_multiple_events_accumulation(self, risk_engine, setup_test_db, sample_exam_id, sample_session_id, current_time):
        events = [
            DetectionEvent(
                exam_id=sample_exam_id,
                session_id=sample_session_id,
                event_type=EventType.MOBILE_DETECTED,
                confidence=0.95,
                timestamp=current_time
            ),
            DetectionEvent(
                exam_id=sample_exam_id,
                session_id=sample_session_id,
                event_type=EventType.TAB_SWITCHED,
                confidence=1.0,
                timestamp=current_time
            ),
        ]
        
        for event in events:
            await risk_engine.save_detection_event(event)
        
        risk_score = await risk_engine.compute_risk_score(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            current_time=current_time
        )
        
        expected_score = (0.95 * 25) + (1.0 * 10)
        assert risk_score.score == pytest.approx(expected_score, rel=1e-2)
        assert len(risk_score.contribution_breakdown) == 2
    
    async def test_score_bounded_at_100(self, risk_engine, setup_test_db, sample_exam_id, sample_session_id, current_time):
        events = [
            DetectionEvent(
                exam_id=sample_exam_id,
                session_id=sample_session_id,
                event_type=EventType.MULTIPLE_PERSONS,
                confidence=1.0,
                timestamp=current_time
            ),
            DetectionEvent(
                exam_id=sample_exam_id,
                session_id=sample_session_id,
                event_type=EventType.MOBILE_DETECTED,
                confidence=1.0,
                timestamp=current_time
            ),
            DetectionEvent(
                exam_id=sample_exam_id,
                session_id=sample_session_id,
                event_type=EventType.TABLET_DETECTED,
                confidence=1.0,
                timestamp=current_time
            ),
            DetectionEvent(
                exam_id=sample_exam_id,
                session_id=sample_session_id,
                event_type=EventType.FACE_NOT_DETECTED,
                confidence=1.0,
                timestamp=current_time
            ),
        ]
        
        for event in events:
            await risk_engine.save_detection_event(event)
        
        risk_score = await risk_engine.compute_risk_score(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            current_time=current_time
        )
        
        assert risk_score.score <= 100.0
        assert risk_score.score == 100.0
    
    async def test_events_outside_window_ignored(self, risk_engine, setup_test_db, sample_exam_id, sample_session_id, current_time):
        old_event = DetectionEvent(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            event_type=EventType.MOBILE_DETECTED,
            confidence=1.0,
            timestamp=current_time - timedelta(minutes=10)
        )
        await risk_engine.save_detection_event(old_event)
        
        recent_event = DetectionEvent(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            event_type=EventType.TAB_SWITCHED,
            confidence=1.0,
            timestamp=current_time
        )
        await risk_engine.save_detection_event(recent_event)
        
        risk_score = await risk_engine.compute_risk_score(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            current_time=current_time
        )
        
        assert risk_score.score == 10.0
        assert len(risk_score.contribution_breakdown) == 1


class TestRiskLevels:
    def test_low_risk_level(self):
        from app.models.events import RiskScore
        assert RiskScore.get_risk_level(0) == "Low"
        assert RiskScore.get_risk_level(15) == "Low"
        assert RiskScore.get_risk_level(30) == "Low"
    
    def test_medium_risk_level(self):
        from app.models.events import RiskScore
        assert RiskScore.get_risk_level(31) == "Medium"
        assert RiskScore.get_risk_level(45) == "Medium"
        assert RiskScore.get_risk_level(60) == "Medium"
    
    def test_high_risk_level(self):
        from app.models.events import RiskScore
        assert RiskScore.get_risk_level(61) == "High"
        assert RiskScore.get_risk_level(75) == "High"
        assert RiskScore.get_risk_level(85) == "High"
    
    def test_critical_risk_level(self):
        from app.models.events import RiskScore
        assert RiskScore.get_risk_level(86) == "Critical"
        assert RiskScore.get_risk_level(95) == "Critical"
        assert RiskScore.get_risk_level(100) == "Critical"


@pytest.mark.asyncio
class TestRiskScorePersistence:
    async def test_save_risk_score(self, risk_engine, setup_test_db, sample_exam_id, sample_session_id, current_time):
        event = DetectionEvent(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            event_type=EventType.MOBILE_DETECTED,
            confidence=1.0,
            timestamp=current_time
        )
        await risk_engine.save_detection_event(event)
        
        risk_score = await risk_engine.compute_risk_score(
            exam_id=sample_exam_id,
            session_id=sample_session_id,
            current_time=current_time
        )
        
        saved_score = await setup_test_db.risk_score_history.find_one({
            "exam_id": sample_exam_id,
            "session_id": sample_session_id
        })
        
        assert saved_score is not None
        assert saved_score["score"] == risk_score.score
        assert saved_score["risk_level"] == risk_score.risk_level
    
    async def test_get_risk_timeline(self, risk_engine, setup_test_db, sample_exam_id, sample_session_id, current_time):
        for i in range(3):
            event = DetectionEvent(
                exam_id=sample_exam_id,
                session_id=sample_session_id,
                event_type=EventType.TAB_SWITCHED,
                confidence=1.0,
                timestamp=current_time + timedelta(minutes=i)
            )
            await risk_engine.save_detection_event(event)
            await risk_engine.compute_risk_score(
                exam_id=sample_exam_id,
                session_id=sample_session_id,
                current_time=current_time + timedelta(minutes=i)
            )
        
        timeline = await risk_engine.get_risk_timeline(
            exam_id=sample_exam_id,
            session_id=sample_session_id
        )
        
        assert len(timeline) == 3
        assert all(score.exam_id == sample_exam_id for score in timeline)


class TestAlertLevels:
    def test_green_alert(self, risk_engine):
        assert risk_engine.get_alert_level(0) == "green"
        assert risk_engine.get_alert_level(30) == "green"
        assert risk_engine.get_alert_level(49) == "green"
    
    def test_yellow_alert(self, risk_engine):
        assert risk_engine.get_alert_level(50) == "yellow"
        assert risk_engine.get_alert_level(60) == "yellow"
        assert risk_engine.get_alert_level(74) == "yellow"
    
    def test_red_alert(self, risk_engine):
        assert risk_engine.get_alert_level(75) == "red"
        assert risk_engine.get_alert_level(85) == "red"
        assert risk_engine.get_alert_level(100) == "red"
