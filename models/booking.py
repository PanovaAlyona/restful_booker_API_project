from datetime import date

from pydantic import BaseModel, Field, field_validator


class BookingDates(BaseModel):
    checkin: str = Field(..., description="Дата заезда в формате YYYY-MM-DD")
    checkout: str = Field(
        ..., description="Дата выезда в формате YYYY-MM-DD"
    )

    @field_validator("checkin", "checkout")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Дата должна быть в формате YYYY-MM-DD: {v}")
        return v


class Booking(BaseModel):
    firstname: str = Field(..., min_length=1, description="Имя")
    lastname: str = Field(..., min_length=1, description="Фамилия")
    totalprice: int = Field(..., gt=0, description="Общая стоимость")
    depositpaid: bool = Field(..., description="Депозит оплачен")
    bookingdates: BookingDates = Field(..., description="Даты бронирования")
    additionalneeds: str = Field(..., description="Дополнительные потребности")

    model_config = {"extra": "forbid"}


class BookingResponse(BaseModel):
    bookingid: int = Field(..., description="ID бронирования")
    booking: Booking = Field(..., description="Данные бронирования")

    model_config = {"extra": "forbid"}


class BookingId(BaseModel):
    bookingid: int = Field(..., description="ID бронирования")

    model_config = {"extra": "forbid"}


class AuthCredentials(BaseModel):
    username: str = Field(..., min_length=1, description="Имя пользователя")
    password: str = Field(..., min_length=1, description="Пароль")

    model_config = {"extra": "forbid"}
