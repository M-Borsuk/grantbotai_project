from fastapi import APIRouter, HTTPException

from app.db import mongo
from app.models import HistoryItem, HistoryResponse

router = APIRouter()


@router.get("/history/{company_id}", response_model=HistoryResponse)
def history_endpoint(company_id: str, limit: int = 20):
    try:
        cursor = mongo.history.find({"company_id": company_id}).sort("created_at", -1).limit(limit)
        items = [
            HistoryItem(
                request_id=entry["request_id"],
                section_type=entry["section_type"],
                generated_text=entry["generated_text"],
                created_at=entry["created_at"],
                sources=entry["sources"],
            )
            for entry in cursor
        ]
        return HistoryResponse(company_id=company_id, items=items)
    except Exception as e:
        raise HTTPException(500, detail=str(e))
