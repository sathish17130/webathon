"""
Comparison Engine Service
Handles scoring and ranking of user-entered items based on purpose and requirements.
Now supports:
- Multiple best items (tie detection)
- Trade-off comparison
"""

# How close scores must be to be considered equal
TIE_THRESHOLD = 0.5


# ----------------------------------------------------
# PURPOSE WEIGHTS
# ----------------------------------------------------
PURPOSE_WEIGHTS = {
    "gaming": {
        "gpu_score": 0.4,
        "processor_score": 0.3,
        "ram": 0.2,
        "ssd": 0.1,
    },
    "coding": {
        "processor_score": 0.4,
        "ram": 0.4,
        "ssd": 0.2,
    },
    "student": {
        "price": 0.4,
        "battery": 0.3,
        "ram": 0.3,
    },
    "video_editing": {
        "processor_score": 0.4,
        "ram": 0.3,
        "ssd": 0.3,
    },
    "office": {
        "price": 0.5,
        "ram": 0.3,
        "ssd": 0.2,
    },
}


# ----------------------------------------------------
# REAL WORLD SPEC → SCORE MAP
# ----------------------------------------------------
PROCESSOR_MAP = {
    "i3": 4,
    "i5": 7,
    "i7": 9,
    "i9": 10,
    "ryzen 3": 4,
    "ryzen 5": 7,
    "ryzen 7": 9,
    "ryzen 9": 10,
}

GPU_MAP = {
    "integrated": 2,
    "intel": 2,
    "gtx 1650": 6,
    "rtx 2050": 7,
    "rtx 3050": 8,
    "rtx 3060": 9,
    "rtx 4050": 10,
}


def get_processor_score(name):
    if not name:
        return 0
    name = name.lower()
    for key in PROCESSOR_MAP:
        if key in name:
            return PROCESSOR_MAP[key]
    return 5


def get_gpu_score(name):
    if not name:
        return 0
    name = name.lower()
    for key in GPU_MAP:
        if key in name:
            return GPU_MAP[key]
    return 3


# ----------------------------------------------------

def _safe_float(value):
    try:
        return float(value)
    except:
        return 0.0


def _has_gpu(specs):
    gpu_name = specs.get("gpu_name", "")
    score = get_gpu_score(gpu_name)
    return score > 3


# ----------------------------------------------------
# MAIN ANALYSIS FUNCTION
# ----------------------------------------------------
def analyze_products(purpose, requirements, items):

    items_list = list(items or [])
    if not items_list:
        return [], None, [], None

    # ---------------- FILTER ----------------
    filtered_items = []

    for item in items_list:
        specs = item.specifications or {}

        price = _safe_float(specs.get("price"))
        ram = _safe_float(specs.get("ram"))
        ssd = _safe_float(specs.get("ssd"))

        if requirements.get("max_budget") and price > requirements["max_budget"]:
            continue

        if requirements.get("min_budget") and price < requirements["min_budget"]:
            continue

        if requirements.get("min_ram") and ram < requirements["min_ram"]:
            continue

        if requirements.get("min_ssd") and ssd < requirements["min_ssd"]:
            continue

        if requirements.get("optional_gpu_required"):
            if not _has_gpu(specs):
                continue

        filtered_items.append(item)

    if not filtered_items:
        return [], None, [], None

    # ---------------- SCORING ----------------
    purpose_weights = PURPOSE_WEIGHTS.get(purpose, {})
    scored = []

    prices = [_safe_float((i.specifications or {}).get("price", 0)) for i in filtered_items]
    max_price = max(prices) if prices else 1
    min_price = min(prices) if prices else 0
    price_range = max_price - min_price if max_price > min_price else 1

    for item in filtered_items:
        specs = item.specifications or {}

        processor_name = specs.get("processor_name", "")
        gpu_name = specs.get("gpu_name", "")

        specs["processor_score"] = get_processor_score(processor_name)
        specs["gpu_score"] = get_gpu_score(gpu_name)

        score = 0

        for field_name, weight in purpose_weights.items():
            value = _safe_float(specs.get(field_name, 0))

            if field_name == "price":
                normalized_price = (max_price - value) / price_range
                score += normalized_price * weight
            else:
                score += value * weight

        scored.append((item, round(score, 2)))

    ranked_items = sorted(scored, key=lambda x: x[1], reverse=True)

    if not ranked_items:
        return [], None, [], None

    # ---------------- TIE DETECTION ----------------
    top_score = ranked_items[0][1]

    top_group = [
        (item, score)
        for item, score in ranked_items
        if abs(score - top_score) <= TIE_THRESHOLD
    ]

    best_item = ranked_items[0][0]

    # ---------------- TRADE-OFF TEXT ----------------
    tradeoff_text = None
    if len(top_group) > 1:
        names = [item.item_name for item, _ in top_group]
        tradeoff_text = (
            "These laptops offer very similar performance based on your requirements. "
            "They differ mainly in brand preference, cooling design, and build quality. "
            "Choose based on design preference, portability, or brand trust."
        )

    return ranked_items, best_item, top_group, tradeoff_text
