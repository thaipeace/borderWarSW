"""
GATE 2: Multi-Speaker Character TTS Generation & Voice QA Script for Episode 01 (v6.0)
Uses Gemini 2.5 Flash Preview TTS (acting-aware Vietnamese neural speech synthesis)
with distinct voice profiles for the 3 archetypes:
  1. Người chài trẻ (Puck - young urgent Southern Vietnamese fisherman, breathless)
  2. Chỉ huy bộ đội / Người trực đêm (Fenrir - commanding, resolute Vietnamese officer)
  3. Lão chài (Charon - weathered, warm, elderly Southern Vietnamese fisherman)

Outputs 48kHz 16-bit mono WAV + 192kbps MP3 normalized to -3.0 dBFS peak,
using non-destructive numpy boundary detection (preserving all internal stop consonants
and pauses) and writes Gate 2 QA metrics to `audio/tts/tts_manifest_gate2.json`.
"""
from __future__ import annotations

import base64
import json
import math
import subprocess
import sys
import tempfile
import time
import urllib.request
import wave
from pathlib import Path

import numpy as np

HAIZFLOW_SRC = Path(r"C:\projects\HaizFlow-main\src")
if HAIZFLOW_SRC.is_dir():
    sys.path.insert(0, str(HAIZFLOW_SRC))

OUTPUT_DIR = Path(__file__).resolve().parent / "audio" / "tts"
FFMPEG_BIN = r"C:\projects\HaizFlow-main\runtime\bin\ffmpeg.exe"
if not Path(FFMPEG_BIN).is_file():
    FFMPEG_BIN = "ffmpeg"


def load_gemini_keys() -> list[str]:
    keys: list[str] = []
    keys_file = Path(r"C:\projects\HaizFlow-main\runtime\data\gemini-api-keys.json")
    if keys_file.is_file():
        try:
            data = json.loads(keys_file.read_text(encoding="utf-8"))
            raw_list = (
                (data.get("keys") or data.get("api_keys") or [])
                if isinstance(data, dict)
                else (data if isinstance(data, list) else [])
            )
            for item in raw_list:
                if isinstance(item, str) and item.strip():
                    keys.append(item.strip())
                elif isinstance(item, dict) and item.get("key"):
                    keys.append(str(item["key"]).strip())
        except Exception:
            pass
    try:
        from haizflow.services.image_generator import get_effective_gemini_api_key

        eff = get_effective_gemini_api_key()
        if eff and eff not in keys:
            keys.insert(0, eff)
    except Exception:
        pass
    return keys


DIALOGUE_ITEMS = [
    {
        "line_id": "line1_beat3_nguoi_chai_tre",
        "beat_id": 3,
        "speaker": "nguoi_chai_tre",
        "character_label": "Người chài trẻ (24 tuổi - Nam Bộ, thở dốc, hối hả cấp báo trong đêm)",
        "voice_name": "Puck",
        "timeline_start_sec": 22.5,
        "timeline_window_sec": 4.8,
        "full_text": "Tàu lạ đổ bộ bãi cát... quân đông lắm, báo gấp!",
        "tts_prompt": (
            "Hãy đóng vai một thanh niên ngư dân miền Tây Nam Bộ 24 tuổi vừa chạy bộ băng rừng trong đêm, "
            "giọng miền Nam thở dốc, hối hả, khẩn trương cấp báo. Chỉ đọc đúng câu thoại trong ngoặc kép "
            "(ngắt nhịp lấy hơi ngắn ở dấu ba chấm, phát âm rõ chữ cuối 'báo gấp!'):\n"
            '"Tàu lạ đổ bộ bãi cát... quân đông lắm, báo gấp!"'
        ),
        "ffmpeg_af": (
            "highpass=f=90,"
            "equalizer=f=2800:width_type=o:width=1.2:g=2.5,"
            "acompressor=threshold=-18dB:ratio=2.5:attack=8:release=90:makeup=2dB"
        ),
    },
    {
        "line_id": "line2_beat4_nguoi_truc_dem",
        "beat_id": 4,
        "speaker": "nguoi_truc_dem",
        "character_label": "Chỉ huy bộ đội / Người trực đêm (29 tuổi - Đanh gọn, chủ động, uy lực)",
        "voice_name": "Fenrir",
        "timeline_start_sec": 41.0,
        "timeline_window_sec": 3.0,
        "full_text": "Chúng hết đường rồi!",
        "tts_prompt": (
            "Hãy đóng vai một nam sĩ quan chỉ huy bộ đội Việt Nam 29 tuổi, "
            "giọng miền Nam đanh thép, dứt khoát, chủ động làm chủ thế trận. "
            "Đọc rõ ràng, tròn vành rõ chữ cả 4 từ, ngân rõ chữ cuối 'rồi!' trước khi dứt "
            "(chỉ đọc đúng câu trong ngoặc kép):\n"
            '"Chúng hết đường rồi! ..."'
        ),
        "force_resynthesize": False,
        "ffmpeg_af": (
            "highpass=f=75,"
            "equalizer=f=160:width_type=o:width=1.0:g=3.0,"
            "equalizer=f=3000:width_type=o:width=1.0:g=2.5,"
            "acompressor=threshold=-16dB:ratio=3.0:attack=6:release=100:makeup=2.5dB"
        ),
    },
    {
        "line_id": "line3_beat5_lao_chai",
        "beat_id": 5,
        "speaker": "lao_chai",
        "character_label": "Lão chài (55 tuổi - Nam Bộ trầm ấm, từng trải, nhẹ nhõm lúc bình minh)",
        "voice_name": "Charon",
        "timeline_start_sec": 50.5,
        "timeline_window_sec": 5.0,
        "full_text": "Hòn đảo của mình... sóng lại êm rồi.",
        "tts_prompt": (
            "Hãy đóng vai một ông lão ngư dân miền Tây Nam Bộ khoảng 55 tuổi, "
            "giọng miền Nam trầm ấm, dày, từng trải sương gió, nhịp đọc chậm rãi, sâu lắng và nhẹ nhõm "
            "khi nhìn biển bình yên lúc bình minh. Chỉ đọc đúng câu thoại trong ngoặc kép "
            "(ngắt nhịp khoảng nửa giây ở dấu ba chấm):\n"
            '"Hòn đảo của mình... sóng lại êm rồi."'
        ),
        "ffmpeg_af": (
            "highpass=f=65,"
            "equalizer=f=140:width_type=o:width=1.2:g=3.5,"
            "equalizer=f=4500:width_type=o:width=1.5:g=-1.5,"
            "acompressor=threshold=-18dB:ratio=2.2:attack=15:release=130:makeup=2dB"
        ),
    },
]


def synthesize_gemini_tts(prompt: str, voice_name: str, api_keys: list[str], out_raw_wav: Path) -> None:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice_name}}
            },
        },
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_err = None

    for key in api_keys:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={key}"
        for attempt in range(2):
            req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    res = json.loads(resp.read().decode("utf-8"))
                part = res["candidates"][0]["content"]["parts"][0]["inlineData"]
                pcm_bytes = base64.b64decode(part["data"])
                with wave.open(str(out_raw_wav), "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(24000)
                    wf.writeframes(pcm_bytes)
                return
            except Exception as exc:
                last_err = exc
                time.sleep(1.5)
    raise RuntimeError(f"Gemini TTS synthesis failed across all keys: {last_err}")


def master_and_normalize(in_wav: Path, out_wav: Path, out_mp3: Path, af_chain: str) -> dict:
    """Apply EQ/compression in FFmpeg, then non-destructively trim outer silence in numpy."""
    subprocess.run(
        [
            FFMPEG_BIN,
            "-y",
            "-v",
            "error",
            "-i",
            str(in_wav),
            "-af",
            af_chain,
            "-ac",
            "1",
            "-ar",
            "48000",
            "-c:a",
            "pcm_s16le",
            str(out_wav),
        ],
        check=True,
    )

    with wave.open(str(out_wav), "rb") as wf:
        sample_rate = wf.getframerate()
        samples = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32)

    # Non-destructive outer boundary detection: find first and last active sample (> -65 dBFS)
    # Never cuts internal pauses or trailing vowel/consonant tails!
    threshold = 32768.0 * (10.0 ** (-65.0 / 20.0))
    active_idx = np.where(np.abs(samples) > threshold)[0]
    if len(active_idx) > 0:
        lead_keep = int(0.08 * sample_rate)
        tail_keep = int(0.32 * sample_rate)
        start_i = max(0, int(active_idx[0]) - lead_keep)
        end_i = min(len(samples), int(active_idx[-1]) + tail_keep)
        samples = samples[start_i:end_i]

    # Gentle 25ms fade-in and 60ms fade-out to prevent any click
    fade_in_len = min(len(samples), int(0.025 * sample_rate))
    fade_out_len = min(len(samples), int(0.060 * sample_rate))
    if fade_in_len > 0:
        samples[:fade_in_len] *= np.linspace(0.0, 1.0, fade_in_len, dtype=np.float32)
    if fade_out_len > 0:
        samples[-fade_out_len:] *= np.linspace(1.0, 0.0, fade_out_len, dtype=np.float32)

    # Peak normalize to -3.0 dBFS
    peak = float(np.max(np.abs(samples))) if len(samples) else 0.0
    if peak > 0:
        target_peak = 32767.0 * (10.0 ** (-3.0 / 20.0))
        samples = np.clip(samples * (target_peak / peak), -32768, 32767)

    # Clean 60ms head pad and 120ms tail pad
    pad_head = np.zeros(int(0.06 * sample_rate), dtype=np.float32)
    pad_tail = np.zeros(int(0.12 * sample_rate), dtype=np.float32)
    full_samples = np.concatenate([pad_head, samples, pad_tail]).astype(np.int16)

    with wave.open(str(out_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(full_samples.tobytes())

    subprocess.run(
        [
            FFMPEG_BIN,
            "-y",
            "-v",
            "error",
            "-i",
            str(out_wav),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            str(out_mp3),
        ],
        check=True,
    )

    norm_floats = full_samples.astype(np.float32) / 32768.0
    duration_sec = round(len(norm_floats) / sample_rate, 3)
    peak_val = float(np.max(np.abs(norm_floats)))
    rms_val = float(np.sqrt(np.mean(norm_floats**2)))
    return {
        "sample_rate": sample_rate,
        "channels": 1,
        "duration_sec": duration_sec,
        "peak_dbfs": round(20.0 * math.log10(max(peak_val, 1e-7)), 2),
        "rms_dbfs": round(20.0 * math.log10(max(rms_val, 1e-7)), 2),
    }


def main() -> None:
    keys = load_gemini_keys()
    if not keys:
        raise RuntimeError("No Gemini API keys found.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest_lines = []

    with tempfile.TemporaryDirectory(prefix="gate2_gemini_tts_") as tmp_dir:
        tmp = Path(tmp_dir)
        for item in DIALOGUE_ITEMS:
            line_id = item["line_id"]
            raw_wav = tmp / f"{line_id}_raw24k.wav"
            final_wav = OUTPUT_DIR / f"{line_id}.wav"
            final_mp3 = OUTPUT_DIR / f"{line_id}.mp3"

            if final_wav.is_file() and final_mp3.is_file() and not item.get("force_resynthesize", False):
                print(f"Reusing verified {line_id} ({final_wav.name})...")
                with wave.open(str(final_wav), "rb") as wf:
                    sr = wf.getframerate()
                    norm_floats = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
                duration_sec = round(len(norm_floats) / sr, 3)
                peak_val = float(np.max(np.abs(norm_floats)))
                rms_val = float(np.sqrt(np.mean(norm_floats**2)))
                metrics = {
                    "sample_rate": sr,
                    "channels": 1,
                    "duration_sec": duration_sec,
                    "peak_dbfs": round(20.0 * math.log10(max(peak_val, 1e-7)), 2),
                    "rms_dbfs": round(20.0 * math.log10(max(rms_val, 1e-7)), 2),
                }
            else:
                print(f"Synthesizing {line_id} with voice '{item['voice_name']}'...")
                synthesize_gemini_tts(item["tts_prompt"], item["voice_name"], keys, raw_wav)
                metrics = master_and_normalize(raw_wav, final_wav, final_mp3, item["ffmpeg_af"])

            fits_window = metrics["duration_sec"] <= item["timeline_window_sec"]
            manifest_lines.append(
                {
                    "line_id": line_id,
                    "beat_id": item["beat_id"],
                    "speaker": item["speaker"],
                    "character_label": item["character_label"],
                    "voice_engine": f"gemini-2.5-flash-preview-tts ({item['voice_name']})",
                    "text": item["full_text"],
                    "timeline_start_sec": item["timeline_start_sec"],
                    "timeline_end_sec": round(item["timeline_start_sec"] + metrics["duration_sec"], 3),
                    "timeline_window_sec": item["timeline_window_sec"],
                    "fits_timeline_window": fits_window,
                    "wav_path": f"factory/materialAndDraft/Chapter1/audio/tts/{final_wav.name}",
                    "mp3_path": f"factory/materialAndDraft/Chapter1/audio/tts/{final_mp3.name}",
                    "metrics": metrics,
                    "qa_status": "PASS" if fits_window and metrics["duration_sec"] > 0.5 else "WARN_DURATION",
                }
            )
            print(
                f" -> {line_id}: duration={metrics['duration_sec']}s "
                f"(window={item['timeline_window_sec']}s), peak={metrics['peak_dbfs']} dBFS, "
                f"rms={metrics['rms_dbfs']} dBFS"
            )

    manifest_path = OUTPUT_DIR / "tts_manifest_gate2.json"
    manifest_path.write_text(
        json.dumps(
            {
                "episode_id": "EP01",
                "gate": "GATE_2_TTS_VOICE_QA",
                "engine": "gemini-2.5-flash-preview-tts + FFmpeg Character Mastering",
                "sample_rate_hz": 48000,
                "target_peak_dbfs": -3.0,
                "lines": manifest_lines,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Gate 2 TTS manifest saved to {manifest_path}")


if __name__ == "__main__":
    main()
