from django import forms

from .models import Store


class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = ["name", "marketplace", "commission_percent"]

    def __init__(self, *args, owner, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.owner = owner
        for name, field in self.fields.items():
            field.widget.attrs["data-testid"] = f"store-{name}"

    def clean_name(self):
        name = self.cleaned_data["name"]
        if Store.objects.filter(owner=self.instance.owner, name=name).exists():
            raise forms.ValidationError("Bu adla bir mağazanız zaten var.")
        return name
