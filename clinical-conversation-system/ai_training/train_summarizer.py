import os

# 🔧 FORCE CPU ONLY (no CUDA issues)
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import torch
import json
import numpy as np
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    BartForConditionalGeneration,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer
)

try:
    from evaluate import load as load_metric
except ImportError:
    from datasets import load_metric

# =========================================================
# 🔧 CPU-ONLY TRAINING (100% STABLE)
# =========================================================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

train_path = os.path.join(PROJECT_ROOT, "clinical_data.json")
val_path = os.path.join(PROJECT_ROOT, "clinical_test.json")
MODEL_SAVE_PATH = os.path.join(PROJECT_ROOT, "final_clinical_model")

print("=" * 80)
print("🚀 CPU-ONLY TRAINING (NO CUDA ISSUES)")
print("=" * 80)
print(f"CUDA Available: {torch.cuda.is_available()} (Disabled)")
print(f"PyTorch Version: {torch.__version__}")
print(f"Training data: {train_path}")
print(f"Validation data: {val_path}")
print(f"Model save path: {MODEL_SAVE_PATH}")
print("\n⚠️  Training on CPU will be SLOWER (2-3 hours) but 100% STABLE")
print("=" * 80)

# Load data
with open(train_path, 'r', encoding='utf-8') as f:
    train_data = json.load(f)
with open(val_path, 'r', encoding='utf-8') as f:
    val_data = json.load(f)

print(f"\n✅ Training samples: {len(train_data)}")
print(f"✅ Validation samples: {len(val_data)}")

# Load model
model_name = "GanjinZero/biobart-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)

print(f"✅ Model loaded: {model_name}")

# Load dataset
data_files = {"train": train_path, "validation": val_path}
dataset = load_dataset("json", data_files=data_files)


def preprocess_function(examples):
    model_inputs = tokenizer(
        examples["transcript"],
        max_length=512,
        truncation=True,
        padding="max_length"
    )
    labels = tokenizer(
        text_target=examples["summary"],
        max_length=128,
        truncation=True,
        padding="max_length"
    )
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


tokenized_train = dataset["train"].map(preprocess_function, batched=True, remove_columns=["transcript", "summary"])
tokenized_val = dataset["validation"].map(preprocess_function, batched=True, remove_columns=["transcript", "summary"])

data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# Ultra-safe training args
training_args = Seq2SeqTrainingArguments(
    output_dir=os.path.join(PROJECT_ROOT, "biobart-clinical-finetuned"),
    eval_strategy="epoch",
    save_strategy="epoch",
    save_total_limit=1,

    # Safe settings
    learning_rate=2e-5,
    num_train_epochs=3,
    weight_decay=0.01,
    warmup_steps=50,  # Use steps instead of ratio
    max_grad_norm=1.0,

    # Batch
    per_device_train_batch_size=2,  # Can be higher on CPU
    per_device_eval_batch_size=2,
    gradient_accumulation_steps=4,

    # NO mixed precision on CPU
    bf16=False,
    fp16=False,

    # Generation
    load_best_model_at_end=True,
    metric_for_best_model="rouge1",
    greater_is_better=True,
    predict_with_generate=True,
    generation_max_length=128,
    generation_num_beams=4,

    # Logging
    logging_steps=20,
    report_to="none",
    save_only_model=True,
)

print("✅ Training config created (CPU-ONLY)")

# Metrics
rouge_metric = load_metric("rouge")


def compute_metrics(eval_pred):
    predictions, labels = eval_pred
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    result = rouge_metric.compute(
        predictions=decoded_preds,
        references=decoded_labels,
        use_stemmer=True
    )

    return {
        "rouge1": result["rouge1"],
        "rouge2": result["rouge2"],
        "rougeL": result["rougeL"],
    }


# Create trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    processing_class=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

print("\n" + "=" * 80)
print("🔥 STARTING CPU TRAINING")
print("=" * 80)
print("⏰ This will take 2-3 HOURS on CPU (be patient!)")
print("📊 Loss should decrease gradually: 6 → 5 → 4 → 3 → 2")
print("=" * 80 + "\n")

# Train
trainer.train()

# Evaluate
eval_results = trainer.evaluate()
print(f"\n✅ ROUGE-1: {eval_results['eval_rouge1']:.4f}")

# Save
trainer.save_model(MODEL_SAVE_PATH)
tokenizer.save_pretrained(MODEL_SAVE_PATH)

print(f"\n✅ Model saved to: {MODEL_SAVE_PATH}")
print("🎉 TRAINING COMPLETE!")