from django.shortcuts import render
from .models import BuyingCircle

# Create your views here.

def buying_circle_list(request):
    buying_circles = BuyingCircle.objects.select_related(
        'product',
        'created_by'
    ).all()

    return render(request, 'operations/buying_circle_list.html', {
        'buying_circles': buying_circles
    })