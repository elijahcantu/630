from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast

app = Flask(__name__)
CORS(app)  

model_path = "./checkpoint-47"
tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
model = DistilBertForSequenceClassification.from_pretrained(model_path)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_text = data.get("text", "")

    print(f"[DEBUG] Received text: {input_text}")

    if not input_text:
        return jsonify({"error": "No text provided"}), 400

    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=-1).item()

    print(f"[DEBUG] Predicted class: {predicted_class}")

    return jsonify({
        "predicted_class": predicted_class,
        "input_text": input_text
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
