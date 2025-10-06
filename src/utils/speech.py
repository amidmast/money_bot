import os
from typing import List, Optional

from google.cloud import speech_v1p1beta1 as speech
import subprocess
import tempfile


def get_speech_client() -> speech.SpeechClient:
    # GOOGLE_APPLICATION_CREDENTIALS already points to /app/credentials.json
    return speech.SpeechClient()


def _transcode_to_linear16(audio_bytes: bytes) -> Optional[bytes]:
    """Transcode input OGG/OPUS bytes to 16kHz mono LINEAR16 WAV using ffmpeg.

    Returns WAV bytes or None if transcode fails.
    """
    if not audio_bytes:
        return None

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=True) as in_file, \
         tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as out_file:
        in_file.write(audio_bytes)
        in_file.flush()
        cmd = [
            "ffmpeg",
            "-y",
            "-i", in_file.name,
            "-ac", "1",
            "-ar", "16000",
            "-f", "wav",
            out_file.name,
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            out_file.flush()
            out_file.seek(0)
            return out_file.read()
        except Exception:
            return None


def transcribe_bytes(audio_bytes: bytes, languages: List[str], target_language: str = "ru-RU") -> Optional[str]:
    """Transcribe audio bytes with Google Cloud Speech.

    languages: list of BCP-47 codes (e.g., ["ru-RU", "en-US", "uk-UA"]).
    target_language: currently unused for translation, but kept for future post-processing.
    """
    if not audio_bytes:
        return None

    client = get_speech_client()

    # Prefer transcoding to LINEAR16/16k for consistent STT results
    wav_bytes = _transcode_to_linear16(audio_bytes)
    if wav_bytes:
        audio = speech.RecognitionAudio(content=wav_bytes)
        config = speech.RecognitionConfig(
            enable_automatic_punctuation=True,
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=languages[0] if languages else "ru-RU",
            alternative_language_codes=languages[1:] if languages and len(languages) > 1 else [],
            model="latest_long",
        )
    else:
        # Fallback to raw OGG_OPUS if transcoding failed
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            enable_automatic_punctuation=True,
            encoding=speech.RecognitionConfig.AudioEncoding.OGG_OPUS,
            language_code=languages[0] if languages else "ru-RU",
            alternative_language_codes=languages[1:] if languages and len(languages) > 1 else [],
            model="latest_long",
        )

    response = client.recognize(config=config, audio=audio)
    # Prefer the first alternative of the first result
    for result in response.results:
        if result.alternatives:
            text = result.alternatives[0].transcript.strip()
            if text:
                return text
    return None


