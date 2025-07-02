import json
import time
from textwrap import dedent
from typing import Any, Dict, List, Tuple

import pandas as pd
import torch
from tqdm import tqdm
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    LogitsProcessor,
    LogitsProcessorList,
)

# Define a system prompt for an in-car virtual assistant.
# This prompt guides the behavior of the assistant by specifying how it should respond to user inputs.
SYSTEM_PROMPT = dedent(
    """
    You are an in car virtual assistant that maps user's inputs to the corresponding function call in the vehicle. You must respond with only a JSON object matching the following schema:

    {
        "function_name": <name of the function>,
        "parameters": {
            <arg1_name>: <arg1_value>,
            <arg2_name>: <arg2_value>,
            ...
        }
    }

    Important: DO NOT include any other information in the response.
    """
)


class FirstTokenLogitsProcessor(LogitsProcessor):
    def __init__(self):
        self.first_token_time = (
            None  # Store the timestamp when first token is generated
        )

    def __call__(self, input_ids: torch.Tensor, scores: torch.Tensor) -> torch.Tensor:
        if self.first_token_time is None:
            self.first_token_time = (
                time.time()
            )  # Capture time of first token generation
        return scores  # Return unchanged scores to allow generation to continue


# Post-processing function: formats the model output
def postprocess_output(raw_output: str) -> Dict[str, Any]:
    """
    Converts model output into a structured dictionary format:
    {"function_name": <function_name>, "parameters": {"param1": "value1", ...}}
    """
    try:
        parsed_output = json.loads(
            raw_output
        )  # Assuming the model returns JSON-like text
        if isinstance(parsed_output, dict) and "function_name" in parsed_output:
            return parsed_output  # Valid structured output
    except json.JSONDecodeError:
        pass

    # Default fallback if model response is not well-formed
    return {
        "function_name": "unknown_function",
        "parameters": {"raw_response": raw_output},
    }


# Function to calculate metrics
def calculate_metrics(
    prompt_tokens: int,
    completion_tokens: int,
    time_to_first_token: float,
    total_time: float,
) -> Dict[str, float]:
    """
    Calculates various performance metrics.
    """
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "time_to_first_token_seconds": round(
            time_to_first_token, 4
        ),  # Time to first token in seconds
        "total_time_seconds": round(total_time, 4),  # Total inference time in seconds
        "tokens_per_second": round(completion_tokens / total_time, 4)
        if total_time > 0
        else 0.0,
    }


def run_single_inference(
    query: str, model, tokenizer, system_prompt: str
) -> Tuple[Dict[str, Any], Dict[str, float]]:
    messages = [
        {"role": "system", "content": system_prompt},  # System instruction
        {"role": "user", "content": query},  # User input
    ]

    # Prepare input for the model
    input_ids = tokenizer.apply_chat_template(
        messages, truncation=True, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    prompt_tokens = input_ids.shape[1]

    # Initialize logits processor to capture first token time
    first_token_processor = FirstTokenLogitsProcessor()

    # Start timing for total time capture of request
    start_time = time.time()

    completion_tokens = []

    for token in model.generate(
        input_ids=input_ids,
        max_new_tokens=256,
        do_sample=False,
        top_k=50,
        logits_processor=LogitsProcessorList([first_token_processor]),
    ):
        completion_tokens.append(token)

    # End timing
    # Capture first token time
    time_to_first_token = (
        first_token_processor.first_token_time - start_time
        if first_token_processor.first_token_time
        else None
    )
    # Capture total time taken
    total_time = time.time() - start_time  # Total inference time

    # calculate completion tokens
    num_completion_tokens = len(completion_tokens[0])

    raw_output = tokenizer.decode(
        completion_tokens[0][input_ids.shape[1] :],
        skip_special_tokens=True,
    )

    formatted_output = postprocess_output(raw_output)
    metrics = calculate_metrics(
        prompt_tokens, num_completion_tokens, time_to_first_token, total_time
    )

    return formatted_output, metrics


# Run inference on a list of queries
def run_inference(
    queries: List[str], model, tokenizer, system_prompt: str
) -> List[Tuple[Dict[str, Any], Dict[str, float]]]:
    """
    Runs inference on multiple queries.

    Returns:
        List of tuples: [(formatted_answer, metrics), ...]
    """
    results = []

    for query in tqdm(queries):
        formatted_output, metrics = run_single_inference(
            query, model, tokenizer, system_prompt
        )

        results.append((formatted_output, metrics))

    return results


model = AutoModelForCausalLM.from_pretrained(
    "quyvu/finetuned_fn_calling_ai_learning_day"
)
tokenizer = AutoTokenizer.from_pretrained("quyvu/finetuned_fn_calling_ai_learning_day")

test_data = pd.read_csv("Data/test_data.csv")

user_queries = test_data["prompt"].tolist()

outputs = run_inference(user_queries, model, tokenizer, SYSTEM_PROMPT)

inference_metrics = pd.DataFrame([x[1] for x in outputs])
inference_metrics.head(3)

inference_metrics.to_csv("evaluation/inference_metrics.csv", index=False)

pred_data = test_data.assign(prediction=[x[0] for x in outputs])
pred_data.head(5)

pred_data_with_metrics = pd.concat([pred_data, inference_metrics], axis=1)
pred_data_with_metrics.head(5)

pred_data_with_metrics.to_csv("./evaluation/prediction_with_metrics.csv", index=False)

with open("./evaluation/predictions.jsonl", "w") as f:
    for entry in outputs:
        f.write(json.dumps(entry[0]) + "\n")
