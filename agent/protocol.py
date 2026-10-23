from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter


class Move(BaseModel):
    t: Literal["move"]
    dx: int = Field(ge=-500, le=500)
    dy: int = Field(ge=-500, le=500)


class Scroll(BaseModel):
    t: Literal["scroll"]
    dx: int = Field(ge=-20, le=20)
    dy: int = Field(ge=-20, le=20)


class Click(BaseModel):
    t: Literal["click"]
    b: Literal["left", "right", "middle"]


Message = Annotated[Union[Move, Scroll, Click], Field(discriminator="t")]
parse = TypeAdapter(Message).validate_json