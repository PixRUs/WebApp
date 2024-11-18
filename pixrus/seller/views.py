from django.shortcuts import render
from product.models import ActivePick,HistoricalPick
from pixrus.utils.decorators import role_required

@role_required(required_role='seller')
def seller_landing(request):
    seller = request.user.seller
    except AttributeError:
        return render(request, '403.html', status=403)  
    active_picks = ActivePick.objects.filter(seller=seller)
    historical_picks = HistoricalPick.objects.filter(seller=seller)
    context = {
        'seller': seller,
        'active_picks': active_picks,
        'historical_picks': historical_picks,
    return render(request, 'seller_landing.html')

# Create your views here.
