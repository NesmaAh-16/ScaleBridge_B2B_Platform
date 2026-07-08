from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150, required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Corporate Email Address'})
    )
    phone = forms.CharField(
        max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number (optional)'})
    )
    role = forms.ChoiceField(
        choices=[
            ('SmallBusiness', 'Small Business Owner'),
            ('EnterpriseBuyer', 'Enterprise Buyer'),
        ]
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Create Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'role', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone', '')
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'placeholder': 'Corporate ID / Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'placeholder': 'Secure Password'})
    )


from .models import Business
class BusinessProfileForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['business_name', 'location', 'business_type', 'description', 'logo']
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'w-full rounded-xl border-slate-200 p-3 focus:ring-sb-green'}),
            'location': forms.TextInput(attrs={'class': 'w-full rounded-xl border-slate-200 p-3'}),
            'business_type': forms.Select(attrs={'class': 'w-full rounded-xl border-slate-200 p-3'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-xl border-slate-200 p-3', 'rows': 3}),
            'logo': forms.FileInput(attrs={'class': 'w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sb-green/10 file:text-sb-navy hover:file:bg-sb-green/20'}),
        }