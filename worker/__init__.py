import os
import random
import string

import torch
from flask import Flask, jsonify
from transformers import DistilBertForSequenceClassification, DistilBertTokenizer

INSTANCE_ID = os.environ.get("INSTANCE_ID", "unknown")

app = Flask(__name__)


# Load the pre-trained model and tokenizer
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=2
)


def generate_random_text(lenth=50):
    letters = string.ascii_lowercase + " "
    return "".join(random.choice(letters) for i in range(lenth))


@app.route("/")
def hello_world():
    return f"Worker ID {INSTANCE_ID}"


@app.route("/health")
def health():
    return "OK"


@app.route("/run_model", methods=["POST"])
def run_model():
    # Generate random input text
    text = generate_random_text()

    # Tokenize the input text and run it through the model
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    outputs = model(**inputs)  # type: ignore

    # The model returns logits, we need to convert them to probabilities
    probabilities = torch.softmax(outputs.logits, dim=-1)

    # Convert the tensor to a list and return it
    probabilities_list = probabilities.tolist()[0]

    return jsonify({"input_text": text, "probabilities": probabilities_list})
