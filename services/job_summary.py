from openai import OpenAI
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def summarize_job_description(job_description: str) -> dict:
    """
    Summarize the key points from a job description into one concise string.
    """
    try:
        # Construct the improved prompt
        summary_prompt = f"""
        You are an expert job description summarizer. Given the following job description, extract **all key details** and summarize them into **one clear and concise paragraph**.
        
        Your summary **must** include:
        - Position title  
        - Company name  
        - Job location (or 'Remote' if applicable)  
        - Required skills and technologies  
        - Preferred skills (if mentioned)  
        - Key responsibilities (in brief)  
        - Years of experience required  
        - Salary details (if mentioned)  
        - Any unique attributes about the company or role  

        Ensure the summary is **clear, grammatically correct, and easy to understand**, formatted as **one paragraph**, and **strictly in JSON** as shown below:

        {{
          "jobSummary": "Summarized job description goes here"
        }}

        **Job Description:**
        {job_description}
        """

        # Call OpenAI API with structured JSON output
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert job description summarizer. Return your response in strict JSON format."},
                {"role": "user", "content": summary_prompt}
            ],
            max_tokens=500,
            temperature=0.5,
            response_format={"type": "json_object"}
        )

        # Parse the response
        response_content = completion.choices[0].message.content.strip()
        parsed_response = json.loads(response_content)
        
        return parsed_response

    except json.JSONDecodeError as json_error:
        print(f"JSON Parsing Error: {json_error}")
        return {"error": "Failed to parse OpenAI JSON response."}

    except Exception as e:
        print(f"Error summarizing job description: {e}")
        return {"error": str(e)}
