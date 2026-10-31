"""Pydantic models for LLM structured output."""

from typing import List
from pydantic import BaseModel, Field


class AnalystResponse(BaseModel):
    """Response from the Analyst step — parses user request into structured criteria."""

    country: str = Field(description="Название страны из запроса пользователя")
    locations: List[str] = Field(
        default_factory=list,
        description="Города и курорты из запроса пользователя. Если нет — пустой массив",
    )
    category: List[int] = Field(
        default_factory=list,
        description="Список звездности отелей из запроса. Если нет — пустой массив",
    )
    preferences: List[str] = Field(
        default_factory=list,
        description="Ключевые требования к отелю из запроса. Если нет — пустой массив",
    )


class HotelCard(BaseModel):
    """Individual hotel card."""

    hotel: str = Field(description="Название отеля")
    category: int = Field(description="Количество звёзд (1-5)")
    description: str = Field(description="Краткое описание-обоснование, почему отель подходит")
    advantages: str = Field(description="Главные фишки отеля")
    nuance: str = Field(description="Нюансы, на что стоит обратить внимание")


class RegionHotels(BaseModel):
    """Region with list of hotels."""

    region: str = Field(description="Название региона/курорта")
    hotels: List[HotelCard] = Field(description="Список отелей в регионе")


class TravelExpertResponse(BaseModel):
    """Response from the Travel Expert step — hotel recommendations."""

    hotelList: List[RegionHotels] = Field(
        description="Список регионов с отелями",
    )
    travelRecommendation: str = Field(
        description="Рекомендация по лучшему времени для отдыха в стране, до 200 символов",
    )
