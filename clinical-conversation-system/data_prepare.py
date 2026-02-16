import pandas as pd
import json


def convert_train_data(csv_path, json_path):
    try:
        # 1. Load your train.csv
        df = pd.read_csv(csv_path)

        # 2. Map 'dialogue' to 'transcript' and keep 'summary'
        with open(json_path, 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                # We use .get() or check for NaN to avoid crashes
                dialogue = str(row['dialogue']) if pd.notnull(row['dialogue']) else ""
                summary = str(row['summary']) if pd.notnull(row['summary']) else ""

                if dialogue and summary:
                    entry = {
                        "transcript": dialogue,
                        "summary": summary
                    }
                    f.write(json.dumps(entry) + '\n')

        print(f"✅ SUCCESS: Converted {len(df)} training samples.")
    except Exception as e:
        print(f"❌ ERROR: {e}")


# Run this now!
convert_train_data('data/processed/train.csv', 'clinical_data.json')
convert_train_data('data/processed/test.csv', 'clinical_test.json')