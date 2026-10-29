# -*- coding: utf-8 -*-
"""
Gate 3: Foley/SFX, Ambience & BGM Synthesis + 60s Multi-Stem Mixing (Auto-Ducking)
Episode 01: Đêm Đầu Tháng 5 Ở Phú Quốc (v6.0 - 60s)
Output format: 48kHz, 16-bit PCM WAV + 192kbps MP3
"""

import json
import math
import subprocess
import sys
import wave
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SR = 48000
TOTAL_DUR = 60.0
TOTAL_SAMPLES = int(SR * TOTAL_DUR)

FFMPEG_BIN = r"C:\projects\HaizFlow-main\runtime\bin\ffmpeg.exe"
BASE_DIR = Path(__file__).resolve().parent
TTS_DIR = BASE_DIR / "audio" / "tts"
SFX_DIR = BASE_DIR / "audio" / "sfx"
BGM_DIR = BASE_DIR / "audio" / "bgm"
MIX_DIR = BASE_DIR / "audio" / "mix"

for d in (SFX_DIR, BGM_DIR, MIX_DIR):
    d.mkdir(parents=True, exist_ok=True)


# ============================================================================
# DSP & ACOUSTIC HELPER FUNCTIONS (Pure NumPy, 48kHz Stereo/Mono)
# ============================================================================

def one_pole_lowpass(x: np.ndarray, cutoff_hz: float, sr: int = SR) -> np.ndarray:
    """Fast 1-pole IIR low-pass filter using cumulative vector operations or loop."""
    rc = 1.0 / (2.0 * math.pi * max(cutoff_hz, 1.0))
    dt = 1.0 / sr
    alpha = dt / (rc + dt)
    # Use FFT-based zero-phase or causal FIR approximation for speed in pure numpy
    # For exact 1st-order causal response, use FFT convolution with exponential kernel:
    kernel_len = min(len(x), int(sr * min(0.25, 6.0 / max(cutoff_hz, 10.0))))
    if kernel_len < 4:
        return x.copy()
    t_k = np.arange(kernel_len, dtype=np.float64) / sr
    kernel = (1.0 / rc) * np.exp(-t_k / rc) * dt
    kernel /= np.sum(kernel)
    return fft_convolve_1d(x, kernel)


def fft_bandpass(x: np.ndarray, low_hz: float, high_hz: float, sr: int = SR, roll_width: float = 0.2) -> np.ndarray:
    """Smooth frequency-domain bandpass filter with raised-cosine transitions."""
    n = len(x)
    freqs = np.fft.rfftfreq(n, d=1.0 / sr)
    X = np.fft.rfft(x)
    mask = np.zeros_like(freqs)

    low_w = max(low_hz * roll_width, 8.0)
    high_w = max(high_hz * roll_width, 20.0)

    # Passband
    in_band = (freqs >= low_hz) & (freqs <= high_hz)
    mask[in_band] = 1.0

    # Lower transition
    low_trans = (freqs >= max(0.0, low_hz - low_w)) & (freqs < low_hz)
    if np.any(low_trans):
        phase = (freqs[low_trans] - (low_hz - low_w)) / low_w
        mask[low_trans] = 0.5 * (1.0 - np.cos(np.pi * phase))

    # Upper transition
    high_trans = (freqs > high_hz) & (freqs <= high_hz + high_w)
    if np.any(high_trans):
        phase = (freqs[high_trans] - high_hz) / high_w
        mask[high_trans] = 0.5 * (1.0 + np.cos(np.pi * phase))

    return np.fft.irfft(X * mask, n=n)


def fft_convolve_1d(x: np.ndarray, h: np.ndarray) -> np.ndarray:
    n = len(x) + len(h) - 1
    n_fft = 1 << (n - 1).bit_length()
    Y = np.fft.rfft(x, n_fft) * np.fft.rfft(h, n_fft)
    y = np.fft.irfft(Y, n_fft)[:len(x)]
    return y


def pink_noise(n_samples: int, rng: np.random.Generator, sr: int = SR) -> np.ndarray:
    """Generate 1/f pink noise in frequency domain."""
    white = rng.standard_normal(n_samples)
    X = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n_samples, d=1.0 / sr)
    scale = np.ones_like(freqs)
    nonzero = freqs > 1.0
    scale[nonzero] = 1.0 / np.sqrt(freqs[nonzero])
    scale[0] = 0.0
    y = np.fft.irfft(X * scale, n=n_samples)
    peak = np.max(np.abs(y)) + 1e-9
    return y / peak


def brown_noise(n_samples: int, rng: np.random.Generator, sr: int = SR) -> np.ndarray:
    """Generate 1/f^2 brown noise in frequency domain."""
    white = rng.standard_normal(n_samples)
    X = np.fft.rfft(white)
    freqs = np.fft.rfftfreq(n_samples, d=1.0 / sr)
    scale = np.zeros_like(freqs)
    nonzero = freqs > 15.0
    scale[nonzero] = 1.0 / freqs[nonzero]
    y = np.fft.irfft(X * scale, n=n_samples)
    peak = np.max(np.abs(y)) + 1e-9
    return y / peak


def stereo_pan(mono: np.ndarray, pan: float = 0.0) -> np.ndarray:
    """Equal-power stereo panner. pan in [-1.0 (left), +1.0 (right)]. Returns (N, 2)."""
    angle = (pan + 1.0) * 0.25 * math.pi
    g_l = math.cos(angle)
    g_r = math.sin(angle)
    return np.column_stack([mono * g_l, mono * g_r])


def add_outdoor_reverb(stereo: np.ndarray, wet: float = 0.22, rt60: float = 0.85, sr: int = SR) -> np.ndarray:
    """Schroeder/early-reflection outdoor night reverb for stereo signal."""
    rng = np.random.default_rng(197505)
    ir_len = int(sr * rt60)
    t = np.arange(ir_len, dtype=np.float64) / sr
    decay = np.exp(-6.91 * t / rt60)
    ir_l = pink_noise(ir_len, rng, sr) * decay
    ir_r = pink_noise(ir_len, rng, sr) * decay
    # Early reflections at realistic coastal distances (28ms, 53ms, 89ms, 142ms)
    for delay_ms, gain in [(28, 0.45), (53, 0.32), (89, 0.22), (142, 0.15)]:
        idx = int(sr * delay_ms / 1000.0)
        if idx < ir_len:
            ir_l[idx] += gain
            ir_r[min(ir_len - 1, idx + int(sr * 0.004))] += gain * 0.95
    ir_l = fft_bandpass(ir_l, 120.0, 4200.0, sr)
    ir_r = fft_bandpass(ir_r, 120.0, 4200.0, sr)
    ir_l /= (np.sqrt(np.sum(ir_l ** 2)) + 1e-9)
    ir_r /= (np.sqrt(np.sum(ir_r ** 2)) + 1e-9)

    wet_l = fft_convolve_1d(stereo[:, 0], ir_l)
    wet_r = fft_convolve_1d(stereo[:, 1], ir_r)
    return stereo * (1.0 - wet) + np.column_stack([wet_l, wet_r]) * wet


def normalize_to_dbfs(audio: np.ndarray, target_peak_db: float = -6.0) -> np.ndarray:
    peak = float(np.max(np.abs(audio)))
    if peak < 1e-9:
        return audio
    target_lin = 10.0 ** (target_peak_db / 20.0)
    return audio * (target_lin / peak)


def fade_in_out(audio: np.ndarray, fade_in_sec: float = 0.05, fade_out_sec: float = 0.05, sr: int = SR) -> np.ndarray:
    out = audio.copy()
    n = len(out)
    n_in = min(n, int(sr * fade_in_sec))
    n_out = min(n, int(sr * fade_out_sec))
    if n_in > 1:
        env_in = 0.5 * (1.0 - np.cos(np.pi * np.linspace(0.0, 1.0, n_in)))
        if out.ndim == 2:
            out[:n_in] *= env_in[:, None]
        else:
            out[:n_in] *= env_in
    if n_out > 1:
        env_out = 0.5 * (1.0 + np.cos(np.pi * np.linspace(0.0, 1.0, n_out)))
        if out.ndim == 2:
            out[-n_out:] *= env_out[:, None]
        else:
            out[-n_out:] *= env_out
    return out


def save_wav_and_mp3(audio: np.ndarray, wav_path: Path, mp3_path: Path | None = None, sr: int = SR) -> dict:
    """Save stereo or mono float64 [-1, 1] array to 16-bit PCM WAV (and optional MP3)."""
    clipped = np.clip(audio, -0.999, 0.999)
    pcm16 = (clipped * 32767.0).astype(np.int16)
    n_ch = 1 if pcm16.ndim == 1 else pcm16.shape[1]

    with wave.open(str(wav_path), "wb") as wf:
        wf.setnchannels(n_ch)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

    if mp3_path is not None:
        subprocess.run(
            [
                FFMPEG_BIN, "-y",
                "-i", str(wav_path),
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(mp3_path),
            ],
            check=True,
            capture_output=True,
        )

    peak_lin = float(np.max(np.abs(clipped)))
    rms_lin = float(np.sqrt(np.mean(clipped ** 2)))
    peak_db = round(20.0 * math.log10(max(peak_lin, 1e-9)), 2)
    rms_db = round(20.0 * math.log10(max(rms_lin, 1e-9)), 2)
    dur_sec = round(len(clipped) / sr, 3)
    return {
        "wav_path": str(wav_path.relative_to(BASE_DIR.parent.parent.parent)).replace("\\", "/"),
        "mp3_path": str(mp3_path.relative_to(BASE_DIR.parent.parent.parent)).replace("\\", "/") if mp3_path else None,
        "duration_sec": dur_sec,
        "channels": n_ch,
        "sample_rate": sr,
        "peak_dbfs": peak_db,
        "rms_dbfs": rms_db,
    }


def read_wav_stereo(wav_path: Path) -> np.ndarray:
    with wave.open(str(wav_path), "rb") as wf:
        n_ch = wf.getnchannels()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)
    samples = np.frombuffer(raw, dtype=np.int16).astype(np.float64) / 32768.0
    if n_ch == 1:
        return np.column_stack([samples, samples])
    samples = samples.reshape(-1, n_ch)
    return samples[:, :2]


# ============================================================================
# LAYER 1: AMBIENCE GENERATORS
# ============================================================================

def synth_amb_beat1_2_night_sea_boat(dur_sec: float = 20.0) -> np.ndarray:
    """
    00.0s - 20.0s: Night sea waves lapping wooden hull + night wind +
    Vietnamese 'ghe máy đuôi tôm' (single-cylinder marine diesel engine) chugging
    until 11.2s (when the tiller strike happens), then sputtering down as waves dominate.
    """
    rng = np.random.default_rng(101)
    n = int(SR * dur_sec)
    t = np.arange(n, dtype=np.float64) / SR

    # 1. Night ocean swell & waves lapping wooden hull (stereo decorrelated)
    p_l = pink_noise(n, rng)
    p_r = pink_noise(n, rng)
    swell_1 = 0.55 + 0.45 * np.sin(2.0 * np.pi * 0.16 * t - 0.4)
    swell_2 = 0.55 + 0.45 * np.sin(2.0 * np.pi * 0.23 * t + 1.1)

    surf_l = fft_bandpass(p_l, 85.0, 950.0) * swell_1 + fft_bandpass(p_l, 900.0, 2800.0) * (swell_1 ** 2) * 0.28
    surf_r = fft_bandpass(p_r, 85.0, 950.0) * swell_2 + fft_bandpass(p_r, 900.0, 2800.0) * (swell_2 ** 2) * 0.28

    # Night wind whistle (subtle eerie coastal breeze)
    wind_mod = 0.5 + 0.5 * np.sin(2.0 * np.pi * 0.09 * t + 0.7)
    wind_l = fft_bandpass(pink_noise(n, rng), 220.0, 680.0) * wind_mod * 0.35
    wind_r = fft_bandpass(pink_noise(n, rng), 240.0, 720.0) * wind_mod * 0.35

    # Wooden hull creaks & water slap against boat planks
    slap_l = np.zeros(n)
    slap_r = np.zeros(n)
    for slap_t in np.arange(0.6, dur_sec - 0.5, 1.35):
        jitter_t = slap_t + rng.uniform(-0.25, 0.25)
        idx = int(jitter_t * SR)
        slen = int(0.32 * SR)
        if idx + slen < n:
            st = np.arange(slen) / SR
            env = np.exp(-st * 16.0) * np.sin(np.pi * np.minimum(1.0, st / 0.015))
            burst = fft_bandpass(rng.standard_normal(slen), 180.0, 650.0) * env * 0.45
            slap_l[idx:idx + slen] += burst * rng.uniform(0.6, 1.0)
            slap_r[idx:idx + slen] += burst * rng.uniform(0.6, 1.0)

    # 2. Ghe máy đuôi tôm (long-tail diesel boat engine: tạch... tạch... xập xình)
    # Runs steadily 0.0s -> 11.2s at ~11.8 Hz, then throttles down / stalls after the tiller swing at 11.2s
    engine_mono = np.zeros(n)
    cur_t = 0.04
    while cur_t < 13.8:
        if cur_t < 11.2:
            fire_hz = 11.8 + 0.35 * math.sin(2.0 * math.pi * 0.7 * cur_t) + rng.uniform(-0.18, 0.18)
            amp = 0.85
        else:
            # Sputtering down between 11.2s and 13.8s
            progress = (cur_t - 11.2) / 2.6
            fire_hz = max(3.5, 11.8 * (1.0 - 0.72 * progress))
            amp = max(0.0, 0.85 * (1.0 - progress) ** 1.6)

        idx = int(cur_t * SR)
        plen = int(0.075 * SR)
        if idx + plen < n and amp > 0.01:
            pt = np.arange(plen) / SR
            # Exhaust thump (95-155 Hz)
            thump = np.sin(2.0 * np.pi * (128.0 - 350.0 * pt) * pt) * np.exp(-pt * 48.0) * 0.75
            # Mechanical valve/injector click ('tạch' at 950-2400 Hz)
            click_noise = fft_bandpass(rng.standard_normal(plen), 850.0, 2600.0)
            click = click_noise * np.exp(-pt * 140.0) * 0.55
            # Propeller water churn ('xập xình' at 250-700 Hz)
            churn = fft_bandpass(rng.standard_normal(plen), 220.0, 720.0) * np.exp(-pt * 28.0) * 0.42
            stroke = (thump + click + churn) * amp
            engine_mono[idx:idx + plen] += stroke

        cur_t += 1.0 / fire_hz

    engine_stereo = stereo_pan(engine_mono, pan=-0.12)
    sea_stereo = np.column_stack([surf_l + wind_l + slap_l, surf_r + wind_r + slap_r])

    mix = sea_stereo * 0.65 + engine_stereo * 0.55
    mix = fade_in_out(mix, 0.4, 0.8)
    return normalize_to_dbfs(mix, -15.5)


def synth_amb_beat3_4_night_coastal_swamp(dur_sec: float = 26.0) -> np.ndarray:
    """
    20.0s - 46.0s: Coastal night wind through palm/mangrove trees, distant surf rumble,
    and subtle tropical night insects/crickets in Phu Quoc forest.
    """
    rng = np.random.default_rng(202)
    n = int(SR * dur_sec)
    t = np.arange(n, dtype=np.float64) / SR

    # Distant low surf rumble
    surf_l = fft_bandpass(brown_noise(n, rng), 55.0, 380.0) * (0.55 + 0.45 * np.sin(2.0 * np.pi * 0.14 * t))
    surf_r = fft_bandpass(brown_noise(n, rng), 55.0, 380.0) * (0.55 + 0.45 * np.sin(2.0 * np.pi * 0.14 * t + 1.2))

    # Wind through mangrove/coconut leaves
    wind_env = 0.5 + 0.5 * np.sin(2.0 * np.pi * 0.11 * t + 0.3)
    leaves_l = fft_bandpass(pink_noise(n, rng), 300.0, 1400.0) * wind_env * 0.35
    leaves_r = fft_bandpass(pink_noise(n, rng), 320.0, 1450.0) * wind_env * 0.35

    # Subtle tropical night crickets (4.1 kHz & 4.38 kHz pulsed chirps, kept gentle so they never mask voice)
    cricket_l = np.zeros(n)
    cricket_r = np.zeros(n)
    for c_t in np.arange(0.3, dur_sec - 0.4, 0.85):
        idx = int((c_t + rng.uniform(-0.1, 0.1)) * SR)
        clen = int(0.28 * SR)
        if idx + clen < n:
            ct = np.arange(clen) / SR
            pulse = np.sin(2.0 * np.pi * 28.0 * ct) > 0.0
            env = np.sin(np.pi * ct / 0.28) * pulse.astype(np.float64)
            tone_l = np.sin(2.0 * np.pi * 4120.0 * ct) * env * 0.045
            tone_r = np.sin(2.0 * np.pi * 4360.0 * ct) * env * 0.045
            cricket_l[idx:idx + clen] += tone_l
            cricket_r[idx:idx + clen] += tone_r

    stereo = np.column_stack([surf_l * 0.65 + leaves_l + cricket_l, surf_r * 0.65 + leaves_r + cricket_r])
    stereo = fade_in_out(stereo, 0.6, 0.8)
    return normalize_to_dbfs(stereo, -16.5)


def synth_amb_beat5_sunrise_calm_sea(dur_sec: float = 14.0) -> np.ndarray:
    """
    46.0s - 60.0s: Peaceful morning waves gently washing the sandy beach at sunrise + warm breeze.
    """
    rng = np.random.default_rng(303)
    n = int(SR * dur_sec)
    t = np.arange(n, dtype=np.float64) / SR

    # Gentle rhythmic morning wave wash (every ~4.5s)
    wave_cycle = 0.45 + 0.55 * (0.5 * (1.0 + np.sin(2.0 * np.pi * 0.21 * t - 0.8))) ** 1.5
    foam_cycle = 0.30 + 0.70 * (0.5 * (1.0 + np.sin(2.0 * np.pi * 0.21 * t - 1.25))) ** 2.2

    p_l = pink_noise(n, rng)
    p_r = pink_noise(n, rng)

    body_l = fft_bandpass(p_l, 90.0, 780.0) * wave_cycle * 0.65
    body_r = fft_bandpass(p_r, 90.0, 780.0) * wave_cycle * 0.65

    foam_l = fft_bandpass(p_l, 800.0, 3200.0) * foam_cycle * 0.24
    foam_r = fft_bandpass(p_r, 800.0, 3200.0) * foam_cycle * 0.24

    stereo = np.column_stack([body_l + foam_l, body_r + foam_r])
    stereo = fade_in_out(stereo, 0.7, 1.2)
    return normalize_to_dbfs(stereo, -16.0)


# ============================================================================
# LAYER 2: ACTION FOLEY GENERATORS (Frame-Accurate)
# ============================================================================

def synth_foley_beat2_tiller_hit_bop(dur_sec: float = 1.65) -> np.ndarray:
    """
    10.90s - 12.55s (Impact peak at 11.20s):
    Ultra-realistic, high-impact cinematic Foley for 'Đánh cần lái' (Hardwood Tiller Strike):
    - 0.04s - 0.29s (10.94s - 11.19s): Heavy two-handed hardwood tiller whip-whoosh ('VÚT!')
      using time-swept aerodynamic noise (120-450 Hz -> 350-1800 Hz, zero tonal sine hum!)
    - 0.30s (11.20s): Explosive dry hardwood smash ('BỐP! RẮC!') with massive RMS density:
      tight sub-thump (<30ms) + broadband hardwood plank slap + splintering timber crackles
    - 0.60s - 1.40s (11.50s - 12.30s): Heavy body & rifle crashing onto hollow wooden boat deck ('RẦM! CỘP!')
    """
    rng = np.random.default_rng(401)
    n = int(SR * dur_sec)
    out_l = np.zeros(n)
    out_r = np.zeros(n)

    # 1. Heavy two-handed hardwood tiller whip-whoosh ('VÚT!') from 0.05s -> 0.30s
    # Time-swept aerodynamic noise (starts low 120-500 Hz, accelerates to 400-2200 Hz right before impact)
    w_idx = int(0.05 * SR)
    w_len = int(0.25 * SR)
    wt = np.arange(w_len) / SR
    prog = wt / 0.25
    env_low_air = (prog ** 1.5) * np.sin(np.pi * (prog ** 0.85))
    env_high_whip = (prog ** 3.0) * np.sin(np.pi * (prog ** 1.2))
    whoosh_low = fft_bandpass(brown_noise(w_len, rng), 120.0, 550.0) * env_low_air * 1.35
    whoosh_whip = fft_bandpass(pink_noise(w_len, rng), 420.0, 2200.0) * env_high_whip * 1.45
    swing_sig = np.tanh((whoosh_low + whoosh_whip) * 1.6) * 0.85
    out_l[w_idx:w_idx + w_len] += swing_sig * 1.10
    out_r[w_idx:w_idx + w_len] += swing_sig * 0.75

    # 2. Explosive Dry Hardwood Smash ('BỐP! RẮC!') at 0.30s (timeline 11.20s)
    # Dense multi-layered hardwood impact with soft-clipping crest control for maximum perceived loudness!
    hit_idx = int(0.30 * SR)
    h_len = int(0.55 * SR)
    ht = np.arange(h_len) / SR

    # (a) Tight physical chest thump (140 Hz -> 45 Hz in 28ms, fast decay so zero boominess)
    f_punch = 45.0 + 110.0 * np.exp(-ht * 65.0)
    chest_punch = np.sin(2.0 * np.pi * np.cumsum(f_punch) / SR) * np.exp(-ht * 34.0) * 1.15

    # (b) Ultra-short dry hardwood knock transient (<14ms decay)
    wood_knock = (
        np.sin(2.0 * np.pi * 185.0 * ht) * np.exp(-ht * 95.0) * 0.70
        + np.sin(2.0 * np.pi * 370.0 * ht) * np.exp(-ht * 125.0) * 0.65
    )

    # (c) Triple-stage broadband hardwood impact ('BỐP!' at 0ms, +12ms, +24ms for thick cinematic body)
    ht2 = np.maximum(0.0, ht - 0.012)
    mask2 = (ht >= 0.012).astype(np.float64)
    ht3 = np.maximum(0.0, ht - 0.024)
    mask3 = (ht >= 0.024).astype(np.float64)

    env_body = np.exp(-ht * 19.0) + 0.70 * np.exp(-ht2 * 22.0) * mask2 + 0.45 * np.exp(-ht3 * 25.0) * mask3
    env_crack = np.exp(-ht * 35.0) + 0.80 * np.exp(-ht2 * 40.0) * mask2 + 0.50 * np.exp(-ht3 * 45.0) * mask3

    wood_body = fft_bandpass(brown_noise(h_len, rng), 90.0, 540.0) * env_body * 1.75
    wood_slap = fft_bandpass(pink_noise(h_len, rng), 380.0, 2200.0) * env_crack * 1.95
    wood_snap = fft_bandpass(rng.standard_normal(h_len), 1400.0, 4800.0) * env_crack * 1.45

    # (d) Hardwood splinter micro-cracks ('RẮC!') at +32ms, +48ms, +68ms, +92ms
    splinters = np.zeros(h_len)
    for sp_t, sp_amp in [(0.032, 0.95), (0.048, 0.80), (0.068, 0.65), (0.092, 0.50)]:
        sp_i = int(sp_t * SR)
        sp_l = int(0.014 * SR)
        if sp_i + sp_l < h_len:
            spt = np.arange(sp_l) / SR
            sp_burst = fft_bandpass(rng.standard_normal(sp_l), 850.0, 4400.0) * np.exp(-spt * 190.0) * sp_amp
            splinters[sp_i:sp_i + sp_l] += sp_burst

    strike_raw = chest_punch + wood_knock + wood_body + wood_slap + wood_snap + splinters
    # High-density saturation so the RMS body of 'BỐP!' is huge and punchy
    strike_wave = np.tanh(strike_raw * 2.1)
    out_l[hit_idx:hit_idx + h_len] += strike_wave * 0.98
    out_r[hit_idx:hit_idx + h_len] += strike_wave * 1.02

    # 3. Heavy body crashing onto hollow wooden boat deck at +0.32s (timeline 11.52s: 'RẦM! CỘP!')
    crash_idx = hit_idx + int(0.32 * SR)
    c_len = int(0.65 * SR)
    if crash_idx + c_len < n:
        ct = np.arange(c_len) / SR
        f_hull = 48.0 + 72.0 * np.exp(-ct * 48.0)
        hull_thump = np.sin(2.0 * np.pi * np.cumsum(f_hull) / SR) * np.exp(-ct * 24.0) * 0.95
        plank_boom = fft_bandpass(brown_noise(c_len, rng), 75.0, 450.0) * np.exp(-ct * 11.0) * 1.65
        plank_slap = fft_bandpass(pink_noise(c_len, rng), 320.0, 1950.0) * np.exp(-ct * 16.0) * 1.45
        plank_snap = fft_bandpass(rng.standard_normal(c_len), 1200.0, 3800.0) * np.exp(-ct * 28.0) * 0.90
        deck_slam = np.tanh((hull_thump + plank_boom + plank_slap + plank_snap) * 1.85) * 0.94
        out_l[crash_idx:crash_idx + c_len] += deck_slam * 0.88
        out_r[crash_idx:crash_idx + c_len] += deck_slam * 1.06

    # 4. Heavy wooden & rifle clatter across boat floorboards (+0.52s and +0.70s — pure broadband wood/metal knocks)
    for clat_offset, clat_gain, c_pan in [(0.52, 0.85, 0.28), (0.70, 0.72, -0.24)]:
        cl_idx = hit_idx + int(clat_offset * SR)
        cl_len = int(0.24 * SR)
        if cl_idx + cl_len < n:
            clt = np.arange(cl_len) / SR
            clatter_thud = np.sin(2.0 * np.pi * 135.0 * clt) * np.exp(-clt * 80.0) * 0.65
            clatter_wood = fft_bandpass(pink_noise(cl_len, rng), 240.0, 2100.0) * np.exp(-clt * 24.0) * 1.35
            clatter_metal = fft_bandpass(rng.standard_normal(cl_len), 1500.0, 4500.0) * np.exp(-clt * 48.0) * 0.85
            clatter = np.tanh((clatter_thud + clatter_wood + clatter_metal) * 1.65) * clat_gain
            panned = stereo_pan(clatter, c_pan)
            out_l[cl_idx:cl_idx + cl_len] += panned[:, 0]
            out_r[cl_idx:cl_idx + cl_len] += panned[:, 1]

    stereo = np.column_stack([out_l, out_r])
    stereo = np.tanh(stereo * 1.35)
    stereo = add_outdoor_reverb(stereo, wet=0.18, rt60=0.55)
    stereo = fade_in_out(stereo, 0.02, 0.10)
    return normalize_to_dbfs(stereo, -0.8)


def synth_water_droplet_grains(
    dur_sec: float,
    rng: np.random.Generator,
    n_grains: int = 45,
) -> np.ndarray:
    """
    Synthesize stochastic liquid water splash grains (20-65ms bursts of narrowband-filtered pink noise
    across 220-2400 Hz, ZERO sine waves!). This produces the unmistakable texture of cascading
    water droplets and foam bursts ('ÀO! RÀO! BÕM!') without any tonal/electronic ringing.
    """
    n = int(SR * dur_sec)
    out = np.zeros(n, dtype=np.float64)
    base_pink = pink_noise(n, rng)
    # Pre-filter into 5 liquid formants so grain assembly is fast and 100% organic
    bands = [
        fft_bandpass(base_pink, 180.0, 480.0),
        fft_bandpass(base_pink, 380.0, 880.0),
        fft_bandpass(base_pink, 720.0, 1550.0),
        fft_bandpass(base_pink, 1250.0, 2500.0),
        fft_bandpass(base_pink, 2000.0, 3600.0),
    ]
    for _ in range(n_grains):
        g_start = rng.uniform(0.02, max(0.04, dur_sec - 0.08))
        g_dur = rng.uniform(0.022, 0.075)
        idx = int(g_start * SR)
        glen = min(n - idx, int(g_dur * SR))
        if glen < 8:
            continue
        gt = np.arange(glen, dtype=np.float64) / SR
        env = np.sin(np.pi * gt / g_dur) ** 1.4
        b_idx = int(rng.integers(0, len(bands)))
        amp = rng.uniform(0.45, 1.15)
        out[idx:idx + glen] += bands[b_idx][idx:idx + glen] * env * amp
    return out


def synth_foley_beat2_water_plunge_um(dur_sec: float = 3.6) -> np.ndarray:
    """
    12.15s - 15.75s (Main plunge peak at 12.50s):
    Ultra-realistic, visceral 'Bỏ thuyền lao xuống biển' (Abandoning Boat & Double Ocean Plunge):
    100% organic hydrodynamic filtered turbulence (ZERO tonal sine sweeps or laser/sonar bubbles!):
    - 0.03s & 0.17s (12.18s & 12.32s): Frantic feet kicking off the wooden boat gunwale ('CỘP! RẦM!')
    - 0.35s (12.50s) & 0.74s (12.89s): Two heavy human bodies plunging into the deep sea ('ÙM! ÀO! XÒA!')
      using time-swept 4-stage spectral water bands:
        Stage A (0.00-0.12s): Heavy wet impact & deep water cavity displacement (55-360 Hz brown noise + tight 52Hz thud)
        Stage B (0.04-0.38s): Rising water column roar (220-1150 Hz pink noise)
        Stage C (0.10-0.65s): Crashing wave crest & splash droplets (550-2800 Hz + stochastic droplet grains)
        Stage D (0.25-1.25s): Turbulent foam wash & sloshing wake (160-1400 Hz)
    - 1.45s - 3.45s (13.60s - 15.60s): Vigorous swimming strokes through the dark sea.
    """
    rng = np.random.default_rng(402)
    n = int(SR * dur_sec)
    out_l = np.zeros(n)
    out_r = np.zeros(n)

    # 1. Gunwale push-off footsteps & wooden boat hull kick ('CỘP! RẦM!' at 0.03s and 0.17s)
    for step_t, step_gain, pan in [(0.03, 0.88, -0.24), (0.17, 0.98, 0.22)]:
        st_i = int(step_t * SR)
        st_l = int(0.19 * SR)
        stt = np.arange(st_l) / SR
        f_kick = 55.0 + 75.0 * np.exp(-stt * 55.0)
        hull_thump = np.sin(2.0 * np.pi * np.cumsum(f_kick) / SR) * np.exp(-stt * 32.0) * 0.80
        plank_knock = fft_bandpass(brown_noise(st_l, rng), 95.0, 620.0) * np.exp(-stt * 22.0) * 1.35
        plank_scuff = fft_bandpass(pink_noise(st_l, rng), 450.0, 2200.0) * np.exp(-stt * 28.0) * 0.85
        wood_kick = np.tanh((hull_thump + plank_knock + plank_scuff) * 1.55) * step_gain
        panned = stereo_pan(wood_kick, pan)
        out_l[st_i:st_i + st_l] += panned[:, 0]
        out_r[st_i:st_i + st_l] += panned[:, 1]

    # 2. Massive Double Ocean Plunge ('ÙM! ÀO! XÒA!'):
    #    Plunge A at 0.35s (timeline 12.50s - Young Fisherman leaping into sea)
    #    Plunge B at 0.74s (timeline 12.89s - Old Fisherman diving right behind him)
    for p_sec, p_gain, p_pan in [(0.35, 1.00, 0.16), (0.74, 0.95, -0.20)]:
        p_idx = int(p_sec * SR)
        p_len = int(1.35 * SR)
        if p_idx + p_len >= n:
            continue
        pt = np.arange(p_len) / SR

        # Tight sub-bass impact thud (<45ms decay so it never sounds like a synth tone)
        sub_impact = np.sin(2.0 * np.pi * 54.0 * pt) * np.exp(-pt * 28.0) * 0.75

        # Stage A: Deep water mass displacement ('ÙM!' at 55-350 Hz, peaking at 25ms)
        env_a = np.sin(np.pi * 0.5 * np.minimum(1.0, pt / 0.022)) * np.exp(-pt * 5.2)
        stage_a_um = fft_bandpass(brown_noise(p_len, rng), 55.0, 350.0) * env_a * 2.10

        # Stage B: Erupting water column ('ÀO!' at 220-1150 Hz, peaking at 85ms)
        pt_b = np.maximum(0.0, pt - 0.020)
        mask_b = (pt >= 0.020).astype(np.float64)
        env_b = np.sin(np.pi * 0.5 * np.minimum(1.0, pt_b / 0.065)) * np.exp(-pt_b * 3.4) * mask_b
        stage_b_ao = fft_bandpass(pink_noise(p_len, rng), 220.0, 1150.0) * env_b * 1.85

        # Stage C: Crashing whitewater crest & splash droplets ('XÒA!' at 600-2900 Hz, peaking at 150ms)
        pt_c = np.maximum(0.0, pt - 0.055)
        mask_c = (pt >= 0.055).astype(np.float64)
        env_c = np.sin(np.pi * 0.5 * np.minimum(1.0, pt_c / 0.095)) * np.exp(-pt_c * 2.8) * mask_c
        stage_c_crest = fft_bandpass(pink_noise(p_len, rng), 600.0, 2900.0) * env_c * 1.45

        # Stage D: Stochastic liquid droplet bursts & sloshing wake (ZERO sine waves!)
        droplets = synth_water_droplet_grains(1.35, rng, n_grains=55) * np.exp(-pt * 2.1) * 0.95

        plunge_sig = np.tanh((sub_impact + stage_a_um + stage_b_ao + stage_c_crest + droplets) * 1.65) * p_gain
        panned = stereo_pan(plunge_sig, p_pan)
        out_l[p_idx:p_idx + p_len] += panned[:, 0]
        out_r[p_idx:p_idx + p_len] += panned[:, 1]

    # 3. Heavy cascading wave wash & turbulent water sloshing around the boat (0.65s -> 2.85s)
    s_idx = int(0.65 * SR)
    s_len = int(2.20 * SR)
    st = np.arange(s_len) / SR
    splash_env = np.sin(np.pi * 0.5 * np.minimum(1.0, st / 0.16)) * np.exp(-st * 1.35)
    slosh_mod_l = np.clip(0.55 + 0.45 * np.sin(2.0 * np.pi * 4.2 * st) * np.cos(2.0 * np.pi * 2.7 * st + 0.5), 0.15, 1.2)
    slosh_mod_r = np.clip(0.55 + 0.45 * np.sin(2.0 * np.pi * 4.5 * st + 1.2) * np.cos(2.0 * np.pi * 2.9 * st + 1.8), 0.15, 1.2)

    slosh_l = (
        fft_bandpass(brown_noise(s_len, rng), 90.0, 520.0) * splash_env * slosh_mod_l * 1.20
        + fft_bandpass(pink_noise(s_len, rng), 320.0, 1650.0) * splash_env * slosh_mod_l * 0.95
        + synth_water_droplet_grains(2.20, rng, n_grains=50) * splash_env * 0.65
    )
    slosh_r = (
        fft_bandpass(brown_noise(s_len, rng), 90.0, 520.0) * splash_env * slosh_mod_r * 1.20
        + fft_bandpass(pink_noise(s_len, rng), 320.0, 1650.0) * splash_env * slosh_mod_r * 0.95
        + synth_water_droplet_grains(2.20, rng, n_grains=50) * splash_env * 0.65
    )
    out_l[s_idx:s_idx + s_len] += slosh_l * 0.85
    out_r[s_idx:s_idx + s_len] += slosh_r * 0.85

    # 4. Vigorous frantic swimming strokes & water churn (1.45s -> 3.45s)
    for stroke_t, s_gain, s_pan in [(1.48, 0.88, -0.26), (1.96, 0.82, 0.26), (2.44, 0.74, -0.22), (2.92, 0.66, 0.22)]:
        st_idx = int(stroke_t * SR)
        st_len = int(0.44 * SR)
        if st_idx + st_len < n:
            stt = np.arange(st_len) / SR
            st_env = np.sin(np.pi * stt / 0.44) ** 1.3
            swim_churn = (
                fft_bandpass(brown_noise(st_len, rng), 80.0, 420.0) * st_env * 1.25
                + fft_bandpass(pink_noise(st_len, rng), 300.0, 1550.0) * st_env * 0.95
                + synth_water_droplet_grains(0.44, rng, n_grains=18) * st_env * 0.65
            )
            swim_churn = np.tanh(swim_churn * 1.40) * s_gain
            panned = stereo_pan(swim_churn, s_pan)
            out_l[st_idx:st_idx + st_len] += panned[:, 0]
            out_r[st_idx:st_idx + st_len] += panned[:, 1]

    stereo = np.column_stack([out_l, out_r])
    stereo = np.tanh(stereo * 1.30)
    stereo = add_outdoor_reverb(stereo, wet=0.22, rt60=0.65)
    stereo = fade_in_out(stereo, 0.02, 0.22)
    return normalize_to_dbfs(stereo, -0.8)


def synth_foley_beat2_ak47_bursts_distant(dur_sec: float = 5.5) -> np.ndarray:
    """
    14.0s - 19.5s: Tiếng súng AK nổ rát rạt trên bờ cát rồi xa dần trong tiếng gió và tiếng lặn nước.
    3 bursts of AK-47 fire (600 RPM = 0.10s cycle) getting progressively more distant / underwater-filtered.
    """
    rng = np.random.default_rng(403)
    n = int(SR * dur_sec)
    out_l = np.zeros(n)
    out_r = np.zeros(n)

    bursts = [
        # (start_sec_in_clip, num_rounds, distance_gain, high_cut_hz, pan)
        (0.15, 3, 0.92, 3400.0, 0.25),
        (1.65, 4, 0.68, 2200.0, -0.20),
        (3.45, 3, 0.45, 1200.0, 0.15),  # Heard while diving deeper / further out
    ]

    for b_start, n_rounds, gain, high_cut, pan in bursts:
        for r_idx in range(n_rounds):
            shot_t = b_start + r_idx * 0.102 + rng.uniform(-0.004, 0.004)
            idx = int(shot_t * SR)
            slen = int(0.42 * SR)
            if idx + slen >= n:
                continue
            st = np.arange(slen) / SR
            # Muzzle blast (140 Hz -> 65 Hz punch + broadband crack 350-high_cut Hz)
            punch = np.sin(2.0 * np.pi * (65.0 + 95.0 * np.exp(-st * 45.0)) * st) * np.exp(-st * 28.0) * 0.85
            crack = fft_bandpass(rng.standard_normal(slen), 280.0, high_cut) * np.exp(-st * 42.0) * 0.95
            tail = fft_bandpass(pink_noise(slen, rng), 150.0, min(1400.0, high_cut)) * np.exp(-st * 8.5) * 0.40
            shot = np.tanh((punch + crack + tail) * 1.6) * gain
            panned = stereo_pan(shot, pan)
            out_l[idx:idx + slen] += panned[:, 0]
            out_r[idx:idx + slen] += panned[:, 1]

    stereo = add_outdoor_reverb(np.column_stack([out_l, out_r]), wet=0.35, rt60=1.15)
    stereo = fade_in_out(stereo, 0.03, 0.40)
    return normalize_to_dbfs(stereo, -7.0)


def synth_foley_beat3_footsteps_and_door_knock(dur_sec: float = 2.45) -> np.ndarray:
    """
    20.0s - 22.45s:
    - 0.00s - 0.95s: Rapid barefoot running steps on wet coastal sand/earth + urgent panting breath
    - 1.00s - 1.75s: 4 urgent fist pounds on wooden cabin door ('Cộc! Cộc! Cộc! Cộc!')
    - 1.90s - 2.38s: Metal latch clack & wooden door swinging open with a low wood stopper thud
    """
    rng = np.random.default_rng(404)
    n = int(SR * dur_sec)
    out_l = np.zeros(n)
    out_r = np.zeros(n)

    # 1. Rapid barefoot footsteps on wet sand/gravel (5 quick steps: 0.06, 0.24, 0.42, 0.59, 0.76s)
    for i, step_t in enumerate([0.06, 0.24, 0.42, 0.59, 0.76]):
        idx = int(step_t * SR)
        flen = int(0.14 * SR)
        ft = np.arange(flen) / SR
        heel = np.sin(2.0 * np.pi * 82.0 * ft) * np.exp(-ft * 40.0) * 0.52
        grit = fft_bandpass(pink_noise(flen, rng), 320.0, 2800.0) * np.exp(-ft * 24.0) * 0.58
        step = (heel + grit) * (0.72 + 0.07 * i)
        pan = -0.18 if (i % 2 == 0) else 0.18
        st_pan = stereo_pan(step, pan)
        out_l[idx:idx + flen] += st_pan[:, 0]
        out_r[idx:idx + flen] += st_pan[:, 1]

    # 2. Urgent wooden door pounding ('Cộc! Cộc! Cộc! Cộc!') at 1.00s, 1.20s, 1.39s, 1.58s
    for k_i, k_t in enumerate([1.00, 1.20, 1.39, 1.58]):
        idx = int(k_t * SR)
        klen = int(0.17 * SR)
        kt = np.arange(klen) / SR
        wood = (
            np.sin(2.0 * np.pi * 118.0 * kt) * np.exp(-kt * 32.0) * 0.88
            + np.sin(2.0 * np.pi * 245.0 * kt) * np.exp(-kt * 42.0) * 0.70
            + np.sin(2.0 * np.pi * 490.0 * kt) * np.exp(-kt * 58.0) * 0.45
        )
        knuckle = fft_bandpass(rng.standard_normal(klen), 500.0, 2600.0) * np.exp(-kt * 90.0) * 0.65
        knock = np.tanh((wood + knuckle) * (1.25 + 0.1 * k_i))
        st_pan = stereo_pan(knock, pan=-0.05)
        out_l[idx:idx + klen] += st_pan[:, 0]
        out_r[idx:idx + klen] += st_pan[:, 1]

    # 3. Metal/wood latch clack (1.88s) + rapid door swing air rush & wood frame thud (2.00s -> 2.32s)
    l_idx = int(1.88 * SR)
    l_len = int(0.09 * SR)
    lt = np.arange(l_len) / SR
    latch = (
        np.sin(2.0 * np.pi * 420.0 * lt) * np.exp(-lt * 75.0) * 0.45
        + fft_bandpass(rng.standard_normal(l_len), 1100.0, 4200.0) * np.exp(-lt * 95.0) * 0.55
    )
    out_l[l_idx:l_idx + l_len] += latch
    out_r[l_idx:l_idx + l_len] += latch

    # Door swing whoosh + wood frame stop thud at 2.12s (no tonal sine sweep!)
    c_idx = int(1.96 * SR)
    c_len = int(0.36 * SR)
    ct = np.arange(c_len) / SR
    swing = fft_bandpass(pink_noise(c_len, rng), 120.0, 900.0) * np.sin(np.pi * ct / 0.36) * 0.42
    thud_t = np.maximum(0.0, ct - 0.16)
    thud_mask = (ct >= 0.16).astype(np.float64)
    stop_thud = (
        np.sin(2.0 * np.pi * 96.0 * thud_t) * np.exp(-thud_t * 36.0) * 0.65
        + np.sin(2.0 * np.pi * 210.0 * thud_t) * np.exp(-thud_t * 48.0) * 0.40
    ) * thud_mask
    out_l[c_idx:c_idx + c_len] += swing + stop_thud
    out_r[c_idx:c_idx + c_len] += (swing + stop_thud) * 0.92

    stereo = add_outdoor_reverb(np.column_stack([out_l, out_r]), wet=0.16, rt60=0.45)
    return normalize_to_dbfs(stereo, -5.0)


def synth_foley_beat3_alarm_gong_keng(dur_sec: float = 3.5) -> np.ndarray:
    """
    26.5s - 30.0s: Tiếng kẻng báo động vang lên dồn dập trong đêm (Keng... keng... keng!)
    Authentic Vietnamese military outpost alarm gong (suspended steel bomb casing struck with iron rod).
    """
    rng = np.random.default_rng(405)
    n = int(SR * dur_sec)
    out = np.zeros(n)

    strike_times = [0.05, 0.29, 0.68, 0.92, 1.32, 1.56, 1.80, 2.22, 2.46, 2.70]
    f0 = 830.61  # G#5 bright steel shell casing fundamental

    # Inharmonic steel cylinder modal partials with crisp metallic ring
    partials = [
        (1.000, 5.5, 0.75),
        (1.392, 6.2, 0.62),
        (1.865, 7.5, 0.52),
        (2.440, 9.0, 0.42),
        (3.120, 12.0, 0.30),
        (3.950, 16.0, 0.22),
        (4.880, 22.0, 0.15),
    ]

    for s_i, st_sec in enumerate(strike_times):
        idx = int(st_sec * SR)
        glen = min(n - idx, int(0.95 * SR))
        if glen <= 0:
            continue
        gt = np.arange(glen) / SR
        strike_vel = rng.uniform(0.88, 1.05)

        bell = np.zeros(glen)
        for ratio, decay_rate, amp in partials:
            freq = f0 * ratio * rng.uniform(0.997, 1.003)
            bell += np.sin(2.0 * np.pi * freq * gt) * np.exp(-gt * decay_rate) * amp

        # Sharp iron hammer-on-steel clink transient (1.8 - 7.5 kHz, 8ms)
        clink = fft_bandpass(rng.standard_normal(glen), 1800.0, 7500.0) * np.exp(-gt * 155.0) * 0.75
        out[idx:idx + glen] += (bell + clink) * strike_vel

    out = np.tanh(out * 1.05)
    stereo = add_outdoor_reverb(stereo_pan(out, pan=0.14), wet=0.30, rt60=0.85)
    stereo = fade_in_out(stereo, 0.01, 0.35)
    return normalize_to_dbfs(stereo, -5.5)


def synth_foley_beat4_mud_slog_and_drum(dur_sec: float = 16.0) -> np.ndarray:
    """
    30.0s - 46.0s (Beat 4 - Thế Kẹt Độc Đạo):
    - 0.0s - 10.0s (timeline 30.0s - 40.0s): Heavy boots/feet bogged down in mangrove mud ('lội bùn sình lầy bì bõm')
      using multi-stage filtered noise bursts (zero sine sweeps!).
    - 10.35s (timeline 40.35s, right before 'Chúng kẹt rồi!') & 13.05s (timeline 43.05s, right after):
      Deep tactical war-drum impacts locking in the bottleneck.
    """
    rng = np.random.default_rng(406)
    n = int(SR * dur_sec)
    out_l = np.zeros(n)
    out_r = np.zeros(n)

    # 1. Mangrove mud squelching & sloshing footsteps (0.3s -> 9.8s)
    slog_times = np.arange(0.35, 9.8, 0.64)
    for s_t in slog_times:
        jitter = s_t + rng.uniform(-0.08, 0.08)
        idx = int(jitter * SR)
        mlen = int(0.44 * SR)
        if idx + mlen >= n:
            continue
        mt = np.arange(mlen) / SR
        # Stage A (0.00-0.18s): Heavy foot sinking into thick mud (80-360 Hz thud + 300-1100 Hz splash)
        env_sink = np.sin(np.pi * np.minimum(1.0, mt / 0.18)) * np.exp(-mt * 9.0)
        sink_low = fft_bandpass(brown_noise(mlen, rng), 75.0, 340.0) * env_sink * 0.65
        sink_mid = fft_bandpass(pink_noise(mlen, rng), 300.0, 1150.0) * env_sink * 0.50

        # Stage B (0.18-0.42s): Boot pulling/straining in sticky mud (high-mid wet suction noise 650-2600 Hz)
        env_pull = np.exp(-((mt - 0.27) / 0.075) ** 2)
        pull_suction = fft_bandpass(rng.standard_normal(mlen), 650.0, 2600.0) * env_pull * 0.38

        step_audio = sink_low + sink_mid + pull_suction
        pan = rng.uniform(-0.25, 0.50)
        panned = stereo_pan(step_audio, pan)
        out_l[idx:idx + mlen] += panned[:, 0]
        out_r[idx:idx + mlen] += panned[:, 1]

    # 2. Tactical low war-drum hits at 10.35s (timeline 40.35s) and 13.30s (timeline 43.30s, right after 'Chúng hết đường rồi!')
    for drum_t, drum_gain in [(10.35, 0.85), (13.30, 0.95), (14.65, 0.65)]:
        idx = int(drum_t * SR)
        dlen = int(1.25 * SR)
        if idx + dlen >= n:
            continue
        dt = np.arange(dlen) / SR
        f_sub = 44.0 + 38.0 * np.exp(-dt * 18.0)
        f_body = 88.0 + 52.0 * np.exp(-dt * 22.0)
        sub_hit = np.sin(2.0 * np.pi * np.cumsum(f_sub) / SR) * np.exp(-dt * 4.2) * 0.90
        body_hit = np.sin(2.0 * np.pi * np.cumsum(f_body) / SR) * np.exp(-dt * 7.5) * 0.55
        skin_slap = fft_bandpass(pink_noise(dlen, rng), 160.0, 950.0) * np.exp(-dt * 32.0) * 0.40
        drum = np.tanh((sub_hit + body_hit + skin_slap) * 1.3) * drum_gain
        out_l[idx:idx + dlen] += drum
        out_r[idx:idx + dlen] += drum

    stereo = add_outdoor_reverb(np.column_stack([out_l, out_r]), wet=0.22, rt60=0.80)
    stereo = fade_in_out(stereo, 0.15, 0.35)
    return normalize_to_dbfs(stereo, -6.0)


def synth_foley_beat5_distant_ship_horn(dur_sec: float = 4.0) -> np.ndarray:
    """
    46.0s - 50.0s: Tiếng còi tàu xa xăm mờ dần ngoài khơi.
    Deep marine steel ship horn (G2 98.0 Hz + D3 146.8 Hz + G3 196.0 Hz brassy triad) receding over water.
    """
    rng = np.random.default_rng(407)
    n = int(SR * dur_sec)
    t = np.arange(n, dtype=np.float64) / SR

    # Two distinct ship horn blasts: 0.25s -> 2.15s, and distant echo blast 2.40s -> 3.65s
    env1 = np.clip((t - 0.20) / 0.22, 0.0, 1.0) * np.clip((2.20 - t) / 0.35, 0.0, 1.0)
    env2 = np.clip((t - 2.38) / 0.20, 0.0, 1.0) * np.clip((3.70 - t) / 0.50, 0.0, 1.0) * 0.52
    env = env1 + env2

    doppler = 1.0 - 0.015 * (t / dur_sec)
    f1 = 98.00 * doppler   # G2
    f2 = 146.83 * doppler  # D3

    ph1 = 2.0 * np.pi * np.cumsum(f1) / SR
    ph2 = 2.0 * np.pi * np.cumsum(f2) / SR

    horn = np.zeros(n)
    for h_num, h_amp in [(1, 1.0), (2, 0.78), (3, 0.52), (4, 0.30), (5, 0.16), (6, 0.08)]:
        horn += (np.sin(h_num * ph1) * 0.68 + np.sin(h_num * ph2) * 0.42) * h_amp

    breath = fft_bandpass(pink_noise(n, rng), 120.0, 620.0) * 0.18
    horn_raw = np.tanh((horn * 0.42 + breath) * 1.35) * env
    horn_filtered = fft_bandpass(horn_raw, 70.0, 820.0)

    stereo = add_outdoor_reverb(stereo_pan(horn_filtered, pan=0.22), wet=0.42, rt60=1.35)
    stereo = fade_in_out(stereo, 0.15, 0.35)
    return normalize_to_dbfs(stereo, -8.0)


# ============================================================================
# LAYER 3: BGM GENERATORS (Tension Drone 00-46s & Sáo Trúc / Đàn Bầu 46-60s)
# ============================================================================

def synth_bgm_part1_tension_drone(dur_sec: float = 46.0) -> np.ndarray:
    """
    00.0s - 46.0s: Cinematic dark low drone (D minor: D1, D2, A2, F3) with slow filter breathing
    and subtle low heartbeat pulse that builds tension across Beats 1-4 without masking SFX or TTS.
    """
    rng = np.random.default_rng(501)
    n = int(SR * dur_sec)
    t = np.arange(n, dtype=np.float64) / SR

    # Fundamental frequencies in D minor (D2=73.42 Hz, A2=110.00 Hz, D3=146.83 Hz, F3=174.61 Hz)
    # Slow detuned bowed cello/contrabass ensemble simulation
    drone_l = np.zeros(n)
    drone_r = np.zeros(n)

    voices = [
        (36.71, 0.45, 0.07, 0.0),    # D1 sub
        (73.42, 0.65, 0.11, -0.3),   # D2
        (73.58, 0.55, 0.13, 0.3),    # D2 detuned
        (110.00, 0.42, 0.09, -0.45), # A2 fifth
        (146.83, 0.30, 0.15, 0.45),  # D3 octave
        (174.61, 0.22, 0.08, -0.2),  # F3 minor third
    ]

    for freq, amp, lfo_hz, pan in voices:
        vib = 1.0 + 0.0025 * np.sin(2.0 * np.pi * 4.2 * t + rng.uniform(0, 6.28))
        ph = 2.0 * np.pi * np.cumsum(freq * vib) / SR
        # Rich bowed string waveform (fundamental + soft 2nd & 3rd harmonics modulated by slow LFO)
        lfo = 0.65 + 0.35 * np.sin(2.0 * np.pi * lfo_hz * t + rng.uniform(0, 6.28))
        wave_sig = (np.sin(ph) + 0.35 * np.sin(2.0 * ph) * lfo + 0.15 * np.sin(3.0 * ph) * (1.0 - lfo)) * amp
        panned = stereo_pan(wave_sig, pan)
        drone_l += panned[:, 0]
        drone_r += panned[:, 1]

    # Tension arc across 0-46s:
    # 0-10s (Beat 1): creeping tension (0.55 -> 0.75)
    # 10-20s (Beat 2): action intensity (0.85)
    # 20-30s (Beat 3): urgent pulse (0.80)
    # 30-46s (Beat 4): bottleneck realization (0.95 -> fades smoothly at 44.5-46.0s into sunrise)
    arc = np.ones(n) * 0.70
    arc[:int(10 * SR)] = np.linspace(0.50, 0.78, int(10 * SR))
    arc[int(10 * SR):int(30 * SR)] = 0.82
    arc[int(30 * SR):int(44 * SR)] = 0.95
    arc[int(44 * SR):] = np.linspace(0.95, 0.05, n - int(44 * SR))

    # Subtle dark heartbeat pulse every 1.15s from 2.0s to 40.0s
    pulse_track = np.zeros(n)
    for p_t in np.arange(2.0, 40.0, 1.15):
        for sub_offset, sub_amp in [(0.0, 0.32), (0.24, 0.18)]:
            idx = int((p_t + sub_offset) * SR)
            plen = int(0.18 * SR)
            if idx + plen < n:
                pt = np.arange(plen) / SR
                thump = np.sin(2.0 * np.pi * (58.0 - 110.0 * pt) * pt) * np.exp(-pt * 24.0) * sub_amp
                pulse_track[idx:idx + plen] += thump

    drone_l = fft_bandpass(drone_l, 32.0, 480.0) * arc + pulse_track
    drone_r = fft_bandpass(drone_r, 32.0, 480.0) * arc + pulse_track

    stereo = np.column_stack([drone_l, drone_r])
    stereo = fade_in_out(stereo, 0.8, 1.2)
    return normalize_to_dbfs(stereo, -15.0)


def synth_dan_bau_note(freq_start: float, freq_target: float, dur_sec: float, glide_sec: float = 0.28, vib_depth: float = 0.012) -> np.ndarray:
    """
    Synthesize an expressive Vietnamese Đàn Bầu (monochord) harmonic note with pitch-bend glissando
    and warm vocal-like vibrato.
    """
    n = int(SR * dur_sec)
    t = np.arange(n, dtype=np.float64) / SR

    # Smooth pitch glide from freq_start to freq_target + delayed expressive vibrato
    glide_progress = np.minimum(1.0, t / max(glide_sec, 0.02))
    glide_curve = 0.5 * (1.0 - np.cos(np.pi * glide_progress))
    base_freq = freq_start + (freq_target - freq_start) * glide_curve

    vib_env = np.clip((t - glide_sec * 0.7) / 0.25, 0.0, 1.0)
    vib = 1.0 + vib_depth * vib_env * np.sin(2.0 * np.pi * 5.2 * t)
    inst_freq = base_freq * vib
    phase = 2.0 * np.pi * np.cumsum(inst_freq) / SR

    # Đàn bầu flageolet (harmonic node pluck) timbre: pure fundamental + singing 2nd/3rd harmonics
    attack = np.sin(np.pi * 0.5 * np.minimum(1.0, t / 0.018))
    decay = np.exp(-t * (1.45 / max(dur_sec, 0.8)))
    release = np.clip((dur_sec - t) / 0.12, 0.0, 1.0)
    env = attack * decay * release

    pluck_transient = np.sin(2.0 * phase) * np.exp(-t * 28.0) * 0.35
    tone = (
        np.sin(phase) * 0.78
        + np.sin(2.0 * phase + 0.3) * 0.42 * np.exp(-t * 1.2)
        + np.sin(3.0 * phase + 0.7) * 0.18 * np.exp(-t * 2.2)
        + np.sin(4.0 * phase) * 0.07 * np.exp(-t * 3.5)
    ) * env + pluck_transient

    return tone


def synth_sao_truc_note(freq_start: float, freq_target: float, dur_sec: float, rng: np.random.Generator) -> np.ndarray:
    """
    Synthesize a warm, breathy Vietnamese Sáo Trúc (bamboo flute) note.
    """
    n = int(SR * dur_sec)
    t = np.arange(n, dtype=np.float64) / SR

    glide = 0.5 * (1.0 - np.cos(np.pi * np.minimum(1.0, t / 0.09)))
    base_freq = freq_start + (freq_target - freq_start) * glide
    vib_env = np.clip((t - 0.18) / 0.22, 0.0, 1.0)
    freq = base_freq * (1.0 + 0.008 * vib_env * np.sin(2.0 * np.pi * 4.8 * t))
    phase = 2.0 * np.pi * np.cumsum(freq) / SR

    attack = 0.5 * (1.0 - np.cos(np.pi * np.minimum(1.0, t / 0.08)))
    release = 0.5 * (1.0 - np.cos(np.pi * np.minimum(1.0, (dur_sec - t) / 0.15)))
    sustain = np.exp(-t * 0.35)
    env = attack * release * sustain

    # Flute harmonics + gentle bamboo breath turbulence
    breath = fft_bandpass(pink_noise(n, rng), freq_target * 0.8, freq_target * 3.2) * 0.08
    flute = (
        np.sin(phase) * 0.82
        + np.sin(2.0 * phase) * 0.24
        + np.sin(3.0 * phase) * 0.09
        + breath
    ) * env
    return flute


def synth_bgm_part2_sao_truc_dan_bau(dur_sec: float = 14.0) -> np.ndarray:
    """
    46.0s - 60.0s (Beat 5 - Chân Trời Trống & Hòa Bình Trở Lại):
    Soulful Southern Vietnamese pentatonic melody (Hò - Xự - Xang - Xê - Cống in D: D, F, G, A, C)
    featuring Đàn Bầu and Sáo Trúc over warm acoustic pad chords.
    """
    rng = np.random.default_rng(502)
    n = int(SR * dur_sec)
    t = np.arange(n, dtype=np.float64) / SR

    out_l = np.zeros(n)
    out_r = np.zeros(n)

    # 1. Warm sunrise harmonic pad (D4=293.66, A3=220.00, F3=174.61, C4=261.63 -> resolving to D major/pentatonic warmth)
    pad_freqs = [(146.83, 0.28, -0.25), (220.00, 0.24, 0.25), (293.66, 0.20, -0.15), (329.63, 0.14, 0.20)]
    pad_env = np.clip(t / 2.2, 0.0, 1.0) * np.clip((dur_sec - t) / 1.5, 0.0, 1.0)
    for pf, pamp, ppan in pad_freqs:
        sig = (np.sin(2.0 * np.pi * pf * t) + 0.25 * np.sin(4.0 * np.pi * pf * t)) * pamp * pad_env
        panned = stereo_pan(sig, ppan)
        out_l += panned[:, 0]
        out_r += panned[:, 1]

    # 2. Đàn Bầu lyrical melody (46.8s -> 59.5s, i.e., local 0.8s -> 13.5s)
    # Notes in D pentatonic (D4=293.66, F4=349.23, G4=392.00, A4=440.00, C5=523.25, D5=587.33)
    dan_bau_phrase = [
        # (start_local_sec, f_start, f_target, dur, glide_sec, gain)
        (0.80, 293.66, 440.00, 2.10, 0.35, 0.55),  # Hò -> Xê (D4 -> A4 expressive slide as sun rises)
        (2.85, 440.00, 392.00, 1.75, 0.25, 0.50),  # A4 -> G4
        (4.65, 349.23, 293.66, 2.40, 0.30, 0.42),  # F4 -> D4 (gentle resolve under Line 3 dialogue)
        (7.20, 293.66, 392.00, 1.85, 0.28, 0.45),  # D4 -> G4 (pause between 'Hòn đảo của mình...' and 'sóng lại êm rồi')
        (9.10, 392.00, 440.00, 1.95, 0.32, 0.62),  # G4 -> A4 (swelling up after dialogue ends at 54.28s)
        (10.95, 523.25, 587.33, 2.65, 0.38, 0.65), # C5 -> D5 (peaceful high harmonic resolution over sunrise flag)
    ]

    for st_sec, f_s, f_t, ndur, glide, gain in dan_bau_phrase:
        idx = int(st_sec * SR)
        note = synth_dan_bau_note(f_s, f_t, ndur, glide_sec=glide) * gain
        nlen = min(len(note), n - idx)
        if nlen > 0:
            panned = stereo_pan(note[:nlen], pan=-0.12)
            out_l[idx:idx + nlen] += panned[:, 0]
            out_r[idx:idx + nlen] += panned[:, 1]

    # 3. Sáo Trúc counter-melody (enters warmly at local 3.8s -> 13.6s, timeline 49.8s -> 59.6s)
    sao_phrase = [
        (3.80, 587.33, 659.25, 2.20, 0.30),  # D5 -> E5 gentle breathy phrase
        (8.35, 440.00, 587.33, 2.50, 0.48),  # A4 -> D5 soaring after Line 3 finishes
        (10.80, 587.33, 440.00, 2.80, 0.45), # D5 -> A4 warm close
    ]
    for st_sec, f_s, f_t, ndur, gain in sao_phrase:
        idx = int(st_sec * SR)
        flute = synth_sao_truc_note(f_s, f_t, ndur, rng) * gain
        nlen = min(len(flute), n - idx)
        if nlen > 0:
            panned = stereo_pan(flute[:nlen], pan=0.18)
            out_l[idx:idx + nlen] += panned[:, 0]
            out_r[idx:idx + nlen] += panned[:, 1]

    stereo = add_outdoor_reverb(np.column_stack([out_l, out_r]), wet=0.38, rt60=1.35)
    stereo = fade_in_out(stereo, 0.9, 1.3)
    return normalize_to_dbfs(stereo, -14.0)


# ============================================================================
# TIMELINE PLACEMENT, AUTO-DUCKING & 60S MASTER MIXING
# ============================================================================

def place_clip(canvas: np.ndarray, clip: np.ndarray, start_sec: float, gain_db: float = 0.0) -> None:
    """Add stereo clip onto 60s stereo canvas at start_sec with linear gain from gain_db."""
    idx = int(round(start_sec * SR))
    if idx >= len(canvas):
        return
    gain = 10.0 ** (gain_db / 20.0)
    avail = min(len(clip), len(canvas) - idx)
    if avail > 0:
        canvas[idx:idx + avail] += clip[:avail] * gain


def build_auto_duck_envelope(
    total_samples: int,
    dialogue_windows: list[tuple[float, float, float]],
    attack_sec: float = 0.25,
    release_sec: float = 0.45,
) -> np.ndarray:
    """
    Create a smooth gain multiplier envelope (in linear amplitude) that ducks background tracks
    by `duck_db` during each (start_sec, end_sec, duck_db) window.
    """
    env_db = np.zeros(total_samples, dtype=np.float64)
    t = np.arange(total_samples, dtype=np.float64) / SR

    for start_s, end_s, duck_db in dialogue_windows:
        # Duck curve: smooth cosine ramp down before start_s, hold during speech, ramp up after end_s
        w = np.zeros(total_samples, dtype=np.float64)
        s0 = max(0.0, start_s - attack_sec)
        s1 = start_s
        e0 = end_s
        e1 = min(TOTAL_DUR, end_s + release_sec)

        att_mask = (t >= s0) & (t < s1)
        hold_mask = (t >= s1) & (t <= e0)
        rel_mask = (t > e0) & (t <= e1)

        if np.any(att_mask):
            ph = (t[att_mask] - s0) / max(s1 - s0, 1e-4)
            w[att_mask] = 0.5 * (1.0 - np.cos(np.pi * ph)) * duck_db
        w[hold_mask] = duck_db
        if np.any(rel_mask):
            ph = (t[rel_mask] - e0) / max(e1 - e0, 1e-4)
            w[rel_mask] = 0.5 * (1.0 + np.cos(np.pi * ph)) * duck_db

        env_db = np.minimum(env_db, w)

    return 10.0 ** (env_db / 20.0)


def main():
    print("=== GATE 3: GENERATING AMBIENCE, ACTION FOLEY, BGM & 60S MASTER MIX ===")
    manifest = {
        "episode_id": "EP01",
        "gate": "GATE_3_SFX_BGM_AND_MIX",
        "sample_rate": SR,
        "total_duration_sec": TOTAL_DUR,
        "leveling_standard": {
            "dialogue_tts_target_peak_dbfs": "-3.0 dBFS",
            "action_foley_target_peak_dbfs": "-9.0 to -4.5 dBFS",
            "ambience_bgm_base_dbfs": "-18.0 to -14.0 dBFS",
            "auto_ducking_during_dialogue": "-22.0 dBFS (attenuated by -7dB to -10dB under voice)",
        },
        "layers": {
            "ambience": {},
            "foley": {},
            "bgm": {},
            "stems_and_master": {},
        },
    }

    # 1. Generate Layer 1: Ambience
    print(" -> Synthesizing Layer 1 (Ambience)...")
    amb_1_2 = synth_amb_beat1_2_night_sea_boat(20.5)
    manifest["layers"]["ambience"]["amb_beat1_2_night_sea_boat"] = {
        "timeline_window_sec": [0.0, 20.0],
        "description": "Tiếng máy ghe đuôi tôm (tạch... tạch... xập xình), sóng biển đêm vỗ mạn gỗ & gió biển rít nhẹ",
        **save_wav_and_mp3(
            amb_1_2,
            SFX_DIR / "amb_beat1_2_night_sea_boat.wav",
            SFX_DIR / "amb_beat1_2_night_sea_boat.mp3",
        ),
    }

    amb_3_4 = synth_amb_beat3_4_night_coastal_swamp(26.5)
    manifest["layers"]["ambience"]["amb_beat3_4_night_coastal_swamp"] = {
        "timeline_window_sec": [20.0, 46.0],
        "description": "Tiếng gió đêm lùa tán dừa/rừng đước, tiếng sóng xa và côn trùng đêm Phú Quốc",
        **save_wav_and_mp3(
            amb_3_4,
            SFX_DIR / "amb_beat3_4_night_coastal_swamp.wav",
            SFX_DIR / "amb_beat3_4_night_coastal_swamp.mp3",
        ),
    }

    amb_5 = synth_amb_beat5_sunrise_calm_sea(14.0)
    manifest["layers"]["ambience"]["amb_beat5_sunrise_calm_sea"] = {
        "timeline_window_sec": [46.0, 60.0],
        "description": "Tiếng sóng biển bình minh hiền hòa vỗ bờ cát & gió sớm",
        **save_wav_and_mp3(
            amb_5,
            SFX_DIR / "amb_beat5_sunrise_calm_sea.wav",
            SFX_DIR / "amb_beat5_sunrise_calm_sea.mp3",
        ),
    }

    # 2. Generate Layer 2: Frame-Accurate Action Foley
    print(" -> Synthesizing Layer 2 (Frame-Accurate Action Foley)...")
    foley_bop = synth_foley_beat2_tiller_hit_bop(1.55)
    manifest["layers"]["foley"]["foley_beat2_tiller_hit_bop"] = {
        "timeline_start_sec": 10.90,
        "impact_peak_sec": 11.20,
        "description": "Nhịp 2 (10.9s–12.45s): Tiếng vung cần lái gỗ nghiến cực mạnh (VÚT – BỐP! / RẦM! tại 11.20s), tiếng ngã nhào lên ván ghe & súng AK văng",
        **save_wav_and_mp3(
            foley_bop,
            SFX_DIR / "foley_beat2_tiller_hit_bop.wav",
            SFX_DIR / "foley_beat2_tiller_hit_bop.mp3",
        ),
    }

    foley_um = synth_foley_beat2_water_plunge_um(3.5)
    manifest["layers"]["foley"]["foley_beat2_water_plunge_um"] = {
        "timeline_start_sec": 12.15,
        "impact_peak_sec": 12.50,
        "description": "Nhịp 2 (12.15s–15.65s): Tiếng đạp mạn ghe bỏ thuyền (CỘP! RẮC!), 2 cú lao mình xuống biển đêm (ÙM! ÀO! tại 12.50s & 12.83s) và tiếng sải bơi thoát thân",
        **save_wav_and_mp3(
            foley_um,
            SFX_DIR / "foley_beat2_water_plunge_um.wav",
            SFX_DIR / "foley_beat2_water_plunge_um.mp3",
        ),
    }

    foley_ak = synth_foley_beat2_ak47_bursts_distant(5.5)
    manifest["layers"]["foley"]["foley_beat2_ak47_bursts_distant"] = {
        "timeline_start_sec": 14.00,
        "description": "Nhịp 2 (14.0s–19.5s): 3 loạt súng AK điểm xạ trên bờ cát rồi xa dần khi lặn sâu dưới nước",
        **save_wav_and_mp3(
            foley_ak,
            SFX_DIR / "foley_beat2_ak47_bursts_distant.wav",
            SFX_DIR / "foley_beat2_ak47_bursts_distant.mp3",
        ),
    }

    foley_knock = synth_foley_beat3_footsteps_and_door_knock(2.45)
    manifest["layers"]["foley"]["foley_beat3_footsteps_and_door_knock"] = {
        "timeline_start_sec": 20.00,
        "description": "Nhịp 3 (20.0s–22.4s): Tiếng bước chân trần chạy gấp, đập cửa gỗ dồn dập (Cộc! Cộc! Cộc!) & mở toang cửa",
        **save_wav_and_mp3(
            foley_knock,
            SFX_DIR / "foley_beat3_footsteps_and_door_knock.wav",
            SFX_DIR / "foley_beat3_footsteps_and_door_knock.mp3",
        ),
    }

    foley_gong = synth_foley_beat3_alarm_gong_keng(3.5)
    manifest["layers"]["foley"]["foley_beat3_alarm_gong_keng"] = {
        "timeline_start_sec": 26.50,
        "description": "Nhịp 3 (26.5s–30.0s): Tiếng kẻng báo động vỏ bom vang lên dồn dập trong đêm (Keng! Keng! Keng!)",
        **save_wav_and_mp3(
            foley_gong,
            SFX_DIR / "foley_beat3_alarm_gong_keng.wav",
            SFX_DIR / "foley_beat3_alarm_gong_keng.mp3",
        ),
    }

    foley_mud = synth_foley_beat4_mud_slog_and_drum(16.0)
    manifest["layers"]["foley"]["foley_beat4_mud_slog_and_drum"] = {
        "timeline_start_sec": 30.00,
        "description": "Nhịp 4 (30.0s–46.0s): Tiếng lội bùn sình lầy bì bõm ở rễ đước & nhịp trống trầm khóa chặt thế trận",
        **save_wav_and_mp3(
            foley_mud,
            SFX_DIR / "foley_beat4_mud_slog_and_drum.wav",
            SFX_DIR / "foley_beat4_mud_slog_and_drum.mp3",
        ),
    }

    foley_horn = synth_foley_beat5_distant_ship_horn(4.0)
    manifest["layers"]["foley"]["foley_beat5_distant_ship_horn"] = {
        "timeline_start_sec": 46.00,
        "description": "Nhịp 5 (46.0s–50.0s): Tiếng còi tàu sắt xa xăm mờ dần ngoài khơi khi rút lui",
        **save_wav_and_mp3(
            foley_horn,
            SFX_DIR / "foley_beat5_distant_ship_horn.wav",
            SFX_DIR / "foley_beat5_distant_ship_horn.mp3",
        ),
    }

    # 3. Generate Layer 3: BGM
    print(" -> Synthesizing Layer 3 (BGM: Tension Drone 00-46s & Sáo Trúc / Đàn Bầu 46-60s)...")
    bgm_1 = synth_bgm_part1_tension_drone(46.5)
    manifest["layers"]["bgm"]["bgm_part1_tension_drone_00_46s"] = {
        "timeline_window_sec": [0.0, 46.0],
        "description": "Nhạc nền nửa đầu (00–46s): Drone trầm căng thẳng (D minor) kết hợp nhịp tim trầm sâu",
        **save_wav_and_mp3(
            bgm_1,
            BGM_DIR / "bgm_part1_tension_drone_00_46s.wav",
            BGM_DIR / "bgm_part1_tension_drone_00_46s.mp3",
        ),
    }

    bgm_2 = synth_bgm_part2_sao_truc_dan_bau(14.0)
    manifest["layers"]["bgm"]["bgm_part2_sao_truc_dan_bau_46_60s"] = {
        "timeline_window_sec": [46.0, 60.0],
        "description": "Nhạc nền nửa cuối (46–60s): Giai điệu ngũ cung Đàn Bầu & Sáo Trúc mộc mạc, sâu lắng lúc bình minh",
        **save_wav_and_mp3(
            bgm_2,
            BGM_DIR / "bgm_part2_sao_truc_dan_bau_46_60s.wav",
            BGM_DIR / "bgm_part2_sao_truc_dan_bau_46_60s.mp3",
        ),
    }

    # 4. Assemble 60.0s Stems & Auto-Ducked Master Mix
    print(" -> Assembling 60.0s Multi-Stem Timeline & Applying Auto-Ducking...")
    stem_dialogue = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float64)
    stem_ambience = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float64)
    stem_foley = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float64)
    stem_bgm = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float64)

    # Load verified Gate 2 TTS lines
    tts_line1 = read_wav_stereo(TTS_DIR / "line1_beat3_nguoi_chai_tre.wav")
    tts_line2 = read_wav_stereo(TTS_DIR / "line2_beat4_nguoi_truc_dem.wav")
    tts_line3 = read_wav_stereo(TTS_DIR / "line3_beat5_lao_chai.wav")

    # Place Dialogue at exact motion_plan.json timestamps (already peaking at -3.0 dBFS)
    place_clip(stem_dialogue, tts_line1, start_sec=22.50, gain_db=0.0)
    place_clip(stem_dialogue, tts_line2, start_sec=41.00, gain_db=0.0)
    place_clip(stem_dialogue, tts_line3, start_sec=50.50, gain_db=0.0)

    # Place Ambience with smooth overlaps
    place_clip(stem_ambience, amb_1_2, start_sec=0.00, gain_db=0.0)
    place_clip(stem_ambience, amb_3_4, start_sec=19.80, gain_db=0.0)
    place_clip(stem_ambience, amb_5, start_sec=45.80, gain_db=0.0)

    # Place Action Foley cues at exact timestamps (Beat 2 tiller strike & water plunge boosted +2.8 dB for maximum impact)
    place_clip(stem_foley, foley_bop, start_sec=10.90, gain_db=2.8)
    place_clip(stem_foley, foley_um, start_sec=12.15, gain_db=2.8)
    place_clip(stem_foley, foley_ak, start_sec=14.00, gain_db=0.0)
    place_clip(stem_foley, foley_knock, start_sec=20.00, gain_db=0.0)
    place_clip(stem_foley, foley_gong, start_sec=26.50, gain_db=0.0)
    place_clip(stem_foley, foley_mud, start_sec=30.00, gain_db=0.0)
    place_clip(stem_foley, foley_horn, start_sec=46.00, gain_db=0.0)

    # Place BGM parts with crossfade around 46.0s
    place_clip(stem_bgm, bgm_1, start_sec=0.00, gain_db=0.0)
    place_clip(stem_bgm, bgm_2, start_sec=45.80, gain_db=0.0)

    # Apply Auto-Ducking to Ambience and BGM during:
    # - Beat 2 Action Climax (10.85s - 15.80s: tiller strike & abandoning boat) so BỐP! and ÙM! explode out of the mix
    # - All 3 Dialogue Windows
    dialogue_windows_bgm = [
        (10.85, 15.80, -10.5),  # Beat 2 Action Climax: Đánh cần lái & bỏ thuyền
        (22.40, 26.05, -9.5),   # Line 1: Người chài trẻ
        (40.90, 43.30, -10.0),  # Line 2: Người trực đêm ('Chúng hết đường rồi!')
        (50.40, 54.40, -9.5),   # Line 3: Lão chài
    ]
    dialogue_windows_amb = [
        (10.85, 15.80, -10.0),  # Beat 2 Action Climax: Hạ sâu nền sóng/máy ghe để tôn cú đánh & nhảy biển
        (22.40, 26.05, -6.5),
        (40.90, 43.30, -7.0),
        (50.40, 54.40, -6.5),
    ]

    duck_bgm = build_auto_duck_envelope(TOTAL_SAMPLES, dialogue_windows_bgm)
    duck_amb = build_auto_duck_envelope(TOTAL_SAMPLES, dialogue_windows_amb)

    stem_bgm *= duck_bgm[:, None]
    stem_ambience *= duck_amb[:, None]

    # Save individual 60s stems
    manifest["layers"]["stems_and_master"]["stem_dialogue_60s"] = save_wav_and_mp3(
        stem_dialogue, MIX_DIR / "stem_dialogue_60s.wav"
    )
    manifest["layers"]["stems_and_master"]["stem_ambience_60s"] = save_wav_and_mp3(
        stem_ambience, MIX_DIR / "stem_ambience_60s.wav"
    )
    manifest["layers"]["stems_and_master"]["stem_foley_60s"] = save_wav_and_mp3(
        stem_foley, MIX_DIR / "stem_foley_60s.wav"
    )
    manifest["layers"]["stems_and_master"]["stem_bgm_60s"] = save_wav_and_mp3(
        stem_bgm, MIX_DIR / "stem_bgm_60s.wav"
    )

    # Combine all 4 stems into the 60.0s Master Soundtrack
    master_raw = stem_dialogue + stem_foley + stem_ambience + stem_bgm
    # Transparent soft-knee brickwall limiter above 0.72 (-2.85 dBFS) up to ceiling 0.89 (-1.0 dBFS)
    # so action peaks hit hard at -1.2 dBFS without scaling down the rest of the timeline!
    abs_m = np.abs(master_raw)
    knee = 0.72
    ceil_headroom = 0.17
    master_raw = np.where(
        abs_m > knee,
        np.sign(master_raw) * (knee + ceil_headroom * np.tanh((abs_m - knee) / ceil_headroom)),
        master_raw,
    )

    manifest["layers"]["stems_and_master"]["master_audio_ep01_v6_60s"] = save_wav_and_mp3(
        master_raw,
        MIX_DIR / "master_audio_ep01_v6_60s.wav",
        MIX_DIR / "master_audio_ep01_v6_60s.mp3",
    )

    manifest_path = MIX_DIR / "audio_manifest_gate3.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Done! Manifest saved to {manifest_path}")


if __name__ == "__main__":
    main()
