from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_interview_questions(user_resume: str, job_description: str, question_type: str = "Technical", num_questions: int = 3) -> dict:
    try:
        # Construct the prompt
        interview_prompt = f"""
        You are an expert in interview preparation. Given the job description and the user's resume, generate {num_questions} {question_type} interview questions that could be asked for this position. 

        **Requirements:**
        - Each question must include a detailed model answer that demonstrates how to effectively answer it.
        - Ensure that the response includes only the specified question type: "{question_type}".
        - Format the response strictly in JSON format as follows:

        {{
          "interviewQuestions": [
            {{
              "type": "{question_type}",
              "question": "Example question here",
              "answer": "Example answer here"
            }}
          ]
        }}

        **Resume**:
        {user_resume}

        **Job Description**:
        {job_description}

        Only return valid JSON. Do not include extra text, explanations, or commentary.
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert interview question generator. Return your response in strict JSON format."},
                {"role": "user", "content": interview_prompt}
            ],
            max_tokens=1250,
            temperature=0.5,
            response_format={"type": "json_object"}  # Structured JSON output
        )

        # Extract and parse the response content
        response_content = completion.choices[0].message.content.strip()

        parsed_response = json.loads(response_content)

        return parsed_response.get("interviewQuestions", [])

    except json.JSONDecodeError as json_error:
        print(f"JSON Parsing Error: {json_error}")
        return {"error": "Failed to parse OpenAI JSON response."}

    except Exception as e:
        print(f"Error generating interview questions: {e}")
        return {"error": str(e)}