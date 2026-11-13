def mean_temp(climate: dict, months: list[int]) -> float | None:
    vals = [climate["t2m"].get(m) for m in months if climate["t2m"].get(m) is not None]
    return sum(vals) / len(vals) if vals else None


def annual_precip_mm(climate: dict) -> float | None:
    vals = [v for v in climate["precip"].values() if v is not None]
    return round(sum(v * 30.4 for v in vals)) if len(vals) == 12 else None
