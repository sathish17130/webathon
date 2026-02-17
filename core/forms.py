from django import forms


class PreferenceWeightsForm(forms.Form):
    """
    Dynamic preference controls (budget + per-spec weights) for a category.

    - Budget is optional.
    - A slider is created for each numeric SpecificationField.
    """

    budget = forms.FloatField(
        label="Budget (optional)",
        required=False,
        min_value=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Max price (e.g., 80000)", "step": "any"}
        ),
        help_text="Items with price > budget are excluded (requires a numeric 'price' spec).",
    )

    def __init__(self, *args, spec_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._spec_fields = list(spec_fields or [])

        for sf in self._spec_fields:
            if sf.field_type != "number":
                continue

            field_name = f"weight__{sf.name}"
            label = f"{sf.name.replace('_', ' ').title()} importance"

            # Default slider value: admin weight scaled to 0-100 (nice starting point)
            default_val = int(round(float(sf.weight or 0) * 100))
            default_val = max(0, min(100, default_val))

            self.fields[field_name] = forms.FloatField(
                label=label,
                required=False,
                min_value=0,
                max_value=100,
                initial=default_val,
                widget=forms.NumberInput(
                    attrs={
                        "class": "form-control weight-slider",
                        "type": "range",
                        "min": "0",
                        "max": "100",
                        "step": "1",
                        "data-spec": sf.name,
                    }
                ),
                help_text="0 = ignore, 100 = very important",
            )

    def get_user_weights(self):
        """
        Return dict: {spec_name: user_weight_float}
        Only numeric spec fields are included.
        """
        weights = {}
        for sf in self._spec_fields:
            if sf.field_type != "number":
                continue
            raw = self.cleaned_data.get(f"weight__{sf.name}")
            try:
                weights[sf.name] = float(raw) if raw is not None else 0.0
            except (TypeError, ValueError):
                weights[sf.name] = 0.0
        return weights


class UserItemEntryForm(forms.Form):
    """
    Dynamic form: fields are created from SpecificationField rows for a category.

    Used with a Django formset so users can enter multiple items (e.g., 3-5 laptops).
    """

    item_name = forms.CharField(
        label="Item Name",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Dell XPS 13"}),
    )

    def __init__(self, *args, spec_fields=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._spec_fields = list(spec_fields or [])

        for sf in self._spec_fields:
            field_key = sf.name
            label = f"{sf.name.replace('_', ' ').title()}"

            if sf.field_type == "number":
                self.fields[field_key] = forms.FloatField(
                    label=label,
                    required=True,
                    widget=forms.NumberInput(
                        attrs={"class": "form-control", "step": "any", "placeholder": f"Enter {sf.name}"}
                    ),
                    help_text=f"Weight: {sf.weight}",
                )
            else:
                self.fields[field_key] = forms.CharField(
                    label=label,
                    required=True,
                    widget=forms.TextInput(attrs={"class": "form-control", "placeholder": f"Enter {sf.name}"}),
                    help_text="Text spec (displayed, not scored)",
                )

    def get_specifications(self):
        """
        Return a JSON-serializable dict of specs for this form based on spec fields.
        """
        specs = {}
        for sf in self._spec_fields:
            specs[sf.name] = self.cleaned_data.get(sf.name)
        return specs
