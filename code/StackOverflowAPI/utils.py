"""
ⓒ Debug.Ai 2025 Eshan Jayasundara

This file contains utility functions for all the dependent python scripts.
"""


import re
from typing import List, Dict, Any, Annotated
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import pandas as pd
from datasets import load_dataset, Dataset

def clean_text(text: str) -> str:
    """Convert multi-line text into a single line by removing extra spaces and newlines."""
    text = re.sub(r'\s+', ' ', text).strip()  # Replace multiple spaces/newlines with a single space
    clean_text = BeautifulSoup(text, "html.parser").get_text()
    return clean_text

def str_to__midnight_utc(str_date: Annotated[str, "Format: YYYY-MM-DD"]) -> int:
    """Convert a string to unix time format rlative to midnight UTC timestamp."""
    year, month, day = list(map(int, str_date.strip().split("-")))
    return int(datetime(year=year, month=month, day=day, tzinfo=timezone.utc).timestamp())

def midnight_utc_to_str(timestamp: int) -> Annotated[str, "Format: YYYY-MM-DD"]:
    """Convert a unix time timestamp midnight UTC to a string."""
    date = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return f"{date.year}-{date.month}-{date.day}"

def update_huggingface_dataset(new_data_df: pd.DataFrame, username:str, dataset_name: str, split:str):
    try:
        existing_dataset = load_dataset(f"{username}/{dataset_name}", split=split)
        existing_df = pd.DataFrame(existing_dataset)

        if existing_df.empty:
            print("⚠️ Existing dataset is empty. Creating a new dataset.")
            updated_df = new_data_df
        else:
            updated_df = pd.concat([existing_df, new_data_df], ignore_index=True)
    except Exception as e:
        # print(f"ℹ️ Could not load existing dataset. Starting fresh. (Error: {e})")
        print(f"ℹ️ Could not load existing dataset. Starting fresh.")
        updated_df = new_data_df

    # Convert final DataFrame to Hugging Face Dataset and push to hub
    if not updated_df.empty:
        dataset = Dataset.from_pandas(updated_df)
        dataset.push_to_hub(f"{username}/{dataset_name}")
        print(f"✅ Successfully updated dataset: {username}/{dataset_name}")
    else:
        print("❌ No data available to upload.")