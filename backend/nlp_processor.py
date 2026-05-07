import os
import io
import re
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract
from transformers import pipeline

MODEL_NAME = os.getenv("MODEL_NAME", "distilbert-base-uncased-finetuned-sst-2-english")

# Initialize the pipeline offline (model should be pre-downloaded in Dockerfile)
print(f"Loading transformer model {MODEL_NAME}...")
try:
    nlp_model = pipeline("text-classification", model=MODEL_NAME)
except Exception as e:
    print(f"Error loading model: {e}")
    nlp_model = None

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """
    Extracts text from a PDF using offline OCR (pdf2image + PyTesseract).
    """
    try:
        # Convert PDF bytes to a list of PIL Images
        images = convert_from_bytes(pdf_bytes)
        
        extracted_text = ""
        for i, img in enumerate(images):
            # Apply PyTesseract
            text = pytesseract.image_to_string(img)
            extracted_text += f"\n--- Page {i+1} ---\n{text}"
            
        return extracted_text
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        raise

def extract_entities(text: str) -> dict:
    """
    Uses Regex to pull out basic entities like Turnover, ISO certification, and past experience.
    (This is a scaffolding, for a real deployment we'd swap this with a fine-tuned DeBERTa model)
    """
    entities = {
        "turnover": None,
        "iso_certification": False,
        "past_experience": None
    }
    
    # 1. Turnover Extraction
    turnover_match = re.search(r'(turnover|revenue)[\s\w]*?((?:rs\.?|inr|\$|€|£)?\s*[\d,]+(?:\.\d+)?\s*(?:cr|crore|lakh|million|billion|k)?)', text, re.IGNORECASE)
    if turnover_match:
        entities["turnover"] = turnover_match.group(2).strip()
        
    # 2. ISO Certification Check
    if re.search(r'iso\s*9001', text, re.IGNORECASE):
        entities["iso_certification"] = True
        
    # 3. Past Experience (very rudimentary search for years)
    exp_match = re.search(r'(\d+)\+?\s*years?(?:\s*of)?\s*experience', text, re.IGNORECASE)
    if exp_match:
        entities["past_experience"] = f"{exp_match.group(1)} Years"
        
    return entities

def evaluate_tender(pdf_bytes: bytes) -> dict:
    """
    Main evaluation pipeline: OCR -> Entity Extraction -> Sentiment/Risk classification
    """
    text = extract_text_from_pdf(pdf_bytes)
    
    # Extract entities
    entities = extract_entities(text)
    
    # Run through Transformer Model
    sentiment_score = None
    sentiment_label = None
    if nlp_model:
        # Truncate text if it's too long for the model (typically 512 tokens)
        short_text = text[:1500] 
        if short_text.strip():
            result = nlp_model(short_text)[0]
            sentiment_label = result['label']
            sentiment_score = result['score']
            
    return {
        "extracted_text_preview": text[:200] + "...",
        "turnover": entities["turnover"],
        "iso_certification": entities["iso_certification"],
        "past_experience": entities["past_experience"],
        "sentiment_label": sentiment_label,
        "sentiment_score": sentiment_score
    }
