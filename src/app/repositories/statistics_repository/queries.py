def user_project_tasks_counts_query(user_id: str):
    return [
        {"$match": {"user_id": user_id}},
        {"$lookup": {
            "from": "tasks",
            "let": {"pid": "$project_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$project", "$$pid"]}}},
                {"$count": "count"}
            ],
            "as": "task_stats"
        }},
        {"$lookup": {
            "from": "project_users",
            "let": {"pid": "$project_id"},
            "pipeline": [
                {"$match": {"$expr": {"$eq": ["$project_id", "$$pid"]}}},
                {"$count": "count"}
            ],
            "as": "user_stats"
        }},
        {"$addFields": {
            "users_count": {"$ifNull": [{"$arrayElemAt": ["$task_stats.count", 0]}, 0]},
            "tasks_count": {"$ifNull": [{"$arrayElemAt": ["$user_stats.count", 0]}, 0]}
        }},
        {"$project": {
            "_id": 0,
            "project_id": 1,
            "tasks_count": 1,
            "users_count": 1,
        }}
    ]


def task_statuses_count_query(project_ids: list[int]):
    return [
        {"$match": {"project": {"$in": project_ids}}},
        {"$group": {
            "_id": {"project": "$project", "status": "$status"},
            "count": {"$count": {}},
        }},
        {"$group": {
            "_id": "$_id.project",
            "status_counts": {
                "$push": {
                    "status": "$_id.status",
                    "count": "$count"
                }
            },
            "total_tasks": {"$sum": "$count"}
        }},
        {"$addFields": {
            "task_statuses": {
                "$map": {
                    "input": "$status_counts",
                    "as": "item",
                    "in": {
                        "status": "$$item.status",
                        "counts": {
                            "amount": "$$item.count",
                            "percent": {
                                "$round": [
                                    {"$multiply": [{"$divide": ["$$item.count", "$total_tasks"]}, 100]},
                                    2
                                ]
                            }
                        }
                    }
                }
            }
        }},
        {"$project": {
            "_id": 0,
            "project_id": "$_id",
            "task_statuses": 1,
            "total_tasks": 1,
        }},
    ]


def finished_in_week_tasks_count_query(project_id: int, user_id: str):
    return [
        {"$match": {"user_id": str(user_id), "project_id": project_id}},
        {"$lookup": {
            "from": "tasks",
            "let": {
                "pid": "$project_id",
                "uid": "$user_id",
                "weekAgo": {
                    "$dateSubtract": {
                        "startDate": "$$NOW",
                        "unit": "day",
                        "amount": 7
                    }
                }
            },
            "pipeline": [
                {"$match": {"$expr": {"$and": [
                    {"$eq": ["$project", "$$pid"]},
                    {"$eq": ["$finished_user", "$$uid"]},
                    {"$gte": [{"$toDate": "$finished_at"}, "$$weekAgo"]}
                ]
                }}},
                {"$count": "count"}
            ],
            "as": "tasks"
        }},
        {"$project": {
            "_id": 0,
            "project_id": 1,
            "user_id": 1,
            "tasks_count": {"$ifNull": [{"$arrayElemAt": ["$tasks.count", 0]}, 0]}
        }}
    ]


def project_tasks_average_duration_query(project_id: int):
    return [
        {"$match": {
            "project": project_id,
            "finished_at": {"$exists": True, "$ne": None},
            "created_at": {"$exists": True, "$ne": None}
        }},
        {"$addFields": {
            "duration_ms": {"$subtract": [
                {"$toDate": "$finished_at"},
                {"$toDate": "$created_at"}
            ]}
        }},
        {"$group": {
            "_id": "$project",
            "avg_duration_ms": {"$avg": "$duration_ms"},
            "tasks_count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "project_id": "$_id",
            "avg_duration_ms": 1,
            "avg_duration_hours": {
                "$divide": ["$avg_duration_ms", 1000 * 60 * 60]
            },
            "tasks_count": 1
        }}
    ]
