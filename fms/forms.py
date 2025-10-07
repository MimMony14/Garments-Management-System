from django import forms
from django.contrib.auth.models import User
from .models import Production
from .models import DailyWork
from django.contrib.auth.forms import AuthenticationForm
from .models import Attendance
 
class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
class ProductionForm(forms.ModelForm):
    class Meta:
        model = Production
        fields = ['quantity']


class ProductCountForm(forms.ModelForm):
    class Meta:
        model = DailyWork
        fields = ['product_count', 'notes']

class AttendanceEditForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['employee', 'status']

class BonusForm(forms.Form):
    percentage = forms.FloatField(
        label="Bonus Percentage",
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter bonus %'})
    )