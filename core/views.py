import json
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from .models import Category, SpecificationField, UserItem
from .forms import UserItemEntryForm, PreferenceWeightsForm
from .services.comparison_engine import rank_items
from .services.ai_service import generate_explanation


def home(request):
    """Home view displaying all categories."""
    categories = Category.objects.all().order_by('name')
    context = {
        'categories': categories
    }
    return render(request, 'home.html', context)


def compare(request, category_id):
    """Dynamic compare: render spec-driven formset for a category."""
    category = get_object_or_404(Category, id=category_id)

    spec_fields = SpecificationField.objects.filter(category=category).order_by("name")
    numeric_spec_fields = [sf for sf in spec_fields if sf.field_type == "number"]

    # Formset for multiple user-entered items
    FormSet = formset_factory(UserItemEntryForm, extra=3, can_delete=True)

    if request.method == 'POST':
        formset = FormSet(request.POST, form_kwargs={"spec_fields": spec_fields})
        pref_form = PreferenceWeightsForm(request.POST, spec_fields=spec_fields)

        if formset.is_valid() and pref_form.is_valid():
            created_ids = []
            for form in formset:
                if not form.cleaned_data:
                    continue
                if form.cleaned_data.get("DELETE"):
                    continue

                item_name = form.cleaned_data.get("item_name")
                specs = form.get_specifications()

                user_item = UserItem.objects.create(
                    category=category,
                    item_name=item_name,
                    specifications=specs,
                )
                created_ids.append(user_item.id)

            if not created_ids:
                # No usable forms submitted
                context = {
                    "category": category,
                    "spec_fields": spec_fields,
                    "numeric_spec_fields": numeric_spec_fields,
                    "formset": formset,
                    "pref_form": pref_form,
                    "error": "Please enter at least one item to analyze.",
                }
                return render(request, "compare.html", context)

            request.session[f"comparex_useritem_ids_{category_id}"] = created_ids
            request.session[f"comparex_prefs_{category_id}"] = {
                "budget": pref_form.cleaned_data.get("budget"),
                "user_weights": pref_form.get_user_weights(),
            }
            return redirect("core:result", category_id=category_id)
    else:
        formset = FormSet(form_kwargs={"spec_fields": spec_fields})
        pref_form = PreferenceWeightsForm(spec_fields=spec_fields)

    context = {
        'category': category,
        "spec_fields": spec_fields,
        "numeric_spec_fields": numeric_spec_fields,
        "formset": formset,
        "pref_form": pref_form,
    }
    return render(request, 'compare.html', context)


def result(request, category_id):
    """Result view: rank dynamic user-entered items for a category."""
    category = get_object_or_404(Category, id=category_id)
    spec_fields = SpecificationField.objects.filter(category=category).order_by("name")

    ids = request.session.get(f"comparex_useritem_ids_{category_id}", [])
    if not ids:
        return redirect("core:compare", category_id=category_id)

    prefs = request.session.get(f"comparex_prefs_{category_id}", {}) or {}
    budget = prefs.get("budget")
    user_weights = prefs.get("user_weights", {}) or {}

    items = list(UserItem.objects.filter(id__in=ids, category=category))
    ranked_items, best_item = rank_items(items, spec_fields, user_weights=user_weights, budget=budget)

    if not ranked_items:
        context = {
            "category": category,
            "error": "No items to rank. Please enter items again.",
            "chart_labels": json.dumps([]),
            "chart_scores": json.dumps([]),
            "budget": budget,
            "user_weights": user_weights,
        }
        return render(request, "result.html", context)

    # Chart data
    chart_labels_json = json.dumps([item.item_name for item, _ in ranked_items])
    chart_scores_json = json.dumps([score for _, score in ranked_items])

    # Build a table-friendly structure: list of dict rows
    result_rows = []
    for item, score in ranked_items:
        row = {
            "item": item,
            "score": score,
            "specs": item.specifications or {},
        }
        result_rows.append(row)

    ai_explanation = generate_explanation(best_item, category) if best_item else "Unable to generate explanation."

    context = {
        "category": category,
        "spec_fields": spec_fields,
        "best_item": best_item,
        "ranked_items": ranked_items,
        "result_rows": result_rows,
        "ai_explanation": ai_explanation,
        "chart_labels": chart_labels_json,
        "chart_scores": chart_scores_json,
        "budget": budget,
        "user_weights": user_weights,
    }
    return render(request, "result.html", context)
