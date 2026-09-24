from db.models.SkillModel import SkillModel
from logging_config import get_logger
from repositories.BaseRepository import BaseRepository

logger = get_logger(__name__)


class SkillRepository(BaseRepository[SkillModel]):
    model = SkillModel
