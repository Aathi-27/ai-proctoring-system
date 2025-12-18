import time
import numpy as np
import cv2
import asyncio
from statistics import mean, median, stdev
from app.services.face_detection import FaceDetectionService
from app.services.liveness_detection import LivenessDetectionService
from app.utils.image_processing import validate_image_format


def generate_test_image(size=(480, 640)):
    image = np.random.randint(0, 255, (*size, 3), dtype=np.uint8)
    cv2.rectangle(image, (200, 100), (440, 380), (255, 255, 255), -1)
    cv2.circle(image, (270, 200), 15, (0, 0, 0), -1)
    cv2.circle(image, (370, 200), 15, (0, 0, 0), -1)
    cv2.ellipse(image, (320, 300), (40, 20), 0, 0, 180, (0, 0, 0), 2)
    return image


async def benchmark_face_detection(num_iterations=100):
    print("=" * 60)
    print("Face Detection Performance Benchmark")
    print("=" * 60)
    
    service = FaceDetectionService()
    image = generate_test_image()
    
    latencies = []
    
    print(f"\nRunning {num_iterations} iterations...")
    
    for i in range(num_iterations):
        start_time = time.time()
        face_count, confidences, landmarks, bbox = service.detect_faces(image)
        latency = (time.time() - start_time) * 1000
        latencies.append(latency)
        
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_iterations}")
    
    print(f"\nResults:")
    print(f"  Total iterations: {num_iterations}")
    print(f"  Mean latency: {mean(latencies):.2f} ms")
    print(f"  Median latency: {median(latencies):.2f} ms")
    print(f"  Min latency: {min(latencies):.2f} ms")
    print(f"  Max latency: {max(latencies):.2f} ms")
    print(f"  Std deviation: {stdev(latencies):.2f} ms")
    print(f"  95th percentile: {sorted(latencies)[int(num_iterations * 0.95)]:.2f} ms")
    print(f"  99th percentile: {sorted(latencies)[int(num_iterations * 0.99)]:.2f} ms")
    
    target_latency = 500
    success_rate = (sum(1 for l in latencies if l < target_latency) / num_iterations) * 100
    print(f"\n  Success rate (<{target_latency}ms): {success_rate:.1f}%")
    
    fps = 1000 / mean(latencies)
    print(f"  Estimated FPS: {fps:.1f}")
    
    return latencies


async def benchmark_liveness_detection(num_iterations=100):
    print("\n" + "=" * 60)
    print("Liveness Detection Performance Benchmark")
    print("=" * 60)
    
    face_service = FaceDetectionService()
    liveness_service = LivenessDetectionService()
    image = generate_test_image()
    
    face_count, confidences, landmarks, bbox = face_service.detect_faces(image)
    
    if not landmarks or len(landmarks) == 0:
        print("No face detected, using sample landmarks")
        landmarks = [[]]
        for i in range(468):
            x = 0.3 + (i % 20) * 0.02
            y = 0.3 + (i // 20) * 0.02
            z = 0.0
            landmarks[0].append([x, y, z])
    
    blink_latencies = []
    movement_latencies = []
    score_latencies = []
    
    print(f"\nRunning {num_iterations} iterations...")
    
    exam_id = "benchmark_exam"
    
    for i in range(num_iterations):
        if landmarks and len(landmarks) > 0:
            left_eye, right_eye = face_service.extract_eye_landmarks(landmarks[0])
            
            start_time = time.time()
            liveness_service.detect_blink(exam_id, left_eye, right_eye)
            blink_latency = (time.time() - start_time) * 1000
            blink_latencies.append(blink_latency)
            
            head_pose = face_service.calculate_head_pose(landmarks[0], image.shape)
            start_time = time.time()
            liveness_service.detect_movement(exam_id, head_pose)
            movement_latency = (time.time() - start_time) * 1000
            movement_latencies.append(movement_latency)
            
            start_time = time.time()
            liveness_service.calculate_liveness_score(exam_id)
            score_latency = (time.time() - start_time) * 1000
            score_latencies.append(score_latency)
        
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_iterations}")
    
    print(f"\nBlink Detection:")
    print(f"  Mean latency: {mean(blink_latencies):.2f} ms")
    print(f"  Median latency: {median(blink_latencies):.2f} ms")
    
    print(f"\nMovement Detection:")
    print(f"  Mean latency: {mean(movement_latencies):.2f} ms")
    print(f"  Median latency: {median(movement_latencies):.2f} ms")
    
    print(f"\nLiveness Score Calculation:")
    print(f"  Mean latency: {mean(score_latencies):.2f} ms")
    print(f"  Median latency: {median(score_latencies):.2f} ms")
    
    total_latency = mean(blink_latencies) + mean(movement_latencies) + mean(score_latencies)
    print(f"\nTotal liveness processing: {total_latency:.2f} ms")
    
    liveness_service.clear_history(exam_id)


async def benchmark_end_to_end(num_iterations=50):
    print("\n" + "=" * 60)
    print("End-to-End Pipeline Benchmark")
    print("=" * 60)
    
    face_service = FaceDetectionService()
    liveness_service = LivenessDetectionService()
    image = generate_test_image()
    
    total_latencies = []
    
    print(f"\nRunning {num_iterations} iterations...")
    
    exam_id = "benchmark_e2e"
    
    for i in range(num_iterations):
        start_time = time.time()
        
        face_count, confidences, landmarks, bbox = face_service.detect_faces(image)
        
        if landmarks and len(landmarks) > 0:
            left_eye, right_eye = face_service.extract_eye_landmarks(landmarks[0])
            liveness_service.detect_blink(exam_id, left_eye, right_eye)
            
            head_pose = face_service.calculate_head_pose(landmarks[0], image.shape)
            liveness_service.detect_movement(exam_id, head_pose)
            
            liveness_service.calculate_liveness_score(exam_id)
        
        total_latency = (time.time() - start_time) * 1000
        total_latencies.append(total_latency)
        
        if (i + 1) % 10 == 0:
            print(f"Progress: {i + 1}/{num_iterations}")
    
    print(f"\nResults:")
    print(f"  Mean latency: {mean(total_latencies):.2f} ms")
    print(f"  Median latency: {median(total_latencies):.2f} ms")
    print(f"  Min latency: {min(total_latencies):.2f} ms")
    print(f"  Max latency: {max(total_latencies):.2f} ms")
    print(f"  95th percentile: {sorted(total_latencies)[int(num_iterations * 0.95)]:.2f} ms")
    
    target_latency = 500
    success_rate = (sum(1 for l in total_latencies if l < target_latency) / num_iterations) * 100
    print(f"\n  Success rate (<{target_latency}ms): {success_rate:.1f}%")
    
    fps = 1000 / mean(total_latencies)
    print(f"  Estimated FPS: {fps:.1f}")
    
    liveness_service.clear_history(exam_id)


async def main():
    print("\n" + "=" * 60)
    print("Face Detection & Liveness Pipeline Benchmark")
    print("=" * 60)
    print("\nThis benchmark measures the performance of:")
    print("  1. Face detection (MediaPipe)")
    print("  2. Liveness detection (blink + movement)")
    print("  3. End-to-end pipeline")
    print("\nTarget: <500ms latency per frame")
    print("=" * 60)
    
    await benchmark_face_detection(100)
    await benchmark_liveness_detection(100)
    await benchmark_end_to_end(50)
    
    print("\n" + "=" * 60)
    print("Benchmark completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
