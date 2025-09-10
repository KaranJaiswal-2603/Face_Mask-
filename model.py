import face_recognition

def get_face_encodings(image):
    """
    Input: RGB image as numpy array
    Output: List of face encodings detected in image
    """
    face_locations = face_recognition.face_locations(image)
    encodings = face_recognition.face_encodings(image, face_locations)
    return encodings

def compare_faces(known_encodings, face_encoding_to_check, tolerance=0.6):
    """
    Input:
    - known_encodings: list of saved face encodings
    - face_encoding_to_check: face encoding to compare
    - tolerance: threshold for matching

    Output:
    - list of booleans indicating matches
    """
    matches = face_recognition.compare_faces(known_encodings, face_encoding_to_check, tolerance)
    return matches
