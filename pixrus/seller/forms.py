from django import forms
from django.core.exceptions import ValidationError

from .models import Seller

class Subscription(forms.Form):
    SUB_CHOICES = [
        ('monthly', 'Monthly Plan - $20/month'),
        ('weekly', 'Weekly Plan - $10/week'),
        ('yearly', 'Yearly Plan - $8/month'),
    ]
    plan = forms.ChoiceField(
        choices=SUB_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Select Your Subscription Plan'
    )

class LookUp(forms.Form):
    SPORT_LEAGUE_CHOICES = [
        ('basketball_nba', 'Basketball: NBA'),
        ('americanfootball_nfl','Football: NFL'),
        ('americanfootball_ncaaf','Football: NCAA'),
        ('icehockey_nhl', 'US Icehockey: NHL'),
    ]
    sports_league_choice = forms.ChoiceField(choices=SPORT_LEAGUE_CHOICES, widget=forms.RadioSelect, label='Select Your sport and league')

    TYPE_OF_BETS = [
        ('h2h', 'Money Line'),
        ('any','any')
    ]
    type_of_bets = forms.ChoiceField(choices=TYPE_OF_BETS, widget=forms.RadioSelect, label='Select your type of bet')

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['user_name', 'bio', 'profile_picture']
        labels = {
            'user_name': 'Display Name',
            'bio': 'About Me',
            'profile_picture': '',
        }
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'd-none',
                'id': 'profilePictureInput',
                'accept': 'image/*',
            }),
            'user_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
            })
        }

    def clean_user_name(self):
        print("Clean user name is being called")
        user_name = self.cleaned_data['user_name']
        # Check if any other seller (excluding current one) has this username
        if Seller.objects.exclude(pk=self.instance.pk).filter(user_name=user_name).exists():
            print("Username already exists")
            raise ValidationError(f'The username "{user_name}" is already taken by another seller.')
        return user_name
