import torch
import os
import pandas as pd
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from rouge_score import rouge_scorer

# =========================================================
# 🔧 EMERGENCY FIX: HARDCODED PATH
# =========================================================
# Your model is definitely at:
# C:\Users\sreen\OneDrive\Documents\clinical-conversation-system\final_clinical_model

# Use ABSOLUTE PATH (no path calculations - just hardcode it!)
model_path = r"C:\Users\sreen\OneDrive\Documents\clinical-conversation-system\final_clinical_model"
test_data_path = r"C:\Users\sreen\OneDrive\Documents\clinical-conversation-system\clinical_test.json"
csv_output_path = r"C:\Users\sreen\OneDrive\Documents\clinical-conversation-system\ai_training\VERIFIED_AI_REPORT.csv"

device = "cuda" if torch.cuda.is_available() else "cpu"

print("=" * 60)
print("🔍 EVALUATION SETUP - EMERGENCY FIX")
print("=" * 60)
print(f"System: {device.upper()}")
print(f"Model path: {model_path}")
print(f"Model exists: {os.path.exists(model_path)}")
print(f"Data path: {test_data_path}")
print(f"Data exists: {os.path.exists(test_data_path)}")
print(f"CSV output: {csv_output_path}")

# =========================================================
# 2. VERIFY MODEL EXISTS
# =========================================================
if not os.path.exists(model_path):
    print(f"\n❌ ERROR: Model not found at {model_path}")
    raise FileNotFoundError(f"Model not found: {model_path}")

if not os.path.exists(test_data_path):
    print(f"\n❌ ERROR: Test data not found at {test_data_path}")
    raise FileNotFoundError(f"Test data not found: {test_data_path}")

# List model files
print(f"\n📁 Files in model directory:")
for file in os.listdir(model_path):
    file_path = os.path.join(model_path, file)
    if os.path.isfile(file_path):
        size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        print(f"   - {file} ({size:.1f} MB)")

print("=" * 60)

# =========================================================
# 3. LOAD MODEL
# =========================================================
print(f"\n✅ Loading model from: {model_path}")
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSeq2SeqLM.from_pretrained(model_path).to(device)

# 🔍 CRITICAL DEBUG INFO
print(f"✅ Model loaded successfully!")
print(f"   Model config._name_or_path: {model.config._name_or_path}")
print(f"   Model type: {type(model).__name__}")
print(f"   Device: {device}")

# Check if it's the base model or fine-tuned
if "biobart-base" in str(model.config._name_or_path).lower() and "final_clinical_model" not in str(
        model.config._name_or_path):
    print(f"   ⚠️  WARNING: This looks like BASE model!")
else:
    print(f"   ✅ This is your FINE-TUNED model!")

dataset = load_dataset("json", data_files={"test": test_data_path})["test"]
print(f"   Test samples: {len(dataset)}")

# =========================================================
# 4. TEST GENERATION ON ONE SAMPLE FIRST
# =========================================================
print("\n" + "=" * 60)
print("🧪 TESTING GENERATION ON ONE SAMPLE")
print("=" * 60)

test_sample = dataset[0]
print(f"Input (first 200 chars): {test_sample['transcript'][:200]}...")

inputs = tokenizer(
    test_sample["transcript"],
    padding="max_length",
    truncation=True,
    max_length=512,
    return_tensors="pt"
).to(device)

with torch.no_grad():
    outputs = model.generate(
        input_ids=inputs.input_ids,
        attention_mask=inputs.attention_mask,
        max_new_tokens=150,
        min_length=30,
        num_beams=4,
        length_penalty=2.0,
        early_stopping=True
    )

test_output = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
print(f"\nGenerated output: {test_output}")
print(f"Output length: {len(test_output)} characters")
print(f"Reference (first 200 chars): {test_sample['summary'][:200]}...")

if len(test_output) < 20:
    print("\n❌ WARNING: Generated output is TOO SHORT!")
    print("   This indicates a problem with the model or generation parameters")
else:
    print("\n✅ Output length looks reasonable")

print("=" * 60)


# =========================================================
# 5. FULL INFERENCE
# =========================================================
def generate_summary(batch):
    inputs = tokenizer(
        batch["transcript"],
        padding="max_length",
        truncation=True,
        max_length=512,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_new_tokens=150,
            min_length=30,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )

    batch["ai_summary"] = [tokenizer.decode(g, skip_special_tokens=True).strip() for g in outputs]
    return batch


print("\n📊 Generating summaries for all samples...")
results = dataset.map(generate_summary, batched=True, batch_size=4)

# =========================================================
# 6. SCORING
# =========================================================
scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
r1, r2, rl = 0, 0, 0
n = len(results)

# Preview first 3 summaries
print("\n" + "=" * 60)
print("📄 SAMPLE OUTPUTS")
print("=" * 60)
for i in range(min(3, n)):
    print(f"\n[SAMPLE {i + 1}]")
    print(f"REFERENCE: {results['summary'][i][:150]}...")
    print(f"AI OUTPUT: {results['ai_summary'][i][:150]}...")
    print(f"AI LENGTH: {len(results['ai_summary'][i])} chars")

# Calculate ROUGE scores
for p, r in zip(results["ai_summary"], results["summary"]):
    scores = scorer.score(str(r), str(p))
    r1 += scores['rouge1'].fmeasure
    r2 += scores['rouge2'].fmeasure
    rl += scores['rougeL'].fmeasure

print("\n" + "=" * 60)
print("📈 ROUGE SCORES")
print("=" * 60)
print(f"ROUGE-1: {r1 / n:.4f}")
print(f"ROUGE-2: {r2 / n:.4f}")
print(f"ROUGE-L: {rl / n:.4f}")
print("=" * 60)

if r1 / n < 0.10:
    print("\n⚠️  ROUGE scores are very low!")
    print("   Checking potential issues:")

    # Check output lengths
    avg_length = sum(len(s) for s in results["ai_summary"]) / n
    print(f"   Average output length: {avg_length:.1f} characters")

    if avg_length < 50:
        print("   ❌ Outputs are too short! Model may not be generating properly.")

    # Check for repeated outputs
    unique_outputs = len(set(results["ai_summary"]))
    print(f"   Unique outputs: {unique_outputs}/{n}")

    if unique_outputs < n * 0.5:
        print("   ❌ Many duplicate outputs! Model may be stuck.")

elif r1 / n < 0.25:
    print("\n⚠️  ROUGE scores are lower than expected.")
    print("   Consider retraining with more epochs.")
else:
    print("\n✅ ROUGE scores look good!")

# =========================================================
# 7. SAVE RESULTS
# =========================================================
df = pd.DataFrame({
    "Human_Reference": results["summary"],
    "AI_Summary": results["ai_summary"]
})
df.to_csv(csv_output_path, index=False)
print(f"\n✅ SUCCESS! File created: {csv_output_path}")