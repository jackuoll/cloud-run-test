from enum import Enum

from pydantic import BaseSettings


class Environment(str, Enum):
    """Environment enum"""

    local = "local"
    dev = "dev"
    prod = "main"


class PrivateSettings(BaseSettings):
    """Settings that shouldn't be accessed outside of the settings class itself."""

    BRANCH_NAME: str = "local"

    class Config:
        env_file = "../.env"


class Settings(BaseSettings):
    """
    Add settings here, they will read from the environment or .env file
    """

    _private_settings: PrivateSettings = PrivateSettings()

    application: str = ""
    force_gcloud_logging: bool = (
        False  # forces gcloud logging even in local environment
    )

    class Config:
        env_file = ".env"

    @property
    def environment(self) -> Environment:
        """The only reference to environment. Please do not use BRANCH_NAME to determine the environment."""
        return Environment(self._private_settings.BRANCH_NAME)

    @property
    def project(self) -> str:
        if self.environment != Environment.local:
            return "gcp-wow-food-de-pel-prod"
        return "gcp-wow-pel-onetoone-dev"


SETTINGS = Settings()
