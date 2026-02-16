import whisper
import pandas as pd
import os
from jiwer import wer

# 1. SETUP
# Use 'small' or 'medium' for better medical accuracy if your GPU can handle it
model = whisper.load_model("base")
REFERENCE_CSV = "data/processed/local_test.csv"
AUDIO_DIR = r"C:/Users/sreen/Downloads/archive/audio_recordings/Audio_Recordings"

# 2. LOAD YOUR "TRUTH" DATA
df = pd.read_csv(REFERENCE_CSV)
results = []

print(f"🎙️ Starting WER Analysis for {len(df)} files...")

# 3. TRANSCRIPTION & COMPARISON LOOP
for index, row in df.iterrows():
    audio_id = row['audio_id']
    audio_path = os.path.join(AUDIO_DIR, f"{audio_id}.mp3")  # Change to .wav if needed

    if not os.path.exists(audio_path):
        continue

    # Whisper hears the audio
    audio_result = model.transcribe(audio_path)
    predicted_text = audio_result["text"].strip()
    reference_text = row['transcript'].strip()

    # Calculate WER for this specific file
    error_rate = wer(reference_text, predicted_text)

    results.append({
        "audio_id": audio_id,
        "reference": reference_text,
        "whisper_output": predicted_text,
        "wer": error_rate
    })

    print(f"✅ Processed {audio_id} | WER: {error_rate:.2f}")

# 4. SAVE & SUMMARIZE
results_df = pd.DataFrame(results)
avg_wer = results_df['wer'].mean()

results_df.to_csv("data/processed/whisper_accuracy_report.csv", index=False)

print("-" * 30)
print(f"📊 FINAL AVERAGE WER: {avg_wer:.4f}")
print(f"📁 Detailed report saved to data/processed/whisper_accuracy_report.csv")