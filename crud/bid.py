from typing import Optional, List
from models import Bid


class BidCRUD:

    @staticmethod
    async def create_bid(data: dict) -> Bid:
        """
        Создаёт заявку, автоматически преобразуя данные для ForeignKey и IntFields
        """
        if 'country' in data:
            data['country_id'] = data.pop('country')

        if 'city' in data:
            city_value = data.pop('city')
            if isinstance(city_value, list):
                data['city_id'] = city_value[0] if city_value else None
            else:
                data['city_id'] = city_value

        if 'category' in data:
            value = data.pop('category')
            if isinstance(value, str):
                value = [int(x) for x in value.split(",") if x]
            data['categories'] = value  # JSONField

        if 'under_category' in data:
            value = data.pop('under_category')
            if isinstance(value, str):
                value = [int(x) for x in value.split(",") if x]
            data['under_categories'] = value  # JSONField

        bid = await Bid.create(**data)
        return bid

    @staticmethod
    async def get_bid_by_id(bid_id: int) -> Optional[Bid]:
        return await Bid.get_or_none(id=bid_id)

    @staticmethod
    async def delete_bid(bid: Bid) -> None:
        await bid.delete()

    @staticmethod
    async def update_bid(bid: Bid, data: dict) -> Bid:
        for key, value in data.items():
            setattr(bid, key, value)
        await bid.save()
        return bid
