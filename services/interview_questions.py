from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_interview_questions(user_resume: str, job_description: str, question_type: str = "Technical", num_questions: int = 3) -> list:
    try:
        interview_prompt = f"""
        You are an expert in interview preparation. Given the job description and the user's resume, generate {num_questions} {question_type} interview questions that could be asked for this position. Include both the question and a detailed model answer that demonstrates how to effectively answer each question.

        Ensure that the response only includes questions of the following types:
        - Technical: Questions that assess the candidate's technical skills and problem-solving abilities related to the job description.
        - Behavioral: Questions that evaluate the candidate's past behavior and experiences to predict future performance in a work environment.

        Format all outputs strictly in the following JSON format:

        {{
          "interviewQuestions": [
            {{"type": "{question_type}", "question": "Example question here", "answer": "Example answer here"}}
          ]
        }}

        **Resume**:
        {user_resume}

        **Job Description**:
        {job_description}

        **JSON Response (plain text only)**:
        """

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert interview question generator."},
                {"role": "user", "content": interview_prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )

        response_content = completion.choices[0].message.content.strip()
        print("Raw OpenAI Response:", response_content)  # Debug line

        # Remove markdown code block formatting
        clean_response = re.sub(r'^```json\s*|\s*```$', '', response_content).strip()

        # Parse the cleaned JSON response
        parsed_response = json.loads(clean_response)
        return parsed_response.get("interviewQuestions", [])
    
    except json.JSONDecodeError as json_error:
        print(f"Error parsing JSON: {json_error}")
        print("Response content that caused the error:", response_content)
        return {"error": "Failed to parse JSON from OpenAI response."}
    except Exception as e:
        print(f"Error generating interview questions: {e}")
        return {"error": str(e)}
