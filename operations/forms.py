from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'product_type', 'price', 'unit', 'description', 'is_group_buy']
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3.5 bg-gray-50 border border-gray-200 rounded-2xl font-bold text-sb-navy focus:ring-4 focus:ring-sb-navy/5 focus:bg-white focus:border-sb-navy transition-all outline-none',
                'placeholder': 'e.g. Industrial Grade Flour'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-5 py-3.5 bg-gray-50 border border-gray-200 rounded-2xl font-bold text-sb-navy focus:ring-4 focus:ring-sb-navy/5 focus:bg-white focus:border-sb-navy transition-all outline-none'
            }),
            'product_type': forms.Select(attrs={
                'class': 'w-full px-5 py-3.5 bg-gray-50 border border-gray-200 rounded-2xl font-bold text-sb-navy focus:ring-4 focus:ring-sb-navy/5 focus:bg-white focus:border-sb-navy transition-all outline-none'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full px-5 py-3.5 bg-gray-50 border border-gray-200 rounded-2xl font-bold text-sb-navy focus:ring-4 focus:ring-sb-navy/5 focus:bg-white focus:border-sb-navy transition-all outline-none'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'w-full px-5 py-3.5 bg-gray-50 border border-gray-200 rounded-2xl font-bold text-sb-navy focus:ring-4 focus:ring-sb-navy/5 focus:bg-white focus:border-sb-navy transition-all outline-none',
                'placeholder': 'kg, ton, unit'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-5 py-3.5 bg-gray-50 border border-gray-200 rounded-2xl font-bold text-sb-navy focus:ring-4 focus:ring-sb-navy/5 focus:bg-white focus:border-sb-navy transition-all outline-none',
                'rows': 4
            }),
            'is_group_buy': forms.CheckboxInput(attrs={
                'class': 'w-6 h-6 rounded-lg border-gray-300 text-sb-green focus:ring-sb-green transition-all cursor-pointer'
            }),
        }