from django import forms

class Subscription(forms.Form):
    SUB_CHOICES = [
        ('monthly', 'Monthly Plan - $20/month'),
        ('weekly', 'Weekly Plan - $10/week'),
        ('yearly', 'Yearly Plan - $8/month'),
    ]
    plan = forms.ChoiceField(choices=SUB_CHOICES, widget=forms.RadioSelect, label='Select Your Subscription Plan')

class LookUp(forms.Form):
    SPORT_LEAGUE_CHOICES = [
        ('basketball_nba', 'Basketball: NBA'),
        ('any', 'any')
    ]
    sports_league_choice = forms.ChoiceField(choices=SPORT_LEAGUE_CHOICES, widget=forms.RadioSelect, label='Select Your sport and league')

    TYPE_OF_BETS = [
        ('money_line', 'Money Line'),
        ('any','any')
    ]
    type_of_bets = forms.ChoiceField(choices=TYPE_OF_BETS, widget=forms.RadioSelect, label='Select your type of bet')
