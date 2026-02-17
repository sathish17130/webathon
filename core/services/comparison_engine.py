"""
Comparison Engine Service
Handles scoring and ranking of user-entered items based on admin-defined specifications.
"""

def _safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def _is_price_field(field_name: str) -> bool:
    name = (field_name or "").strip().lower()
    return name == "price" or "price" in name or "cost" in name


def _performance_key(spec_fields):
    """
    Choose a field name to break ties (performance-like).
    """
    for sf in spec_fields:
        if sf.field_type != "number":
            continue
        n = (sf.name or "").lower()
        if "performance" in n:
            return sf.name
    # fallback: processor_score is also common
    for sf in spec_fields:
        if sf.field_type != "number":
            continue
        n = (sf.name or "").lower()
        if "processor" in n or "benchmark" in n:
            return sf.name
    return None


def rank_items(items, spec_fields, user_weights=None, budget=None):
    """
    Rank items using user-defined weights (dynamic per category).

        score += value * user_weight

    Special handling:
    - If spec name is price-like (e.g., "price"), lower is better:
        normalized_price = max_price - price_value
        score += normalized_price * user_weight
    - Budget filter:
        If price > budget, exclude item (only if a numeric price-like spec exists)
    - Tie-break:
        If scores are equal, pick the one with higher performance-like spec value.

    Args:
        items: iterable of UserItem objects (each has .specifications JSON)
        spec_fields: iterable of SpecificationField objects

    Returns:
        (ranked_items, best_item)
        ranked_items: list of (UserItem, score) sorted by score desc
        best_item: UserItem with highest score (or None)
    """
    items_list = list(items or [])
    spec_fields_list = list(spec_fields or [])
    user_weights = dict(user_weights or {})

    if not items_list or not spec_fields_list:
        return [], None

    numeric_fields = [sf for sf in spec_fields_list if sf.field_type == "number"]
    perf_field_name = _performance_key(numeric_fields)

    # Determine max price for normalization (only among submitted items)
    price_field_names = [sf.name for sf in numeric_fields if _is_price_field(sf.name)]
    price_field_name = price_field_names[0] if price_field_names else None

    prices = []
    if price_field_name:
        for item in items_list:
            prices.append(_safe_float((item.specifications or {}).get(price_field_name)))
    max_price = max(prices) if prices else 0.0

    # Budget filter (only applies if we have a price field)
    filtered_items = []
    if budget is not None and price_field_name:
        try:
            budget_val = float(budget)
        except (TypeError, ValueError):
            budget_val = None
        if budget_val is not None:
            for item in items_list:
                price_val = _safe_float((item.specifications or {}).get(price_field_name))
                if price_val <= budget_val:
                    filtered_items.append(item)
        else:
            filtered_items = items_list
    else:
        filtered_items = items_list

    if not filtered_items:
        return [], None

    scored = []
    for item in filtered_items:
        specs = item.specifications or {}
        score = 0.0
        for field in numeric_fields:
            w = _safe_float(user_weights.get(field.name))
            if w == 0:
                continue
            raw_val = _safe_float(specs.get(field.name))

            if price_field_name and field.name == price_field_name:
                normalized_price = max_price - raw_val
                score += normalized_price * w
            else:
                score += raw_val * w

        score = round(score, 2)

        perf_val = _safe_float(specs.get(perf_field_name)) if perf_field_name else 0.0
        scored.append((item, score, perf_val))

    # Sort by score desc, then performance desc
    ranked_triplets = sorted(scored, key=lambda x: (x[1], x[2]), reverse=True)
    ranked = [(item, score) for (item, score, _perf) in ranked_triplets]
    best_item = ranked[0][0] if ranked else None
    return ranked, best_item
