from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
import time
import boto3
from botocore.exceptions import NoCredentialsError
from PyPDF2 import PdfReader
from docx import Document
import google.generativeai as genai
from dotenv import load_dotenv
import base64


load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')


#? Comman Functions
def run_prompt(prompt):
    #! Temp Fix for Rate Limit
    while True:
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Rate Limit Hit: {e}")
            time.sleep(10)

def pretty_print(data):
    print(json.dumps(data, indent=4))

def preprocess(data):
    data = data.replace("json", "").replace("```", "").strip()
    data = data.replace('Suited', "suited")
    return data

def my_jsonify(data):
    data = json.loads(data)
    return data

def postprocess(data):
    data["matching"]["pursuits"] = ""
    data["matching"]["compensation"] = ""
    return data

def prompt_to_json(prompt):
    prompt = preprocess(prompt)
    prompt = my_jsonify(prompt)
    prompt = postprocess(prompt)
    return prompt

def extract_text(file_path):
    extracted_text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                extracted_text += page.extract_text()
    except:
        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            extracted_text += paragraph.text
    return extracted_text.replace("\n", "")


#? Resume Functions
def get_resume_data(resumeUrl):
    os.makedirs("./resumes", exist_ok=True)
    resume_path = download_from_s3(resumeUrl)
    resume_text = extract_text(resume_path)
    if resume_path:
        os.remove(resume_path)
    return resume_text

def download_from_s3(resumeUrl, download_path=f'./resumes/candidate_resume.pdf'):
    bucket_name = os.getenv("resume_bucket")
    try:
        s3 = boto3.client('s3',
                        aws_access_key_id=os.getenv("resume_aws_access_key_id"),
                        aws_secret_access_key=os.getenv("resume_aws_secret_access_key"),
                        region_name='ap-south-1')
        
        s3.download_file(bucket_name, resumeUrl, download_path)
        return download_path
    except NoCredentialsError as e:
        error_message = f"AWS credentials not available: {str(e)}"
        print(error_message)
        raise NoCredentialsError(error_message)
    except Exception as e:
        error_message = f"An error occurred while downloading from S3: {str(e)}"
        print(error_message)
        raise Exception(error_message)


#? Skillgraph Functions
def sanitize_candidate_data(candidate):
    return {key: value for key, value in candidate.items() if key != 'talent'}

def encode64(original_string):
    bytes_string = original_string.encode('utf-8')
    base64_bytes = base64.b64encode(bytes_string)
    base64_string = base64_bytes.decode('utf-8')
    return base64_string
