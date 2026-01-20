---
tags: [operations, troubleshooting, error]
---

# 🔧 Troubleshooting Guide

## 🚨 Common Startup Errors

### CUDA Out of Memory (OOM)
**Symptoms**:
```text
torch.OutOfMemoryError: CUDA out of memory. Tried to allocate 20.00 MiB.
```
**Cause**:
Running Llama 3.1 8B (approx 5GB VRAM) alongside Whisper (approx 1GB VRAM) on a 6GB card (RTX 3050/3060) leads to saturation.

**Fix**:
We force Whisper to run on **CPU** in `core/adaptive_asr.py`.
```python
# core/adaptive_asr.py
device = "cpu" # Force CPU for Whisper
```
*Impact*: STT takes 0.5s longer, but the text generation (LLM) stays fast on GPU.

### ALSA / Audio Errors
**Symptoms**:
```text
[Errno -9998] Invalid number of channels
```
**Fix**:
1. Run `aplay -l` to see devices.
2. Reset PulseAudio: `pulseaudio -k && pulseaudio --start`

## 🎙️ Recognition Issues
**Symptoms**: "It keeps hearing silence" or "It types output while I am still speaking."

**Fix**:
Tweak `A1/core/adaptive_asr.py`:
- `THRESHOLD`: Lower to `300` for sensitive mics.
- `SILENCE_LIMIT`: Increase to `2.5` to allow pauses in speech.
- `prompt`: Ensure the "Vocabulary List" is simple (see `tanglish_vocab` variable).

## 🗣️ TTS Issues
**Symptoms**: "Static noise when speaking Tamil."
**Fix**:
A1 currently **cannot** speak native Tamil script. It only speaks English/Tanglish in Roman script.
- *Bad*: "வணக்கம்"
- *Good*: "Vanakkam"
