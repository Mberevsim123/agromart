from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, Review, Category, Product, Order, Cart
from django.core.exceptions import ValidationError

# Registration Form (User + UserProfile)
class RegisterForm(UserCreationForm):
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Phone number'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4, 'placeholder': 'Address'}), required=False)
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'City'}))
    country = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Country'}))
    postal_code = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Postal Code'}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'border p-2 w-full'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4, 'placeholder': 'Tell us about yourself'}), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'phone', 'address', 'city', 'country', 'postal_code', 'profile_picture', 'bio']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Email'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data['phone'],
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                country=self.cleaned_data['country'],
                postal_code=self.cleaned_data['postal_code'],
                profile_picture=self.cleaned_data['profile_picture'],
                bio=self.cleaned_data['bio']
            )
        return user

# Login Form
class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Password'}))

# User Info Form (Read-only for display)
class UserInfoForm(forms.ModelForm):
    username = forms.CharField(disabled=True, widget=forms.TextInput(attrs={'class': 'border p-2 w-full bg-gray-100'}))
    email = forms.EmailField(disabled=True, widget=forms.EmailInput(attrs={'class': 'border p-2 w-full bg-gray-100'}))

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'phone', 'address', 'city', 'country', 'postal_code', 'preferred_currency', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'border p-2 w-full bg-gray-100', 'disabled': 'true'}),
            'address': forms.Textarea(attrs={'class': 'border p-2 w-full bg-gray-100', 'rows': 4, 'disabled': 'true'}),
            'city': forms.TextInput(attrs={'class': 'border p-2 w-full bg-gray-100', 'disabled': 'true'}),
            'country': forms.TextInput(attrs={'class': 'border p-2 w-full bg-gray-100', 'disabled': 'true'}),
            'postal_code': forms.TextInput(attrs={'class': 'border p-2 w-full bg-gray-100', 'disabled': 'true'}),
            'preferred_currency': forms.TextInput(attrs={'class': 'border p-2 w-full bg-gray-100', 'disabled': 'true'}),
            'bio': forms.Textarea(attrs={'class': 'border p-2 w-full bg-gray-100', 'rows': 4, 'disabled': 'true'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email

# User Profile Form (Editable)
class UserProfileForm(forms.ModelForm):
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Username'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Email'}))

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'phone', 'address', 'city', 'country', 'postal_code', 'profile_picture', 'preferred_currency', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Phone number'}),
            'address': forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4, 'placeholder': 'Address'}),
            'city': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Country'}),
            'postal_code': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Postal Code'}),
            'profile_picture': forms.FileInput(attrs={'class': 'border p-2 w-full'}),
            'preferred_currency': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Preferred Currency (e.g., USD)'}),
            'bio': forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4, 'placeholder': 'Tell us about yourself'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        user = self.instance.user
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            super().save(commit)
        return self.instance

# Password Change Form
class UserPasswordChangeForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Current Password'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'New Password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Confirm New Password'}))

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if not self.user or not authenticate(username=self.user.username, password=current_password):
            raise ValidationError("Current password is incorrect.")

        if new_password != confirm_password:
            raise ValidationError("New password and confirm password do not match.")

        if len(new_password) < 8:
            raise ValidationError("New password must be at least 8 characters long.")

        return cleaned_data

# Product Filter Form
class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'border p-2 w-full'})
    )
    search_query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Search products...'})
    )

# Review Form
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)], attrs={'class': 'border p-2 w-full'}),
            'comment': forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4, 'placeholder': 'Your review...'}),
        }

# Add to Cart Form
class AddToCartForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'border p-2 w-16', 'value': 1}),
        label='Quantity'
    )

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product', None)
        super().__init__(*args, **kwargs)

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if self.product and quantity > self.product.stock:
            raise ValidationError(f"Only {self.product.stock} items available in stock.")
        return quantity

# Order Form (for shipping details)
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['shipping_address', 'shipping_city', 'shipping_country', 'shipping_postal_code']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'class': 'border p-2 w-full', 'rows': 4, 'placeholder': 'Shipping Address'}),
            'shipping_city': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'City'}),
            'shipping_country': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Country'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'border p-2 w-full', 'placeholder': 'Postal Code'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and hasattr(self.user, 'userprofile'):
            profile = self.user.userprofile
            self.initial = {
                'shipping_address': profile.address,
                'shipping_city': profile.city,
                'shipping_country': profile.country,
                'shipping_postal_code': profile.postal_code,
            }

# Payment Form
class PaymentForm(forms.Form):
        PAYMENT_METHODS = (
            ('stripe', 'Credit/Debit Card (Stripe)'),
            ('paypal', 'PayPal'),
            ('bank_transfer', 'Bank Transfer'),
            ('sdd', 'SEPA Direct Debit'),
        )
        payment_method = forms.ChoiceField(choices=PAYMENT_METHODS, widget=forms.RadioSelect(attrs={'class': 'form-radio'}))
        card_number = forms.CharField(max_length=16, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Card Number'}))
        card_expiry = forms.CharField(max_length=5, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'}))
        card_cvc = forms.CharField(max_length=4, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVC'}))
        iban = forms.CharField(max_length=34, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'IBAN'}))
        sdd_mandate = forms.BooleanField(required=False, label="I authorize the SEPA Direct Debit mandate")

        def __init__(self, *args, **kwargs):
            user = kwargs.pop('user', None)
            super().__init__(*args, **kwargs)
            if user and hasattr(user, 'customer') and user.customer.preferred_payment_method:
                self.fields['payment_method'].initial = user.customer.preferred_payment_method

        def clean(self):
            cleaned_data = super().clean()
            payment_method = cleaned_data.get('payment_method')
            card_number = cleaned_data.get('card_number')
            card_expiry = cleaned_data.get('card_expiry')
            card_cvc = cleaned_data.get('card_cvc')
            iban = cleaned_data.get('iban')
            sdd_mandate = cleaned_data.get('sdd_mandate')

            if payment_method in ['stripe', 'paypal']:
                if not (card_number and card_expiry and card_cvc):
                    raise forms.ValidationError("Card number, expiry, and CVC are required for card payments.")
            elif payment_method == 'bank_transfer':
                if not iban:
                    raise forms.ValidationError("IBAN is required for bank transfer.")
            elif payment_method == 'sdd':
                if not iban:
                    raise forms.ValidationError("IBAN is required for SEPA Direct Debit.")
                if not sdd_mandate:
                    raise forms.ValidationError("You must authorize the SEPA Direct Debit mandate.")
            return cleaned_data

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your Message'}))

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data