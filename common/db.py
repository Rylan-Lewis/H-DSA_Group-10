import os
import psycopg2
import psycopg2.extras
import json
from dotenv import load_dotenv


load_dotenv()

def create_db_connection():
    DATABASE = os.getenv('DB')
    USER = os.getenv('DB_USER')
    PASSWORD = os.getenv('DB_PASSWORD')
    HOST = os.getenv('DB_HOST')
    PORT = os.getenv('DB_PORT')

    conn = psycopg2.connect(
        dbname=DATABASE,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        # sslmode='verify-full',
        # sslrootcert='./global-bundle.pem'
    )
    return conn

def fetch_job(jobid):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM public.jobs WHERE jobid = {jobid}')
    job = cursor.fetchone()[2]
    cursor.close()
    conn.close()
    return job


#? Candidate Functions
def fetch_candidate(talentid):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM public.skillgraphs WHERE talentid = {talentid}')
    candidate = cursor.fetchone()[1]
    cursor.close()
    conn.close()
    return candidate

#! Deprecated
def get_resumeUrl_from_talent(talentid):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'SELECT * FROM public.talents WHERE talentid = {talentid}')
    candidate = cursor.fetchone()[2]
    cursor.close()
    conn.close()
    return candidate

#! Fix for resumeUrl
def get_resumeUrl_from_skillgraph(talentid):
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT talentid, skillgraph -> 'talent' ->> 'resumeUrl' AS resumeUrl FROM public.skillgraphs WHERE talentid = {talentid}")
    candidate = cursor.fetchone()[1]
    cursor.close()
    conn.close()
    return candidate


#? Procedure Functions
def get_pending_applications():
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM get_pending_applications();
    ''')
    pendingApplications = cursor.fetchall()
    cursor.close()
    conn.close()
    return pendingApplications

def update_insights(talentid, jobid, insights, email_template):
    conn = create_db_connection()
    cursor = conn.cursor()
    
    insights_json = psycopg2.extras.Json(insights)
    cursor.callproc('update_insights', (int(talentid), int(jobid), insights_json, email_template))
    conn.commit()
    
    cursor.close()
    conn.close()
    return True

def update_resume_text(talentid, resume_text):
    conn = create_db_connection()
    cursor = conn.cursor()

    cursor.callproc('update_resume_text', (int(talentid), str(resume_text)))
    conn.commit()
    
    cursor.close()
    conn.close()
    return True

