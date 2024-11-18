from django.shortcuts import render
from pixrus.utils.decorators import role_required

@role_required(required_role='buyer')
def buyer_landing(request):
    """
    try:
        seller = request.user.seller
    except AttributeError:
        return render(request, '403.html', status=403)  
    active_picks = ActivePick.objects.filter(seller=seller)
    historical_picks = HistoricalPick.objects.filter(seller=seller)
    context = {
        'seller': seller,
        'active_picks': active_picks,
        'historical_picks': historical_picks,
    """
    return render(request, 'buyer_landing.html')

