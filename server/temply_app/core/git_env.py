"""Git 환경"""

import logging
import os

from temply_app.core.config import Config
from temply_app.models.common_model import VersionInfo

logger = logging.getLogger(__name__)


class GitEnv:
    """Git 환경"""

    def __init__(self, config: Config, version_info: VersionInfo):
        self.config = config
        self.version_info: VersionInfo = version_info
        self.efs_root_path = os.path.abspath(self.config.noti_temply_dir)
        self.version_path = f"{self.efs_root_path}/{self.version_info.version}"
