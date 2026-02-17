"""
Script to add sample data to the database.
Run this after migrations: python manage.py shell < add_sample_data.py
Or run: python manage.py shell, then copy-paste the code below.
"""

from core.models import Category, SpecificationField

# Create categories
categories_data = [
    {"name": "Laptop"},
    {"name": "Phone"},
    {"name": "Tablet"},
]

print("Creating categories...")
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(name=cat_data['name'])
    if created:
        print(f"Created category: {category.name}")
    else:
        print(f"Category already exists: {category.name}")

def add_specs(category_name, specs):
    category = Category.objects.get(name=category_name)
    print(f"\nCreating specs for: {category_name} ...")
    for s in specs:
        sf, created = SpecificationField.objects.get_or_create(
            category=category,
            name=s["name"],
            defaults={"field_type": s.get("field_type", "number"), "weight": s.get("weight", 1.0)},
        )
        if not created:
            # Update weight/type to match this script (handy during iteration)
            sf.field_type = s.get("field_type", sf.field_type)
            sf.weight = s.get("weight", sf.weight)
            sf.save()
        print(f"- {sf.name} ({sf.field_type}, weight={sf.weight})")


# Laptop specs (example)
add_specs(
    "Laptop",
    [
        {"name": "price", "field_type": "number", "weight": 0.4},
        {"name": "performance", "field_type": "number", "weight": 0.3},
        {"name": "battery", "field_type": "number", "weight": 0.2},
        {"name": "graphics", "field_type": "number", "weight": 0.1},
        {"name": "ram", "field_type": "number", "weight": 0.15},
        {"name": "ssd", "field_type": "number", "weight": 0.1},
        {"name": "processor", "field_type": "text", "weight": 0.0},
    ],
)

# Phone specs (example)
add_specs(
    "Phone",
    [
        {"name": "price", "field_type": "number", "weight": 0.35},
        {"name": "camera_score", "field_type": "number", "weight": 0.25},
        {"name": "battery", "field_type": "number", "weight": 0.2},
        {"name": "storage", "field_type": "number", "weight": 0.1},
        {"name": "display_score", "field_type": "number", "weight": 0.1},
        {"name": "chipset", "field_type": "text", "weight": 0.0},
    ],
)

# Tablet specs (example)
add_specs(
    "Tablet",
    [
        {"name": "price", "field_type": "number", "weight": 0.35},
        {"name": "display_score", "field_type": "number", "weight": 0.25},
        {"name": "battery", "field_type": "number", "weight": 0.2},
        {"name": "performance", "field_type": "number", "weight": 0.2},
        {"name": "pen_support", "field_type": "text", "weight": 0.0},
    ],
)

print("\nSample data added successfully!")
print("Next: open /admin to adjust specs, then use the home page to compare by entering items.")
