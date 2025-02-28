import uuid
from pydantic import BaseModel, field_validator


class PlaylistConfig(BaseModel):
    uri: str
    name: str

    @field_validator("name", mode="before")
    def set_name(cls, v: str | None) -> str:
        return v if v else uuid.uuid4().hex
