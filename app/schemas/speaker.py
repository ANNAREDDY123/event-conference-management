from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SpeakerCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
    )

    email: EmailStr

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    bio: str | None = None

    expertise: str | None = Field(
        default=None,
        max_length=500,
    )

    company: str | None = Field(
        default=None,
        max_length=200,
    )

    experience: int = Field(
        default=0,
        ge=0,
    )

    is_active: bool = True


class SpeakerUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    email: EmailStr | None = None

    phone: str | None = Field(
        default=None,
        max_length=30,
    )

    bio: str | None = None

    expertise: str | None = Field(
        default=None,
        max_length=500,
    )

    company: str | None = Field(
        default=None,
        max_length=200,
    )

    experience: int | None = Field(
        default=None,
        ge=0,
    )

    is_active: bool | None = None


class SpeakerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None
    bio: str | None
    expertise: str | None
    company: str | None
    experience: int
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
    )