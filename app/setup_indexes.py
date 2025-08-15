from motor.motor_asyncio import AsyncIOMotorDatabase


async def ensure_mongo_indexes(db: AsyncIOMotorDatabase):
    await db.delivery_logs.create_index(
        [("day_key", 1), ("type_id", 1)], name="idx_day_type"
    )

    await db.delivery_logs.create_index([("day_key", 1)], name="idx_day")
