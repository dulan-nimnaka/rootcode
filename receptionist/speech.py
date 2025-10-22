def speech_to_text(audio_blob: bytes) -> str:
    """Stub: convert audio blob to text. In demo, we'll accept raw text instead.

    In production, plug in a proper STT engine (Google, Azure, Vosk, etc.).
    """
    try:
        return audio_blob.decode('utf-8')
    except Exception:
        return ""

def text_to_speech(text: str) -> bytes:
    """Stub: return a bytes payload representing audio.

    In production, integrate TTS (local or cloud) and stream audio to speakers.
    """
    return text.encode('utf-8')
