from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter, field_validator

from .keynames import KEY_NAMES, MOD_NAMES


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


class Key(BaseModel):
    t: Literal["key"]
    k: str
    mods: list[str] = Field(default_factory=list, max_length=4)

    @field_validator("k")
    @classmethod
    def _known_key(cls, v: str) -> str:
        if v not in KEY_NAMES:
            raise ValueError("unknown key")
        return v

    @field_validator("mods")
    @classmethod
    def _known_mods(cls, v: list[str]) -> list[str]:
        if any(m not in MOD_NAMES for m in v):
            raise ValueError("unknown modifier")
        return v


class Text(BaseModel):
    t: Literal["text"]
    s: str = Field(max_length=200)


Message = Annotated[Union[Move, Scroll, Click, Key, Text], Field(discriminator="t")]
parse = TypeAdapter(Message).validate_json