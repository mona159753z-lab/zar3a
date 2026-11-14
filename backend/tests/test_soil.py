from app.services import soil_service as ss


def test_texture():
    assert ss.usda_texture(26.72, 49.62, 23.7) == "sandy clay loam"   # أسيوط
    assert ss.usda_texture(38.3, 31.97, 29.68) == "clay loam"          # الشرقية


def test_estimate_near_and_far():
    e = ss.estimate(30.55, 31.57)             # الشرقية
    assert e and e["point"] == "sharqia" and e["distance_km"] <= 1
    assert ss.estimate(31.2, 29.9) is None    # الإسكندرية: بعيدة عن أي نقطة
    assert ss.estimate(None, None) is None
