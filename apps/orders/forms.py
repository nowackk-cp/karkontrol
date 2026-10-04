from django import forms

from .models import OrderLine


class UploadForm(forms.Form):
    file = forms.FileField(
        label="Sipariş dosyası",
        widget=forms.ClearableFileInput(
            attrs={"accept": ".csv,.xlsx", "data-testid": "order-file"}
        ),
    )


class OrderFilterForm(forms.Form):
    start = forms.DateField(
        required=False,
        label="Başlangıç",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    end = forms.DateField(
        required=False,
        label="Bitiş",
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
    )
    product = forms.CharField(required=False, max_length=200, label="Ürün veya kod")

    def clean(self):
        data = super().clean()
        if data.get("start") and data.get("end") and data["start"] > data["end"]:
            raise forms.ValidationError("Başlangıç tarihi bitiş tarihinden sonra olamaz.")
        return data


class ReturnForm(forms.ModelForm):
    class Meta:
        model = OrderLine
        fields = ["returned_quantity"]
        widgets = {"returned_quantity": forms.NumberInput(attrs={"data-testid": "return-quantity"})}
