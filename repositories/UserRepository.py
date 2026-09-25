from db.models.UserModel import UserModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


class UserRepository(BaseRepository[UserModel]):
    model = UserModel
