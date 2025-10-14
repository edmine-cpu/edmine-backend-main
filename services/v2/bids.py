from models import Bid


async def get_bids(
    language: str,
    city: int | None = None,
    country: int | None = None,
    category: int | None = None,
    under_category: int | None = None,
    search: str = "",
    budget_from: int | None = None,
    budget_to: int | None = None,
):
    result = await Bid.filter()
