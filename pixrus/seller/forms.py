from django import forms

class Subscription(forms.Form):
    SUB_CHOICES = [
        ('monthly', 'Monthly Plan - $20/month'),
        ('weekly', 'Weekly Plan - $10/week'),
        ('yearly', 'Yearly Plan - $8/month'),
    ]
    plan = forms.ChoiceField(choices=SUB_CHOICES, widget=forms.RadioSelect, label='Select Your Subscription Plan')
