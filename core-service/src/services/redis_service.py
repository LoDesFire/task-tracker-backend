import datetime
import pickle
from uuid import UUID

import redis.exceptions
from django_redis import get_redis_connection
from redis import Redis

from apps.todo.dtos.invitation_dtos import InvitationDto


class RedisService:
    def __init__(self, redis_connection_name: str = "default"):
        self._redis_connection_name = redis_connection_name
        self.keys_pattern_dict = {
            "invitation": "invite:{}",
            "status_subscription": "status_subscription:{}",
        }

    def save_invite_link_info(
        self,
        invitation_id: UUID,
        expires_at: datetime.datetime,
        invitation_dict: InvitationDto,
    ):
        invitation_key = self.keys_pattern_dict["invitation"].format(str(invitation_id))

        serialized_data = pickle.dumps(invitation_dict)
        redis_conn: Redis = get_redis_connection(self._redis_connection_name)

        try:
            redis_conn.set(
                name=invitation_key,
                value=serialized_data,
                exat=int(expires_at.timestamp()),
            )
        except redis.exceptions.RedisError:
            return False

        return True

    def get_invite_link_info(self, invitation_id: UUID) -> InvitationDto | None:
        invitation_key = self.keys_pattern_dict["invitation"].format(str(invitation_id))
        redis_conn: Redis = get_redis_connection(self._redis_connection_name)
        try:
            raw_invite_info = redis_conn.get(name=invitation_key)
            if raw_invite_info is None:
                return None
        except redis.exceptions.RedisError:
            return None

        invite_info_dict = pickle.loads(raw_invite_info)

        return invite_info_dict

    def subscribe_user_on_task_statuses(self, task_id, user_id):
        redis_conn: Redis = get_redis_connection(self._redis_connection_name)
        status_subscription_key = self.keys_pattern_dict["status_subscription"].format(
            str(task_id)
        )
        try:
            redis_conn.lpush(status_subscription_key, str(user_id))
        except redis.exceptions.RedisError:
            return False

        return True

    def unsubscribe_user_on_task_statuses(self, task_id, user_id):
        redis_conn: Redis = get_redis_connection(self._redis_connection_name)
        status_subscription_key = self.keys_pattern_dict["status_subscription"].format(
            str(task_id)
        )
        try:
            redis_conn.lrem(status_subscription_key, 0, str(user_id))
        except redis.exceptions.RedisError:
            return False

        return True

    def get_subscribed_users_on_task_statuses(self, task_id):
        redis_conn: Redis = get_redis_connection(self._redis_connection_name)
        status_subscription_key = self.keys_pattern_dict["status_subscription"].format(
            str(task_id)
        )
        try:
            raw_user_ids = redis_conn.lrange(status_subscription_key, 0, -1)
            if not raw_user_ids:
                return None
        except redis.exceptions.RedisError:
            return None

        return [raw_user_id.decode("utf-8") for raw_user_id in raw_user_ids]
