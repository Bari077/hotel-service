"""Pydantic models for LLM structured output."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AnalystResponse(BaseModel):
    """Response from the Analyst step — parses user request into structured criteria."""

    country: str = Field(description="Название страны")
    region: List[str] = Field(
        default_factory=list,
        description="Список курортов/регионов из запроса пользователя. Если нет — пустой массив",
    )
    category: List[int] = Field(
        default_factory=list,
        description="Список звездности отелей из запроса. Если нет — пустой массив",
    )
    preferences: List[str] = Field(
        default_factory=list,
        description="Предпочтения по отелю из запроса пользователя. Если нет — пустой массив",
    )


class HotelCard(BaseModel):
    """Individual hotel card."""

    hotel: str = Field(description="Название отеля")
    category: int = Field(description="Количество звёзд (1-5)")
    description: str = Field(description="Описание отеля, до 200 символов")
    advantages: str = Field(description="Преимущества отеля, до 300 символов")
    nuance: str = Field(description="Нюансы, на что стоит обратить внимание, до 150 символов")
    kindOfLeisure: str = Field(description="Для какого отдыха подойдёт, до 100 символов")


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
