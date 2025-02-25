from django import forms
from . models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'about']
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell us something about yourself...'}),
        }
