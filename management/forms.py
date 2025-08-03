from django import forms
from store.models import Product, Order, FarmTool, Staff, Inventory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'price', 'stock', 'image', 'weight', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        price = cleaned_data.get('price')
        stock = cleaned_data.get('stock')
        if price is not None and price < 0:
            raise forms.ValidationError("Price cannot be negative.")
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return cleaned_data

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'shipping_address', 'shipping_city', 'shipping_country', 'shipping_postal_code']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Shipping Address'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'shipping_country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
        }

class FarmToolForm(forms.ModelForm):
    class Meta:
        model = FarmTool
        fields = ['name', 'tool_type', 'description', 'serial_number', 'location', 'purchase_date', 'cost', 'is_operational']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tool Name'}),
            'tool_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Serial Number'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'purchase_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_operational': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean_serial_number(self):
        serial_number = self.cleaned_data.get('serial_number')
        if serial_number and FarmTool.objects.filter(serial_number=serial_number).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Serial number must be unique.")
        return serial_number

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['user', 'date_of_birth', 'state', 'country', 'address', 'phone', 'certification', 'hire_date', 'job_title', 'location', 'is_active']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}),
            'certification': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class InventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['product', 'farm_tool', 'location', 'quantity', 'unit']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'farm_tool': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unit (e.g., kg, units)'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        farm_tool = cleaned_data.get('farm_tool')
        quantity = cleaned_data.get('quantity')
        if not product and not farm_tool:
            raise forms.ValidationError("Either a product or farm tool must be selected.")
        if product and farm_tool:
            raise forms.ValidationError("Select only one: product or farm tool.")
        if quantity is not None and quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative.")
        return cleaned_data