---
tags: [configuration, audio, biometrics]
---

# 🎙️ Configuration: Voice Enrollment

This guide details how the **Speaker Identification** system works and how to train it.

## 🧬 Biometric Technology
We use **SpeechBrain** with the **ECAPA-TDNN** model.
-   **Input**: Waveform audio.
-   **Output**: 192-dimensional vector (The "Voice Print").
-   **Verification**: We calculate the Cosine Similarity between the live vector and the enrolled vector.

## 🛠️ Enrollment Process (`voice_enroll.py`)

1.  **Start**: Run the script. It initializes the microphone.
2.  **Prompt 1**: "Please speak: *The quick brown fox jumps over the lazy dog.*"
    -   Captures wide phonetic range.
3.  **Prompt 2**: "Please speak: *Hey A1, open the terminal and update the system.*"
    -   Captures command-specific intonation.
4.  **Prompt 3**: "Please speak: *Identify me securely.*"
5.  **Averaging**: The 3 vectors are averaged to create a robust `user_profile.npy`.

## 📊 Threshold Tuning
You can tweak the strictness in `core/adaptive_asr.py`:

```python
VERIFICATION_THRESHOLD = 0.75
```
-   **0.60**: Loose. May accept similar sounding people.
-   **0.75**: Balanced. (Default)
-   **0.85**: Strict. May reject you if you have a cold.

## 📂 Storage
The profile is stored at: `A1/models/user_profile.npy`
**Delete this file** to reset the enrollment.
