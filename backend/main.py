from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import os
import uvicorn

from auth import (
    create_access_token, 
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_evaluator_or_admin,
    verify_password,
    MOCK_USERS
)
from models import UserInDB, EvaluationResult, Token
from audit import log_audit_event
from nlp_processor import evaluate_tender

app = FastAPI(title="TenderGuard AI", description="Zero-Trust Automated Tender Evaluation System")

def authenticate_user(db, username: str, password: str):
    user = db.get(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(MOCK_USERS, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/upload", response_model=EvaluationResult)
async def upload_tender_pdf(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_evaluator_or_admin)
):
    if not file.filename.endswith(".pdf"):
        log_audit_event(current_user.username, "UPLOAD", file.filename, "REJECTED", {"reason": "Not a PDF"})
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Read file
    pdf_bytes = await file.read()
    
    log_audit_event(current_user.username, "UPLOAD", file.filename, "ACCEPTED", {"size": len(pdf_bytes)})

    try:
        # Run NLP evaluation
        results = evaluate_tender(pdf_bytes)
        
        # Log successful processing
        log_audit_event(current_user.username, "EVALUATE", file.filename, "SUCCESS", results)
        
        return EvaluationResult(
            filename=file.filename,
            turnover=results.get("turnover"),
            iso_certification=results.get("iso_certification"),
            past_experience=results.get("past_experience"),
            sentiment_score=results.get("sentiment_score"),
            sentiment_label=results.get("sentiment_label"),
            status="Processed Successfully"
        )
    except Exception as e:
        error_msg = str(e)
        log_audit_event(current_user.username, "EVALUATE", file.filename, "FAILED", {"error": error_msg})
        raise HTTPException(status_code=500, detail=f"Error processing tender: {error_msg}")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import pathlib
    cert_file = pathlib.Path(__file__).parent.parent / "cert.pem"
    key_file = pathlib.Path(__file__).parent.parent / "key.pem"
    if cert_file.exists() and key_file.exists():
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True,
                     ssl_certfile=str(cert_file), ssl_keyfile=str(key_file))
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
