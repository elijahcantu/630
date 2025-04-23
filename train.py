import pandas as pd
from datasets import Dataset, ClassLabel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.utils.class_weight import compute_class_weight
from sklearn.utils import resample
from sklearn.metrics import precision_recall_fscore_support, accuracy_score
import numpy as np
import torch

assert torch.cuda.is_available() or torch.backends.mps.is_available() or torch.backends.cpu, \
    "PyTorch not detected. Please install it with `pip install torch`."


df = pd.read_csv("final_dataset_train.csv")

df = df.rename(columns={"title": "text", "news": "label"})

class_weights = compute_class_weight('balanced', classes=np.unique(df['label']), y=df['label'])
class_weights_dict = {0: class_weights[0], 1: class_weights[1]}

df_majority = df[df['label'] == 0]
df_minority = df[df['label'] == 1]

df_minority_upsampled = resample(df_minority, 
                                 replace=True,
                                 n_samples=len(df_majority),
                                 random_state=42)

df_balanced = pd.concat([df_majority, df_minority_upsampled])

balanced_dataset = Dataset.from_pandas(df_balanced)

label_class = ClassLabel(num_classes=2, names=["non-news", "news"])
balanced_dataset = balanced_dataset.cast_column("label", label_class)

model_name = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

def tokenize_function(example):
    return tokenizer(example["text"], padding="max_length", truncation=True)

tokenized_dataset = balanced_dataset.map(tokenize_function, batched=True)
tokenized_dataset = tokenized_dataset.train_test_split(test_size=0.2, stratify_by_column="label")

model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    num_train_epochs=5,
    weight_decay=0.01,
    load_best_model_at_end=True,
)

def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='binary')
    acc = accuracy_score(labels, preds)
    return {"accuracy": acc, "f1": f1, "precision": precision, "recall": recall}

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset["train"],
    eval_dataset=tokenized_dataset["test"],
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

trainer.train()
