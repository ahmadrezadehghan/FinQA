from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
from peft import get_peft_config, get_peft_model, LoraConfig, TaskType

# 1) Load data as for SFT: each record needs 'prompt' and 'completion'
# (you can reuse the JSONL you made above)
ds = load_dataset("json", data_files="train_gpt_qa.jsonl", split="train")

tokenizer = AutoTokenizer.from_pretrained("gpt2", padding_side="left")
model     = AutoModelForCausalLM.from_pretrained("gpt2", device_map="auto")

# 2) Prepare PEFT config
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    r=8, lora_alpha=32, lora_dropout=0.05
)
model = get_peft_model(model, peft_config)

# 3) Tokenize
def preprocess(record):
    tokens = tokenizer(
        record["prompt"] + record["completion"],
        truncation=True,
        max_length=512
    )
    tokens["labels"] = tokens["input_ids"].copy()
    return tokens

train_ds = ds.map(preprocess, remove_columns=ds.column_names)

# 4) Train
args = TrainingArguments(
    output_dir="gpt3-lora-qa",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    logging_steps=10,
    save_total_limit=2,
)
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_ds,
    tokenizer=tokenizer
)
trainer.train()
model.push_to_hub("my-org/gpt2-lora-telegram-qa")
