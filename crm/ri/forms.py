from django import forms
from .models import Warehouse, Unit, Good, Counterparty, Documents, Doctype, Goods_in_stock, User

import datetime

class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'address']


class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['name']


class GoodForm(forms.ModelForm):
    class Meta:
        model = Good
        fields = ['name']

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['unit'].queryset = Unit.objects.all()
    #     self.fields['name'].widget.attrs.update({'onchange': 'update_unit_field(this.value)'})


class CounterpartyForm(forms.ModelForm):
    class Meta:
        model = Counterparty
        fields = ['name', 'first_name', 'last_name', 'id_card', 'phone']


class GoodsInStockForm(forms.ModelForm):
    class Meta:
        model = Goods_in_stock
        fields = ['Good', 'Quantity', 'Sum']


class DocumentForm(forms.ModelForm):
    Date = forms.DateTimeField(
        input_formats=['%Y-%m-%dT%H:%M'],  # Укажите формат даты и времени
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    class Meta:
        model = Documents
        exclude = ['Title']

    def __init__(self, *args, **kwargs):
        document_type = kwargs.pop('document_type', None)
        super().__init__(*args, **kwargs)

        # Add select fields for Author, Warehouse, Counterparty
        self.fields['Author'].queryset = User.objects.all()  # Assuming Author field relates to User model
        self.fields['Warehouse'].queryset = Warehouse.objects.all()
        self.fields['Counterparty'].queryset = Counterparty.objects.all()

        if document_type:
            doctype_object = Doctype.objects.get(name__iexact=document_type)
            self.fields['Doctype'].initial = doctype_object
            self.fields['Doctype'].disabled = True

        self.fields['Date'].widget = forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')

    def clean(self):
        cleaned_data = super().clean()
        doctype = cleaned_data.get('Doctype')
        date = cleaned_data.get('Date')
        amount = cleaned_data.get('Amount')

        if doctype and date and amount:
            title = f"{doctype} - {date} - {amount}"
            cleaned_data['Title'] = title

        return cleaned_data

