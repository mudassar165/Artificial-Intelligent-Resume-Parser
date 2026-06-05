from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import os
from datetime import datetime
from pydantic import BaseModel
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import auth, credentials, firestore, storage
import ai_engine

load_dotenv()

app = FastAPI(title="ResumeMind AI API")

firebase_service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
storage_bucket_name = os.getenv("FIREBASE_STORAGE_BUCKET", "resumeparser-f2154.appspot.com")
db = None
bucket = None
if firebase_service_account:
    if os.path.exists(firebase_service_account):
        cred = credentials.Certificate(firebase_service_account)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred, {"storageBucket": storage_bucket_name})
        db = firestore.client()
        bucket = storage.bucket()
    else:
        print(f"Warning: Firebase service account not found at {firebase_service_account}")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to ResumeMind AI API"}

@app.post("/api/upload")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Ensure upload directory exists
    import os
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    try:
        content = await file.read()
        # Save file to disk
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Extract text from PDF using PyMuPDF
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        
        # Add AI parsing logic
        extracted_info = ai_engine.extract_information(text)
        extracted_info["full_text"] = text  # Include full text for re-matching

        # Calculate default match score (for applicant dashboard)
        default_jd = "Software Engineer with skills in Python, JavaScript, React, Machine Learning, and web development."
        match_result = ai_engine.calculate_match_score(text, default_jd)

        # Save upload metadata to Firebase Firestore if configured
        if db is not None:
            try:
                db.collection("resumes").add({
                    "filename": file.filename,
                    "uploaded_at": datetime.utcnow(),
                    "extracted_data": extracted_info,
                    "match_score": match_result["score"],
                    "source": "backend-api",
                })
            except Exception as firebase_error:
                print(f"Firebase write failed: {firebase_error}")

        return {
            "filename": file.filename,
            "extracted_data": extracted_info,
            "match_score": match_result["score"],
            "score_breakdown": match_result["score_breakdown"],
            "matched_keywords": match_result["matched_keywords"],
            "missing_skills": match_result["missing_skills"],
            "improvement_suggestions": match_result["improvement_suggestions"],
            "ai_recommendation": match_result["ai_recommendation"],
            "recommended_roles": match_result["recommended_roles"],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class MatchRequest(BaseModel):
    resume_text: str
    job_description: str

@app.post("/api/match")
async def match_resume(req: MatchRequest):
    try:
        match_result = ai_engine.calculate_match_score(req.resume_text, req.job_description)
        return {
            "match_score": match_result["score"],
            "score_breakdown": match_result["score_breakdown"],
            "matched_keywords": match_result["matched_keywords"],
            "missing_skills": match_result["missing_skills"],
            "improvement_suggestions": match_result["improvement_suggestions"],
            "ai_recommendation": match_result["ai_recommendation"],
            "recommended_roles": match_result["recommended_roles"],
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/storage/upload")
async def firebase_storage_upload(file: UploadFile = File(...), folder: str = "uploads"):
    if bucket is None:
        raise HTTPException(status_code=500, detail="Firebase Storage is not configured.")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        content = await file.read()
        blob_name = f"{folder}/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(content, content_type=file.content_type)
        blob.make_public()
        return {
            "status": "success",
            "storage_path": blob_name,
            "public_url": blob.public_url,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    upload_dir = os.path.join(os.path.dirname(__file__), "uploads")
    file_path = os.path.join(upload_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="application/pdf", filename=filename)
