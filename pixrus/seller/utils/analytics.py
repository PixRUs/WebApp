from django.db.models import Count
from datetime import datetime, timedelta
from django.utils.timezone import now
from product.models import Subscription
from django.utils.safestring import mark_safe
import json

def get_new_subs(seller):
    # Initialize labels and data
    labels = []
    data = []

    current_date = now()

    # Loop for the last 6 months
    for i in range(6, -1, -1):
        start_of_month = (current_date - timedelta(days=i * 30)).replace(day=1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1)

        # Format the label as "YYYY-MM" or your preferred format
        month_label = start_of_month.strftime("%Y-%m")
        labels.append(month_label)

        # Count subscriptions within this month for the given seller
        monthly_count = Subscription.objects.filter(
            seller=seller,
            subscribed_at__gte=start_of_month,
            subscribed_at__lt=end_of_month
        ).count()

        data.append(monthly_count)

    # Build the chart data dictionary
    chart_data = {
        "labels": labels,
        "series": [{
            "name": "Subscribers",
            "data": data
        }]
    }

    return mark_safe(json.dumps(chart_data))


def get_total_subs(seller):
    current_date = now().date()

    # Filter subscriptions active until this month
    monthly_count = Subscription.objects.filter(
        seller=seller,
        subscribed_until__gte=current_date  # Check if the subscription is still active
    ).count()
    return monthly_count