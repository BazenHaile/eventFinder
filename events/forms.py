# Import necessary modules
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import Event, Message

# Get the custom user model
User = get_user_model()

# Form for user sign-up
class SignUpForm(UserCreationForm):
    # Add extra fields to the default UserCreationForm
    email = forms.EmailField(max_length=254, help_text='Required. Add a valid email address.')
    bio = forms.CharField(max_length=500, widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)
    contact_phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        # Specify which fields to include in the form
        fields = ('username', 'email', 'password1', 'password2', 'profile_picture', 'bio', 'contact_phone')

# Form for updating user profile
class UserUpdateForm(UserChangeForm):
    # Add extra fields for profile update
    bio = forms.CharField(max_length=500, widget=forms.Textarea, required=False)
    profile_picture = forms.ImageField(required=False)
    contact_phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        # Specify which fields can be updated
        fields = ('username', 'email', 'profile_picture', 'bio', 'contact_phone')

# Form for searching events
class EventSearchForm(forms.Form):
    query = forms.CharField(required=False, label='Search')
    category = forms.ChoiceField(choices=[('', 'All')] + Event.CATEGORY_CHOICES, required=False)
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    location = forms.CharField(required=False)

# Form for creating and updating events
class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        # Specify which fields to include in the form
        fields = ['name', 'description', 'start_time', 'end_time', 'location', 'latitude', 'longitude', 'entrance', 'status', 'category']
        # Customize widgets for some fields
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

# Form for composing messages
class ComposeMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        # Specify which fields to include in the form
        fields = ['receiver', 'subject', 'body']