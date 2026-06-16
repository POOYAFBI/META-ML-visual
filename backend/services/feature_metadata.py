from __future__ import annotations

from typing import Any

FEATURE_FA = {
    "OverallQual": "کیفیت کلی ساختمان",
    "OverallCond": "وضعیت کلی ساختمان",
    "GrLivArea": "زیربنای قابل سکونت",
    "YearBuilt": "سال ساخت",
    "YearRemodAdd": "سال بازسازی",
    "LotArea": "مساحت زمین",
    "TotalBsmtSF": "مساحت زیرزمین",
    "TotalSF": "مساحت کل",
    "GarageArea": "مساحت پارکینگ",
    "GarageCars": "ظرفیت پارکینگ",
    "FullBath": "حمام کامل",
    "BedroomAbvGr": "تعداد اتاق خواب",
    "TotRmsAbvGrd": "تعداد اتاق‌ها",
    "Fireplaces": "تعداد شومینه",
    "Neighborhood": "محله",
}
AREA_FEATURES = {"GrLivArea", "LotArea", "TotalBsmtSF", "1stFlrSF", "2ndFlrSF", "LowQualFinSF", "GarageArea", "WoodDeckSF", "OpenPorchSF", "EnclosedPorch", "3SsnPorch", "ScreenPorch", "PoolArea", "TotalSF", "TotalPorchSF"}
GENERAL_FEATURES = {"MSSubClass", "YearBuilt", "YearRemodAdd", "HouseAge", "YearsSinceRemod", "MoSold", "YrSold"}
QUALITY_FEATURES = {"OverallQual", "OverallCond", "OverallScore"}
AMENITY_FEATURES = {"FullBath", "HalfBath", "BedroomAbvGr", "KitchenAbvGr", "TotRmsAbvGrd", "Fireplaces", "GarageCars", "TotalBathrooms", "HasGarage", "HasBasement", "HasFireplace", "IsRemodeled"}


def feature_meta(name: str) -> dict[str, Any]:
    raw_name = name
    one_hot = "_" in name and name not in {"TotalSF_x_OverallQual"}
    prefix, value = name.split("_", 1) if one_hot else (name, "")
    if prefix == "Neighborhood":
        group, label_fa, input_kind = "محله", f"محله: {value}", "oneHotOption"
    elif name in GENERAL_FEATURES:
        group, label_fa, input_kind = "مشخصات کلی", FEATURE_FA.get(name, name), "number"
    elif name in AREA_FEATURES:
        group, label_fa, input_kind = "مساحت‌ها", FEATURE_FA.get(name, name), "number"
    elif name in QUALITY_FEATURES or name.endswith("_encoded"):
        group, label_fa, input_kind = "کیفیت و وضعیت", FEATURE_FA.get(name, name.replace("_encoded", " کدگذاری‌شده")), "number"
    elif name in AMENITY_FEATURES:
        group, label_fa, input_kind = "امکانات", FEATURE_FA.get(name, name), "number"
    elif one_hot:
        group, label_fa, input_kind = "featureهای فنی", f"{prefix}: {value}", "oneHotOption"
    else:
        group, label_fa, input_kind = "featureهای فنی", FEATURE_FA.get(name, name), "number"
    unit = "sqft" if name in AREA_FEATURES or name.endswith("SF") or name == "LotArea" else "year" if "Year" in name or name == "YearBuilt" else ""
    help_text = f"نام خام مدل: {raw_name}" + (f"؛ واحد: {unit}" if unit else "")
    return {
        "name": name,
        "raw_name": raw_name,
        "rawName": raw_name,
        "display_name_fa": label_fa,
        "display_name_en": name,
        "labelFa": label_fa,
        "labelEn": name,
        "rawFeature": raw_name,
        "raw_feature": raw_name,
        "feature_group": group,
        "group": group,
        "unit": unit,
        "help_text": help_text,
        "help": help_text,
        "input_kind": input_kind,
        "inputKind": input_kind,
        "oneHotGroup": prefix if input_kind == "oneHotOption" else None,
        "oneHotValue": value if input_kind == "oneHotOption" else None,
        "type": "number",
        "default": 0,
    }
