from django.db import models


class Category(models.Model):
    """Category model for organizing comparison items."""
    name = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class SpecificationField(models.Model):
    """
    Admin-defined specification for a given category.

    Example (Category: Laptop):
      - price (number, weight=0.4)
      - performance (number, weight=0.3)
      - battery (number, weight=0.2)
      - graphics (number, weight=0.1)
      - processor (text, weight=0)  # text fields are displayed but not scored
    """

    FIELD_TYPE_NUMBER = "number"
    FIELD_TYPE_TEXT = "text"
    FIELD_TYPE_CHOICES = [
        (FIELD_TYPE_NUMBER, "Number"),
        (FIELD_TYPE_TEXT, "Text"),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="spec_fields")
    name = models.CharField(max_length=100, help_text="Key used in JSON (e.g., price, ram, battery_score)")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPE_CHOICES, default=FIELD_TYPE_NUMBER)
    weight = models.FloatField(default=1.0, help_text="Used only for number fields (higher weight = more impact)")

    def __str__(self):
        return f"{self.category.name} :: {self.name}"

    class Meta:
        unique_together = ("category", "name")
        ordering = ["category__name", "name"]


class UserItem(models.Model):
    """
    User-entered item to compare for a category.

    Specifications are stored as JSON using SpecificationField.name as keys.

    Example JSON:
    {
      "price": 60000,
      "ram": 16,
      "battery_score": 8,
      "processor": "i7"
    }
    """

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="user_items")
    item_name = models.CharField(max_length=200)
    specifications = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} ({self.category.name})"

    class Meta:
        ordering = ["-created_at"]


# Sample data examples (add via Django admin):
#
# 1) Add a Category:
#    - name: "Laptop"
#
# 2) Add SpecificationFields for that category:
#    - price (number, weight 0.4)
#    - performance (number, weight 0.3)
#    - battery (number, weight 0.2)
#    - graphics (number, weight 0.1)
#    - ram (number, weight 0.15)
#    - processor (text)
#
# Users will then enter items on the compare page using these dynamic fields.
