"""Helper code to publish the finetuned model to huggingface"""

import os

from dotenv import load_dotenv
from huggingface_hub import HfApi, login
from transformers import AutoModelForCausalLM, AutoTokenizer

load_dotenv()

output_dir = "models/fine_tuned_adapter"  # where the model is saved
tokenizer = AutoTokenizer.from_pretrained(output_dir)
model = AutoModelForCausalLM.from_pretrained(output_dir).to("cpu")

login(token=os.environ["HF_TOKEN"])
api = HfApi()
api.create_repo(repo_id="finetuned_fn_calling_ai_learning_day")

model.push_to_hub("finetuned_fn_calling_ai_learning_day", use_temp_dir=True)
tokenizer.push_to_hub("finetuned_fn_calling_ai_learning_day", use_temp_dir=True)
