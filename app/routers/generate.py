from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.db import mongo
from app.llm import openrouter_llm as llm
from app.models import GenerateSectionRequest, GenerateSectionResponse

router = APIRouter()


@router.post("/generate-section", response_model=GenerateSectionResponse)
def generate_section_endpoint(payload: GenerateSectionRequest):
    try:
        result = llm.generate_section(
            input_text=payload.text,
            section_type=payload.section_type,
            company_id=payload.company_id,
        )
        entry = {
            "request_id": str(uuid4()),
            "company_id": payload.company_id,
            "section_type": payload.section_type,
            "generated_text": result["generated_text"],
            "created_at": datetime.now(timezone.utc),
            "sources": result["sources"],
        }
        mongo.history.insert_one(entry)
        return GenerateSectionResponse(
            request_id=entry["request_id"],
            company_id=payload.company_id,
            section_type=payload.section_type,
            generated_text=result["generated_text"],
            sources=result["sources"],
            created_at=entry["created_at"],
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
