"""
VOXOPS AI Gateway — Voice Query Endpoint

POST /voice-query
  Accepts audio (file upload) or text, runs STT if needed,
  and returns a JSON response with transcript + system reply.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from configs.logging_config import get_logger
from src.voxops.database.db import get_db

log = get_logger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

class VoiceQueryResponse(BaseModel):
    transcript: str
    intent: str | None = None
    response_text: str
    audio_url: str | None = None


# ---------------------------------------------------------------------------
# POST /voice-query
# ---------------------------------------------------------------------------

@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query(
    audio: Optional[UploadFile] = File(None, description="Audio file (WAV/MP3)"),
    text: Optional[str] = Form(None, description="Text query (alternative to audio)"),
    db: Session = Depends(get_db),
):
    """
    Accept a voice query (audio file **or** text) and return a response.

    Pipeline (Phase 7 will add orchestrator integration):
      1. STT transcription (if audio provided)
      2. Intent detection (stub — always returns 'general')
      3. Response generation (stub — echoes transcript)
    """
    if audio is None and text is None:
        raise HTTPException(status_code=400, detail="Provide either 'audio' file or 'text' form field.")

    transcript = text or ""

    # --- STT (if audio file provided) ---
    if audio is not None:
        try:
            from src.voxops.voice.stt.whisper_engine import transcribe_audio

            # Write uploaded bytes to a temporary file for Whisper
            suffix = Path(audio.filename).suffix if audio.filename else ".wav"
            raw = await audio.read()
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(raw)
                tmp_path = tmp.name

            log.info("Transcribing uploaded audio ({} bytes)", len(raw))
            result = transcribe_audio(tmp_path)
            transcript = result.get("text", "")
            log.info("Transcript: {}", transcript[:120])

            # Cleanup
            Path(tmp_path).unlink(missing_ok=True)
        except ImportError:
            log.warning("Whisper not available — falling back to empty transcript.")
        except Exception as exc:
            log.error("STT failed: {}", exc)
            raise HTTPException(status_code=500, detail=f"Speech-to-text failed: {exc}")

    if not transcript.strip():
        raise HTTPException(status_code=400, detail="Could not extract any text from the input.")

    # --- Intent detection (stub for Phase 7) ---
    intent = "general"

    # --- Response generation (stub for Phase 7) ---
    response_text = f"Received your query: '{transcript}'. Full AI processing will be available after Phase 7."

    return VoiceQueryResponse(
        transcript=transcript,
        intent=intent,
        response_text=response_text,
        audio_url=None,
    )
