from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Enter Password here'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder':"Enter password again"
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email','password']

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password!=confirm_password:
            raise forms.ValidationError(
            'Password does not match'
            )
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] ="Enter first name"
        self.fields['last_name'].widget.attrs['placeholder'] ="Enter last name"
        self.fields['phone_number'].widget.attrs['placeholder'] ="Enter phone number"
        self.fields['email'].widget.attrs['placeholder'] ="Enter email address"
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserForm(forms.ModelForm):

# Used META instaed of Meta and wasted more than 2 hours because error cam up as something diffreent. Modelform does not exist etc.
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ('address_line_1','address_line_2','city','state','country','profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class PasswordForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder': 'Enter Password here'
    }))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder':"Enter new password "
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
    'placeholder':"Enter password again "
    }))
    class Meta:
        model = Account
        fields = ('password',)
    def clean(self):
        cleaned_data = super(PasswordForm, self).clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password!=confirm_password:
            raise forms.ValidationError(
            'Password does not match'
            )
    def __init__(self, *args, **kwargs):
        super(PasswordForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
