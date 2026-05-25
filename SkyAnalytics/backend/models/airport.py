"""
Referencia de aeropuertos / códigos IATA (fuente típica: OurAirports CSV).

Sirve para enriquecer SkyAnalytics con códigos estándar, ciudad, país ISO y coordenadas
sin sustituir la tabla operativa `pasajeros`.
"""

from sqlalchemy import Column, Float, Index, Integer, String, Text, text

from models.base import Base


class Airport(Base):
    """
    Una fila por aeropuerto. `iata_code` puede ser NULL (aeropuertos sin código IATA público).

    Formato de import sugerido: https://ourairports.com/data/airports.csv
    """

    __tablename__ = "airports"
    __table_args__ = (
        Index(
            "uq_airports_iata_when_present",
            "iata_code",
            unique=True,
            postgresql_where=text("iata_code IS NOT NULL AND btrim(iata_code) <> ''"),
        ),
        Index("ix_airports_country_iso", "country_iso"),
        Index("ix_airports_city", "city"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    # ID numérico del CSV OurAirports (estable para reimportaciones)
    source_row_id = Column(String(32), nullable=True, unique=True, index=True)
    iata_code = Column(String(3), nullable=True, index=True)
    icao_code = Column(String(4), nullable=True, index=True)
    name = Column(String(500), nullable=False)
    city = Column(String(200), nullable=True)
    country_iso = Column(String(2), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    airport_type = Column(String(50), nullable=True)
    # Metadatos de import
    data_source = Column(String(64), nullable=False, default="ourairports")
    raw_keywords = Column(Text, nullable=True)
