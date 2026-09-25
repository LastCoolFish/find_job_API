from db.models.ProfileModel import ProfileModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


class ProfileRepository(BaseRepository[ProfileModel]):
    model = ProfileModel
