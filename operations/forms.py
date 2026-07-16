from django import forms
from .models import Product, BuyingCircle
from .models import Review
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

    def __init__(self, *args, fixed_product_type=None, allow_group_buy=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.fixed_product_type = fixed_product_type
        if fixed_product_type:
            self.fields.pop('product_type')
        self.allow_group_buy = allow_group_buy
        self.fields.pop('is_group_buy')
        if not allow_group_buy:
            self.fields.pop('min_order_quantity')
        else:
            self.fields['min_order_quantity'].required = True

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.fixed_product_type:
            instance.product_type = self.fixed_product_type
        instance.is_group_buy = self.allow_group_buy
        if not self.allow_group_buy:
            instance.min_order_quantity = None
        if commit:
            instance.save()
        return instance


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


from decimal import Decimal # Import this at the top

class JoinCircleForm(forms.Form):
    requested_quantity = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal('0.01'), # Use string '0.01' to ensure exact precision
        widget=forms.NumberInput(attrs={
            'class': 'w-full h-14 px-5 bg-slate-50 border border-slate-100 rounded-2xl text-lg font-black focus:ring-4 focus:ring-sb-navy/5 outline-none',
            'placeholder': '0.00',
            'step': '0.01',
        }),
        label='Your Requested Quantity',
    )


from .models import Review
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.HiddenInput(), 
            'comment': forms.Textarea(attrs={
                'class': 'w-full rounded-2xl border-slate-100 focus:ring-sb-green p-4 text-sm',
                'placeholder': 'Describe the quality of goods and logistics performance...',
                'rows': 4
            }),
        }