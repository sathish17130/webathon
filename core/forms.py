from django import forms


class PurposeRequirementsForm(forms.Form):

    purpose = forms.ChoiceField(
        label="Purpose",
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    min_budget = forms.FloatField(
        label="Min Budget",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    max_budget = forms.FloatField(
        label="Max Budget",
        required=False,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    # laptop specific filters
    min_ram = forms.FloatField(required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
    min_ssd = forms.FloatField(required=False, widget=forms.NumberInput(attrs={"class": "form-control"}))
    optional_gpu_required = forms.BooleanField(required=False)

    def __init__(self, *args, category=None, **kwargs):
        super().__init__(*args, **kwargs)

        if not category:
            return

        name = category.name.lower()

        # ---------------- LAPTOP ----------------
        if "laptop" in name:
            choices = [
                ("gaming", "Gaming"),
                ("coding", "Coding"),
                ("office", "Office"),
                ("video_editing", "Video Editing"),
                ("student", "Student"),
            ]
            self.fields["purpose"].choices = choices

        # ---------------- MOBILE ----------------
        elif "mobile" in name:
            choices = [
                ("gaming", "Gaming"),
                ("camera", "Camera"),
                ("battery", "Battery"),
                ("performance", "Performance"),
                ("daily_use", "Daily Use"),
            ]
            self.fields["purpose"].choices = choices

            # remove laptop filters
            self.fields.pop("min_ram", None)
            self.fields.pop("min_ssd", None)
            self.fields.pop("optional_gpu_required", None)

        # ---------------- HOSTEL ----------------
        elif "hostel" in name or "pg" in name:
            choices = [
                ("college", "College Student"),
                ("job", "Working Professional"),
                ("budget", "Budget Stay"),
                ("premium", "Premium Stay"),
            ]
            self.fields["purpose"].choices = choices

            self.fields.pop("min_ram", None)
            self.fields.pop("min_ssd", None)
            self.fields.pop("optional_gpu_required", None)

        # ---------------- COURSE ----------------
        elif "course" in name:
            choices = [
                ("job", "Job Ready"),
                ("trending", "Trending"),
                ("certification", "Certification"),
                ("skill_upgrade", "Skill Upgrade"),
                ("beginner", "Beginner"),
            ]
            self.fields["purpose"].choices = choices

            self.fields.pop("min_ram", None)
            self.fields.pop("min_ssd", None)
            self.fields.pop("optional_gpu_required", None)


class UserItemEntryForm(forms.Form):

    item_name = forms.CharField(
        label="Item Name",
        max_length=200,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, spec_fields=None, **kwargs):
        super().__init__(*args, **kwargs)

        self._spec_fields = list(spec_fields or [])

        for sf in self._spec_fields:
            field_key = sf.name
            label = sf.name.replace("_", " ").title()

            if sf.field_type == "number":
                self.fields[field_key] = forms.FloatField(
                    label=label,
                    required=True,
                    widget=forms.NumberInput(attrs={"class": "form-control"}),
                )
            else:
                self.fields[field_key] = forms.CharField(
                    label=label,
                    required=True,
                    widget=forms.TextInput(attrs={"class": "form-control"}),
                )

    def get_specifications(self):
        specs = {}
        for sf in self._spec_fields:
            specs[sf.name] = self.cleaned_data.get(sf.name)
        return specs
