from django import forms
from .models import Product, BuyingCircle

INPUT  = 'w-full px-5 py-3.5 bg-gray-50 border border-gray-200 rounded-2xl font-bold text-sb-navy focus:ring-4 focus:ring-sb-navy/5 focus:bg-white focus:border-sb-navy transition-all outline-none'
SELECT = INPUT


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'product_type', 'price', 'currency', 'unit', 'description', 'is_group_buy', 'min_order_quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'e.g. Industrial Grade Flour'}),
            'category': forms.Select(attrs={'class': SELECT}),
            'product_type': forms.Select(attrs={'class': SELECT}),
            'price': forms.NumberInput(attrs={'class': INPUT, 'placeholder': '0.00', 'min': '0', 'step': '0.01'}),
            'currency': forms.Select(attrs={'class': SELECT}),
            'unit': forms.Select(attrs={'class': SELECT}),
            'description': forms.Textarea(attrs={'class': INPUT, 'rows': 4}),
            'is_group_buy': forms.CheckboxInput(attrs={
                'class': 'w-6 h-6 rounded-lg border-gray-300 text-sb-green focus:ring-sb-green transition-all cursor-pointer',
                'id': 'id_is_group_buy',
            }),
            'min_order_quantity': forms.NumberInput(attrs={
                'class': INPUT,
                'placeholder': 'e.g. 500',
                'min': '0',
                'step': '0.01',
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('is_group_buy') and not cleaned_data.get('min_order_quantity'):
            self.add_error('min_order_quantity', 'Required when Demand Aggregation is enabled.')
        return cleaned_data


class BuyingCircleForm(forms.Form):
    requested_quantity = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': INPUT,
            'placeholder': 'How much do you need?',
            'step': '0.01',
            'id': 'id_requested_quantity',
        }),
        label='Your Requested Quantity',
    )


class JoinCircleForm(forms.Form):
    requested_quantity = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': INPUT,
            'placeholder': 'How much do you need?',
            'step': '0.01',
        }),
        label='Your Requested Quantity',
    )
