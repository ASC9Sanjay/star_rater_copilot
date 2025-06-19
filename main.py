# from fastapi import FastAPI, File, UploadFile, HTTPException
# from typing import Dict, Optional
# import pdfplumber
# import docx
# import uvicorn
# import os
# import re

# app = FastAPI(
#     title="EOC Star Rating Calculator",
#     description="Analyzes US healthcare plan EOC documents and returns a CMS-style star rating.",
#     version="1.0"
# )

# # Define domain keywords and score mappings
# DOMAIN_KEYWORDS = {
#     "preventive_care": {
#         "high": ["annual wellness visit", "cancer screening", "immunization", "comprehensive preventive care"],
#         "medium": ["some preventive services", "screening available"],
#         "low": ["requires prior authorization", "limited coverage"]
#     },
#     "member_services": {
#         "high": ["24/7 availability", "available 24 hours", "24x7 support"],
#         "medium": ["customer service team", "support available during business hours"],
#         "low": ["business hours only", "limited support"]
#     },
#     "appeals": {
#         "high": ["processed on time", "within required timeframe", "95% resolved timely"],
#         "medium": ["most appeals resolved timely", "reasonable processing time"],
#         "low": ["delays reported", "slow processing", "incomplete resolution"]
#     },
#     "chronic_care": {
#         "high": ["regular follow-ups", "telehealth support", "comprehensive management"],
#         "medium": ["basic chronic disease management", "care through primary physician"],
#         "low": ["limited chronic care", "no structured programs"]
#     }
# }

# def extract_text_from_pdf(file_path: str) -> str:
#     with pdfplumber.open(file_path) as pdf:
#         text = ""
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#         return text

# def extract_text_from_docx(file_path: str) -> str:
#     doc = docx.Document(file_path)
#     full_text = [para.text for para in doc.paragraphs]
#     return '\n'.join(full_text)

# def clean_text(text: str) -> str:
#     # Normalize spacing and case
#     return re.sub(r'\s+', ' ', text).strip().lower()

# def calculate_star_rating(text: str) -> Dict[str, float]:
#     text_lower = clean_text(text)

#     scores = {
#         "preventive_care": 2,
#         "member_services": 2,
#         "appeals": 2,
#         "chronic_care": 2
#     }

#     def score_domain(domain: str) -> int:
#         high_keywords = DOMAIN_KEYWORDS[domain]["high"]
#         medium_keywords = DOMAIN_KEYWORDS[domain]["medium"]
#         low_keywords = DOMAIN_KEYWORDS[domain]["low"]

#         for word in high_keywords:
#             if word in text_lower:
#                 return 5
#         for word in medium_keywords:
#             if word in text_lower:
#                 return 4
#         for word in low_keywords:
#             if word in text_lower:
#                 return 2
#         return 3  # Default score if none matched strongly

#     # Score each domain
#     scores["preventive_care"] = score_domain("preventive_care")
#     scores["member_services"] = score_domain("member_services")
#     scores["appeals"] = score_domain("appeals")
#     scores["chronic_care"] = score_domain("chronic_care")

#     # Calculate overall score
#     total_score = sum(scores.values())
#     average_score = round(total_score / len(scores), 1)
#     star_rating = round(average_score)

#     return {
#         "preventive_care": scores["preventive_care"],
#         "member_services": scores["member_services"],
#         "appeals": scores["appeals"],
#         "chronic_care": scores["chronic_care"],
#         "overall_score": average_score,
#         "star_rating": star_rating
#     }

# @app.post("/calculate-star-rating")
# async def calculate_star_rating_api(file: UploadFile = File(...)) -> Dict[str, float]:
#     file_extension = file.filename.split(".")[-1].lower()
#     if file_extension not in ["pdf", "docx"]:
#         raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or DOCX.")

#     try:
#         temp_file_path = f"temp_upload.{file_extension}"
#         with open(temp_file_path, "wb") as buffer:
#             buffer.write(await file.read())

#         if file_extension == "pdf":
#             content = extract_text_from_pdf(temp_file_path)
#         else:
#             content = extract_text_from_docx(temp_file_path)

#         result = calculate_star_rating(content)

#         # Clean up temporary file
#         os.remove(temp_file_path)

#         return result

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

# if __name__ == "__main__":
#     # Run the server on port 8080 instead of default 8000
#     uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)




from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Dict, Optional
import pdfplumber
import docx
import uvicorn
import os
import re
import base64
import tempfile

app = FastAPI(
    title="EOC Star Rating Calculator",
    description="Analyzes US healthcare plan EOC documents and returns a CMS-style star rating.",
    version="1.0"
)

# Define domain keywords and score mappings
DOMAIN_KEYWORDS = {
    "preventive_care": {
        "high": ["annual wellness visit", "cancer screening", "immunization", "comprehensive preventive care"],
        "medium": ["some preventive services", "screening available"],
        "low": ["requires prior authorization", "limited coverage"]
    },
    "member_services": {
        "high": ["24/7 availability", "available 24 hours", "24x7 support"],
        "medium": ["customer service team", "support available during business hours"],
        "low": ["business hours only", "limited support"]
    },
    "appeals": {
        "high": ["processed on time", "within required timeframe", "95% resolved timely"],
        "medium": ["most appeals resolved timely", "reasonable processing time"],
        "low": ["delays reported", "slow processing", "incomplete resolution"]
    },
    "chronic_care": {
        "high": ["regular follow-ups", "telehealth support", "comprehensive management"],
        "medium": ["basic chronic disease management", "care through primary physician"],
        "low": ["limited chronic care", "no structured programs"]
    }
}

def extract_text_from_pdf(file_path: str) -> str:
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text

def extract_text_from_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    full_text = [para.text for para in doc.paragraphs]
    return '\n'.join(full_text)

def clean_text(text: str) -> str:
    # Normalize spacing and case
    return re.sub(r'\s+', ' ', text).strip().lower()

def calculate_star_rating(text: str) -> Dict[str, float]:
    text_lower = clean_text(text)

    scores = {
        "preventive_care": 2,
        "member_services": 2,
        "appeals": 2,
        "chronic_care": 2
    }

    def score_domain(domain: str) -> int:
        high_keywords = DOMAIN_KEYWORDS[domain]["high"]
        medium_keywords = DOMAIN_KEYWORDS[domain]["medium"]
        low_keywords = DOMAIN_KEYWORDS[domain]["low"]

        for word in high_keywords:
            if word in text_lower:
                return 5
        for word in medium_keywords:
            if word in text_lower:
                return 4
        for word in low_keywords:
            if word in text_lower:
                return 2
        return 3  # Default score if none matched strongly

    # Score each domain
    scores["preventive_care"] = score_domain("preventive_care")
    scores["member_services"] = score_domain("member_services")
    scores["appeals"] = score_domain("appeals")
    scores["chronic_care"] = score_domain("chronic_care")

    # Calculate overall score
    total_score = sum(scores.values())
    average_score = round(total_score / len(scores), 1)
    star_rating = round(average_score)

    return {
        "preventive_care": scores["preventive_care"],
        "member_services": scores["member_services"],
        "appeals": scores["appeals"],
        "chronic_care": scores["chronic_care"],
        "overall_score": average_score,
        "star_rating": star_rating
}

# Request model for base64 input
class Base64FileRequest(BaseModel):
    file_data: str
    file_name: str

@app.post("/calculate-star-rating-base64")
async def calculate_star_rating_base64(request: Base64FileRequest) -> Dict[str, float]:
    try:
        file_data = request.file_data
        file_name = request.file_name
        file_extension = file_name.split(".")[-1].lower()

        if file_extension not in ["pdf", "docx"]:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload PDF or DOCX.")

        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmpfile:
            tmpfile.write(base64.b64decode(file_data))
            temp_file_path = tmpfile.name

        # Extract content
        if file_extension == "pdf":
            content = extract_text_from_pdf(temp_file_path)
        else:
            content = extract_text_from_docx(temp_file_path)

        result = calculate_star_rating(content)

        # Clean up
        os.unlink(temp_file_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
