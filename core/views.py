import json
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from .models import Category, SpecificationField, UserItem
from .forms import UserItemEntryForm, PurposeRequirementsForm
from .services.comparison_engine import analyze_products
from .services.ai_service import generate_ai_explanation


def home(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'home.html', {"categories": categories})


def compare(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    # get spec fields ONLY for this category
    spec_fields = SpecificationField.objects.filter(category=category).order_by("name")

    FormSet = formset_factory(UserItemEntryForm, extra=3, can_delete=True)

    if request.method == "POST":
        formset = FormSet(request.POST, form_kwargs={"spec_fields": spec_fields})

        # IMPORTANT: pass category here
        purpose_form = PurposeRequirementsForm(request.POST, category=category)

        if formset.is_valid() and purpose_form.is_valid():
            created_ids = []

            for form in formset:
                if not form.cleaned_data:
                    continue
                if form.cleaned_data.get("DELETE"):
                    continue

                item_name = form.cleaned_data.get("item_name")
                if not item_name:
                    continue

                specs = form.get_specifications()

                user_item = UserItem.objects.create(
                    category=category,
                    item_name=item_name,
                    specifications=specs,
                )
                created_ids.append(user_item.id)

            request.session[f"comparex_useritem_ids_{category_id}"] = created_ids
            request.session[f"comparex_purpose_{category_id}"] = purpose_form.cleaned_data.get("purpose")

            request.session[f"comparex_requirements_{category_id}"] = {
                "min_budget": purpose_form.cleaned_data.get("min_budget"),
                "max_budget": purpose_form.cleaned_data.get("max_budget"),
                "min_ram": purpose_form.cleaned_data.get("min_ram"),
                "min_ssd": purpose_form.cleaned_data.get("min_ssd"),
                "optional_gpu_required": purpose_form.cleaned_data.get("optional_gpu_required"),
            }

            return redirect("core:result", category_id=category_id)

    else:
        # 🔴 THIS IS THE GET PART YOU ASKED
        formset = FormSet(form_kwargs={"spec_fields": spec_fields})

        # IMPORTANT: pass category here
        purpose_form = PurposeRequirementsForm(category=category)

    context = {
        "category": category,
        "spec_fields": spec_fields,
        "formset": formset,
        "purpose_form": purpose_form,
    }

    return render(request, "compare.html", context)

    category = get_object_or_404(Category, id=category_id)
    spec_fields = SpecificationField.objects.filter(category=category).order_by("name")

    FormSet = formset_factory(UserItemEntryForm, extra=3, can_delete=True)

    if request.method == 'POST':
        formset = FormSet(request.POST, form_kwargs={"spec_fields": spec_fields})
        purpose_form = PurposeRequirementsForm(request.POST, category=category)

        if formset.is_valid() and purpose_form.is_valid():
            created_ids = []

            for form in formset:
                if not form.cleaned_data:
                    continue
                if form.cleaned_data.get("DELETE"):
                    continue

                item_name = form.cleaned_data.get("item_name")
                if not item_name:
                    continue

                specs = form.get_specifications()

                user_item = UserItem.objects.create(
                    category=category,
                    item_name=item_name,
                    specifications=specs,
                )
                created_ids.append(user_item.id)

            if not created_ids:
                return render(request, "compare.html", {
                    "category": category,
                    "spec_fields": spec_fields,
                    "formset": formset,
                    "purpose_form": purpose_form,
                    "error": "Please enter at least one item."
                })

            request.session[f"comparex_useritem_ids_{category_id}"] = created_ids
            request.session[f"comparex_purpose_{category_id}"] = purpose_form.cleaned_data.get("purpose")
            request.session[f"comparex_requirements_{category_id}"] = {
                "min_budget": purpose_form.cleaned_data.get("min_budget"),
                "max_budget": purpose_form.cleaned_data.get("max_budget"),
                "min_ram": purpose_form.cleaned_data.get("min_ram"),
                "min_ssd": purpose_form.cleaned_data.get("min_ssd"),
                "optional_gpu_required": purpose_form.cleaned_data.get("optional_gpu_required", False),
            }

            return redirect("core:result", category_id=category_id)

    else:
        formset = FormSet(form_kwargs={"spec_fields": spec_fields})
        purpose_form = PurposeRequirementsForm()

    return render(request, 'compare.html', {
        'category': category,
        "spec_fields": spec_fields,
        "formset": formset,
        "purpose_form": purpose_form,
    })


def result(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    spec_fields = SpecificationField.objects.filter(category=category).order_by("name")

    ids = request.session.get(f"comparex_useritem_ids_{category_id}", [])
    if not ids:
        return redirect("core:compare", category_id=category_id)

    purpose = request.session.get(f"comparex_purpose_{category_id}")
    requirements = request.session.get(f"comparex_requirements_{category_id}", {}) or {}

    items = list(UserItem.objects.filter(id__in=ids, category=category))

    # ⭐ NEW ENGINE CALL
    ranked_items, best_item, top_group, tradeoff_text = analyze_products(
        purpose, requirements, items
    )

    if not ranked_items:
        return render(request, "result.html", {
            "category": category,
            "error": "No items match your requirements.",
            "chart_labels": json.dumps([]),
            "chart_scores": json.dumps([]),
            "purpose": purpose,
            "requirements": requirements,
        })

    chart_labels_json = json.dumps([item.item_name for item, _ in ranked_items])
    chart_scores_json = json.dumps([score for _, score in ranked_items])

    result_rows = []
    for item, score in ranked_items:
        result_rows.append({
            "item": item,
            "score": score,
            "specs": item.specifications or {},
        })

    # ⭐ AI logic
    # ⭐ Always let AI explain (even if multiple matches)
    ai_explanation = generate_ai_explanation(
        best_item=best_item,
        purpose=purpose,
        requirements=requirements,
        category=category
    )




    purpose_display = {
        "student": "Student",
        "coding": "Coding",
        "gaming": "Gaming",
        "video_editing": "Video Editing",
        "office": "Office",
    }.get(purpose, purpose.title())

    return render(request, "result.html", {
        "category": category,
        "spec_fields": spec_fields,
        "best_item": best_item,
        "ranked_items": ranked_items,
        "top_group": top_group,          # ⭐ NEW
        "tradeoff_text": tradeoff_text,  # ⭐ NEW
        "result_rows": result_rows,
        "ai_explanation": ai_explanation,
        "chart_labels": chart_labels_json,
        "chart_scores": chart_scores_json,
        "purpose": purpose,
        "purpose_display": purpose_display,
        "requirements": requirements,
    })
