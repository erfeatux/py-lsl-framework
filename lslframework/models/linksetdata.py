from pydantic import BaseModel, Field
from uuid import UUID

from lslgwlib.models import Avatar, Region, Invetory
from lslframework.config import SLShard


class LinkSetData(BaseModel):
    """Model contains linkset information"""

    id: UUID
    shard: SLShard
    name: str = Field(pattern=r"^[\x20-\x7b\x7d-\x7e]{1,63}$")
    owner: Avatar
    region: Region
    inventory: Invetory | None = None
