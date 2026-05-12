"""
Importa airports.csv (formato OurAirports) a la tabla PostgreSQL `airports`.

Fuente oficial del CSV: https://ourairports.com/data/airports.csv

Uso (desde la carpeta `backend/`):
  python scripts/load_ourairports_csv.py --file ruta/al/airports.csv
  python scripts/load_ourairports_csv.py --url https://ourairports.com/data/airports.csv

Por defecto elimina filas con data_source='ourairports' y reinserta (idempotente para reimport).

Para un dev junior: no ejecutes esto en producción en horario pico; el CSV tiene decenas de miles de filas.
"""

from __future__ import annotations

import argparse
import csv
import io
import logging
import sys
from typing import Any, Dict, List, Optional

import requests

_BACKEND = __file__.rsplit("scripts", 1)[0]
if _BACKEND not in sys.path:
    sys.path.insert(0, _BACKEND)

from database import SessionLocal  # noqa: E402
from models.airport import Airport  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_URL = "https://ourairports.com/data/airports.csv"
BATCH = 1500


def _row_to_airport(row: Dict[str, str]) -> Optional[Airport]:
    if row.get("type") == "closed":
        return None
    sid = str(row.get("id", "")).strip()
    if not sid:
        return None
    iso = (row.get("iso_country") or "").strip().upper()
    if len(iso) != 2:
        return None
    name = (row.get("name") or "").strip()
    if not name:
        return None
    iata = (row.get("iata_code") or "").strip().upper() or None
    if iata == "":
        iata = None
    gps = (row.get("gps_code") or "").strip().upper() or None
    ident = (row.get("ident") or "").strip().upper() or None
    icao = gps if gps and len(gps) == 4 else (ident if ident and len(ident) == 4 else None)
    lat_s = row.get("latitude_deg") or ""
    lon_s = row.get("longitude_deg") or ""
    try:
        lat = float(lat_s) if lat_s not in ("", None) else None
        lon = float(lon_s) if lon_s not in ("", None) else None
    except ValueError:
        lat, lon = None, None
    city = (row.get("municipality") or "").strip() or None
    kw = row.get("keywords") or None
    return Airport(
        source_row_id=sid,
        iata_code=iata,
        icao_code=icao,
        name=name[:500],
        city=city[:200] if city else None,
        country_iso=iso,
        latitude=lat,
        longitude=lon,
        airport_type=(row.get("type") or "").strip()[:50] or None,
        data_source="ourairports",
        raw_keywords=kw,
    )


def load_rows(rows: List[Dict[str, str]], db, replace: bool) -> int:
    if replace:
        deleted = db.query(Airport).filter(Airport.data_source == "ourairports").delete()
        db.commit()
        logger.info("Filas eliminadas (ourairports previas): %s", deleted)

    batch: List[Airport] = []
    total = 0
    for row in rows:
        ap = _row_to_airport(row)
        if ap is None:
            continue
        batch.append(ap)
        if len(batch) >= BATCH:
            db.bulk_save_objects(batch)
            db.commit()
            total += len(batch)
            batch.clear()
            logger.info("Insertadas acumuladas: %s", total)
    if batch:
        db.bulk_save_objects(batch)
        db.commit()
        total += len(batch)
    return total


def main() -> None:
    p = argparse.ArgumentParser(description="Carga CSV OurAirports → tabla airports")
    p.add_argument("--file", help="Ruta local a airports.csv")
    p.add_argument("--url", help="URL del CSV", default=None)
    p.add_argument("--no-replace", action="store_true", help="No borrar datos ourairports previos")
    args = p.parse_args()

    text: str
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    else:
        url = args.url or DEFAULT_URL
        logger.info("Descargando %s", url)
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        text = r.text

    reader = csv.DictReader(io.StringIO(text))
    rows = list(reader)
    logger.info("Filas leídas del CSV: %s", len(rows))

    db = SessionLocal()
    try:
        n = load_rows(rows, db, replace=not args.no_replace)
        logger.info("Importación terminada. Aeropuertos insertados: %s", n)
    finally:
        db.close()


if __name__ == "__main__":
    main()
