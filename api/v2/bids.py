from fastapi import APIRouter, HTTPException
from schemas.v2.bids import Bid, PaginationParams
from models import Bid as BidModel

SUPPORTED_LANGUAGES = ["en", "uk", "pl", "de", "fr"]
router = APIRouter()


@router.get("/bids/")
async def get_bids(response: Bid, pagination: PaginationParams):
			if response.language not in SUPPORTED_LANGUAGES:
				raise HTTPException(status_code=400, detail="Unsupported language")
			
			await BidModel.filter()


