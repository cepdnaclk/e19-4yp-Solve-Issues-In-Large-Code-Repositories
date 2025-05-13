## Main File: `main.py`

This is the primary script that combines multiple components and performs the required operations for fetching, processing, and updating data.

### Functionality:

- **Data Fetching:** The script fetches question-answer pairs using the `get_question_answer_pairs()` function from the `api_call.py` file. It retrieves data for specified date ranges, such as from December 18th, 2024, to December 25th, 2024.
  
- **Data Processing:** The fetched data is processed and combined into a pandas DataFrame. It utilizes the `ThreadPoolExecutor` for concurrent fetching of data across multiple date ranges.

- **Dataset Update:** Once the data is processed, it updates the Hugging Face dataset using the `update_huggingface_dataset()` function, specifying the dataset name (`stackoverflow_q_and_a_sample`), user credentials, and dataset split (in this case, "train").

### How It Works:

1. **Login to Hugging Face Hub:** The script logs in to the Hugging Face Hub with the provided token.
  
2. **Data Fetching:** It fetches question-answer pairs using `get_question_answer_pairs()` for each date range in `date_ranges`.

3. **Data Aggregation:** The data is concatenated into a single DataFrame for easy processing.

4. **Updating Dataset:** The final DataFrame is uploaded to Hugging Face, updating the specified dataset (`stackoverflow_q_and_a_sample`).

### Requirements:
- Recommend to use [`conda`](https://docs.anaconda.com/miniconda/install/) environment but it's up to you.
- New HuggingFace Dataset
    - If you don't know to create a new dataset on huggingface ui please read this: [`upload_dataset`](https://huggingface.co/docs/datasets/en/upload_dataset)
- Python version should be above 3.10
- Python packages
    - `huggingface_hub`
    - `datasets`
    - `pandas`
    - `concurrent.futures`
    - `beautifulsoup4` (needed to clean the extracted body of the question and answer text)

    To install the above packages please run the following command:
    ```
    pip install -r requirements.txt
    ```

### Example:
```bash
python main.py
```
Adjust the `from_date` and `to_date` as you need and
Make sure to replace the `<>` in the 
- `login(token="<>")` : with your actual Hugging Face token.
- `update_huggingface_dataset(new_data_df=df, username="<>", dataset_name="<>", split="<>")` : with your huggingface username, dataset name and split(`train`, `test` or `dev`)
