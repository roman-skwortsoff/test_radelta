from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pymongo import ASCENDING, DESCENDING

from app.exceptions import InvalidDateRangeError, TypeIdNotFoundError


class AnalyticsRepository:
    def __init__(self, db):
        self.collection = db.delivery_logs

    async def get_all(
        self,
        skip: int,
        limit: int,
        type_id: Optional[int],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        sort_field: str,
        sort_order: str,
    ):
        query = {}
        if type_id is not None:
            query["type_id"] = type_id
        if date_from or date_to:
            query["created_at"] = {}
            if date_from:
                query["created_at"]["$gte"] = date_from
            if date_to:
                query["created_at"]["$lte"] = date_to

        sort_direction = DESCENDING if sort_order == "desc" else ASCENDING
        cursor = self.collection.find(
            query, skip=skip, limit=limit, sort=[(sort_field, sort_direction)]
        )

        results = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return results

    async def get_totals_range(
        self, start_date: date, end_date: date, type_id: Optional[int]
    ):
        if start_date > end_date:
            raise InvalidDateRangeError

        match_stage: dict[str, Any] = {
            "day_key": {"$gte": str(start_date), "$lte": str(end_date)}
        }
        if type_id is not None:
            match_stage["type_id"] = type_id

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": "$type_id",
                    "total_delivery_cost": {
                        "$sum": {
                            "$multiply": [
                                {
                                    "$add": [
                                        {"$multiply": ["$weight_kg", 0.5]},
                                        {"$multiply": ["$value_usd", 0.01]},
                                    ]
                                },
                                "$usd_rub_rate",
                            ]
                        }
                    },
                    "count_packages": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        results = await self.collection.aggregate(pipeline).to_list(None)

        if type_id is not None and not results:
            raise TypeIdNotFoundError

        return results

    async def get_daily_totals(self, day: str) -> List[Dict[str, Any]]:
        """
        Получить суммы стоимости доставки и количество посылок за указанный day_key.
        :param day: строка в формате YYYY-MM-DD
        """
        pipeline = [
            {"$match": {"day_key": day}},
            {
                "$group": {
                    "_id": "$type_id",
                    "total_delivery_cost": {
                        "$sum": {
                            "$multiply": [
                                {
                                    "$add": [
                                        {"$multiply": ["$weight_kg", 0.5]},
                                        {"$multiply": ["$value_usd", 0.01]},
                                    ]
                                },
                                "$usd_rub_rate",
                            ]
                        }
                    },
                    "count_packages": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "total_delivery_cost": {"$round": ["$total_delivery_cost", 2]},
                    "count_packages": 1,
                }
            },
            {"$sort": {"_id": 1}},
        ]
        return await self.collection.aggregate(pipeline).to_list(None)
