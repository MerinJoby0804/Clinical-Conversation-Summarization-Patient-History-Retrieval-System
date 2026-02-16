import json

print("🔧 CLEANING AND FILTERING DATA...")

# Fix training data
print("\n1. Processing clinical_data.json...")
with open('clinical_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"   Original samples: {len(data)}")

# Filter out bad samples
good_data = []
removed = 0

for i, sample in enumerate(data):
    transcript = sample.get('transcript', '').strip()
    summary = sample.get('summary', '').strip()

    # Filter criteria
    if len(transcript) < 50:
        print(f"   ❌ Removed sample {i}: transcript too short ({len(transcript)} chars)")
        removed += 1
        continue

    if len(summary) < 30:
        print(f"   ❌ Removed sample {i}: summary too short ({len(summary)} chars)")
        removed += 1
        continue

    if summary.lower() in ['none', 'none.', 'noncontributory', 'noncontributory.']:
        print(f"   ❌ Removed sample {i}: useless summary ('{summary}')")
        removed += 1
        continue

    good_data.append(sample)

print(f"   ✅ Kept: {len(good_data)} samples")
print(f"   ❌ Removed: {removed} samples")

# Save cleaned data
with open('clinical_data.json', 'w', encoding='utf-8') as f:
    json.dump(good_data, f, indent=2, ensure_ascii=False)

# Fix test data
print("\n2. Processing clinical_test.json...")
with open('clinical_test.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"   Original samples: {len(data)}")

good_data = []
removed = 0

for i, sample in enumerate(data):
    transcript = sample.get('transcript', '').strip()
    summary = sample.get('summary', '').strip()

    if len(transcript) < 50 or len(summary) < 30:
        removed += 1
        continue

    if summary.lower() in ['none', 'none.', 'noncontributory', 'noncontributory.']:
        removed += 1
        continue

    good_data.append(sample)

print(f"   ✅ Kept: {len(good_data)} samples")
print(f"   ❌ Removed: {removed} samples")

with open('clinical_test.json', 'w', encoding='utf-8') as f:
    json.dump(good_data, f, indent=2, ensure_ascii=False)

# Verify
print("\n✅ DATA CLEANED!")
print("\n🔍 Verification:")

with open('clinical_data.json', 'r', encoding='utf-8') as f:
    train = json.load(f)
with open('clinical_test.json', 'r', encoding='utf-8') as f:
    test = json.load(f)

print(f"   Training: {len(train)} samples")
print(f"   Test: {len(test)} samples")

# Show min/max/avg lengths
train_transcript_lens = [len(s['transcript']) for s in train]
train_summary_lens = [len(s['summary']) for s in train]

print(f"\n   Training data stats:")
print(
    f"   Transcript: min={min(train_transcript_lens)}, max={max(train_transcript_lens)}, avg={sum(train_transcript_lens) / len(train):.0f}")
print(
    f"   Summary: min={min(train_summary_lens)}, max={max(train_summary_lens)}, avg={sum(train_summary_lens) / len(train):.0f}")

print("\n✅ ALL DONE! Data is now clean and ready for training.")