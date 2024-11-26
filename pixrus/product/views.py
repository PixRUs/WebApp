from django.shortcuts import render
from seller.models import Seller
# Create your views here.
def marketplace_landing(request):
    sellers = Seller.objects.all()
    context = {
        'sellers': sellers,
    }
    return render(request=request,context=context,template_name='marketplace_landing.html')