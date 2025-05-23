# Services package for face detection and recognition
from app.services.face_detection import (
    detect_faces,
    FaceDetectionError,
    MultipleFacesError,
    ImageQualityError
)