import requests
import json

url = "http://127.0.0.1:5000/api/generate_quiz"
payload = {
    "skill_level": "Beginner",
    "choice": 1,
    "topic": "Python Basics",
    "num_questions": 5
}

response = requests.post(url, json=payload)

print("Status Code:", response.status_code)

try:
    data = response.json()
    print("\nResponse JSON:")
    quiz = data.get("quiz")

    # If structured quiz is available
    if isinstance(quiz, dict) and "quiz" in quiz:
        questions = quiz["quiz"]
        for i, q in enumerate(questions, 1):
            print(f"\nQ{i}: {q['question']}")
            if q["type"] == "mcq":
                for idx, opt in enumerate(q["options"], start=1):
                    print(f"   {idx}. {opt}")
                print(f"   ✅ Answer: {q['answer']}")
            elif q["type"] == "fill_blank":
                print("   (Fill in the blank)")
                print(f"   ✅ Answer: {q['answer']}")
            elif q["type"] == "descriptive":
                print("   (Descriptive question)")
    else:
        # fallback if not structured
        print(json.dumps(data, indent=2))

except Exception as e:
    print("Error parsing response:", str(e))
    print("Raw text:", response.text)
