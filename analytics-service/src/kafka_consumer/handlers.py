from motor.motor_asyncio import AsyncIOMotorClient

from settings import settings


async def handle_kafka_model_event(event: dict, object_id: str):
    motor_client = AsyncIOMotorClient(settings.mongo_settings.connection_string)
    db = motor_client[settings.mongo_settings.db_name]
    event_type_split = str(event["type"]).split(".")
    collection_dict = {
        "user": "users",
        "task": "tasks",
        "project": "projects",
        "project_user": "project_users",
    }
    collection = collection_dict[event_type_split[0]]
    action = event_type_split[1]

    match action:
        case "create":
            await db[collection].insert_one(event["object"])
        case "update":
            await db[collection].update_one(
                {
                    "id": event["object"]["id"],
                },
                {"$set": event["object"]},
                upsert=True,
            )
        case "delete":
            if object_id.isnumeric():
                await db[collection].delete_one({"id": int(object_id)})
            else:
                await db[collection].delete_one({"id": object_id})
