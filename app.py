import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer, util
import json
import torch
from thefuzz import process

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app, resources={r"/*": {"origins": "*"}})

# Load dataset from JSON file
def load_dataset():
    with open("datasets/dous-datasets.json", "r", encoding="utf-8") as f:
        return json.load(f)

dataset = load_dataset()

# Load sentence transformer model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/chat")
def chat():
    return render_template("askdous.html")

def find_best_answer(user_question):
    separators = [" and ", ",", "."]
    for sep in separators:
        user_question = user_question.replace(sep, "|")
    
    questions = [q.strip() for q in user_question.split("|") if q.strip()]
    responses = []
    
    stored_questions = [item["question"].lower() for item in dataset]
    stored_answers = [item["answer"] for item in dataset]
    
    stored_embeddings = model.encode(stored_questions, convert_to_tensor=True)
    
    for question in questions:
        question = question.lower().strip()

        # If the exact question exists in dataset, return it directly
        if question in stored_questions:
            answer = stored_answers[stored_questions.index(question)]
        elif len(question) <= 4:  # If input is too short, return a fallback
            answer = "I'm Sorry but What are you referring to?"
        else:
            user_embedding = model.encode(question, convert_to_tensor=True)
            similarities = util.pytorch_cos_sim(user_embedding, stored_embeddings)[0]
            
            best_match_index = torch.argmax(similarities).item()
            best_match_score = similarities[best_match_index].item()
            
            if best_match_score >= 0.4:
                answer = stored_answers[best_match_index]
            else:
                best_match, best_score = process.extractOne(question, stored_questions)
                if best_score >= 70:
                    answer = stored_answers[stored_questions.index(best_match)]
                else:
                    answer = "I'm Sorry but What are you referring to?"
        
        responses.append(answer)
    
    final_response = "\n\n".join(responses) + "\n\nFeel free to ask more questions!"
    return final_response


@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_question = data.get("question", "").lower()
    best_answer = find_best_answer(user_question)
    return jsonify({"answer": best_answer})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use PORT from Render, default to 5000
    app.run(host="0.0.0.0", port=port)
