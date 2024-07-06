# This file contains the 'views' - they control what happens when a user visits a page

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib import messages as django_messages
from django.core.mail import send_mail
from django.core.serializers import serialize
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, UpdateView, DetailView, ListView
from .models import Event, Message
from .forms import SignUpForm, UserUpdateForm, EventSearchForm
from .forms import ComposeMessageForm
from .utils import geocode_location
from .forms import EventForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.utils import timezone
import json

# This function handles the event map page
def event_map(request):
    # Get all events from the database
    events = Event.objects.all()
    # Convert events to JSON format (for use in JavaScript)
    events_json = serialize('json', events, fields=('name', 'latitude', 'longitude'))
    # Render the map page with the events data
    return render(request, 'events/event_map.html', {'events_json': json.dumps(json.loads(events_json))})

# This class handles user sign up
class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'events/signup.html'
    success_url = reverse_lazy('login')

    # This method is called when valid form data has been POSTed
    def form_valid(self, form):
        response = super().form_valid(form)
        # Log the user in after they sign up
        user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
        login(self.request, user)
        return response

# This function handles the user profile page
@login_required  # This decorator ensures only logged-in users can access this view
def profile_view(request):
    if request.method == 'POST':
        # If the request is POST, process the form data
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        # If the request is GET, show the form
        form = UserUpdateForm(instance=request.user)
    return render(request, 'events/profile.html', {'form': form})

# This function handles the home page
def home(request):
    # Get the next 3 upcoming events
    upcoming_events = Event.objects.filter(start_time__gte=timezone.now()).order_by('start_time')[:3]
    return render(request, 'events/home.html', {'upcoming_events': upcoming_events})

# This function handles the user's inbox
@login_required
def inbox(request):
    # Get all unarchived messages for the current user, ordered by most recent first
    messages = Message.objects.filter(receiver=request.user, archived=False).order_by('-sent_at')
    return render(request, 'events/inbox.html', {'messages': messages})

# This function handles viewing a single message
@login_required
def view_message(request, message_id):
    # Get the message or return a 404 error if not found
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    if not message.read:
        # Mark the message as read
        message.read = True
        message.save()
    return render(request, 'events/view_message.html', {'message': message})

# This function handles composing a new message
@login_required
def compose_message(request):
    if request.method == 'POST':
        form = ComposeMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.save()
            django_messages.success(request, 'Message sent successfully.')
            return redirect('inbox')
    else:
        form = ComposeMessageForm()
    return render(request, 'events/compose_message.html', {'form': form})

# This function handles archiving a message
@login_required
def archive_message(request, message_id):
    message = get_object_or_404(Message, id=message_id, receiver=request.user)
    message.archived = True
    message.save()
    django_messages.success(request, 'Message archived.')
    return redirect('inbox')

# This class handles listing all events
class EventListView(ListView):
    model = Event
    template_name = 'events/event_list.html'
    context_object_name = 'events'
    paginate_by = 10  # Show 10 events per page

    def get_queryset(self):
        # Start with all events
        queryset = Event.objects.all()
        form = EventSearchForm(self.request.GET)
        if form.is_valid():
            # Filter events based on search criteria
            query = form.cleaned_data.get('query')
            category = form.cleaned_data.get('category')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            location = form.cleaned_data.get('location')
            if query:
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query)
                )
            if category:
                queryset = queryset.filter(category=category)
            if start_date:
                queryset = queryset.filter(start_time__date__gte=start_date)
            if end_date:
                queryset = queryset.filter(end_time__date__lte=end_date)
            if location:
                queryset = queryset.filter(location__icontains=location)
        return queryset.order_by('start_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = EventSearchForm(self.request.GET)
        return context

# This class handles displaying details of a single event
class EventDetailView(DetailView):
    model = Event
    template_name = 'events/event_detail.html'
    context_object_name = 'event'

# This class handles creating a new event
class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')

    def form_valid(self, form):
        form.instance.organizer = self.request.user
        location = form.cleaned_data.get('location')
        # Get latitude and longitude for the location
        lat, lng = geocode_location(location)
        form.instance.latitude = lat
        form.instance.longitude = lng
        return super().form_valid(form)

# This class handles updating an existing event
class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        # Check if the current user is the event organizer or has permission to manage all events
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.has_perm('events.can_manage_all_events')

    def form_valid(self, form):
        location = form.cleaned_data.get('location')
        # Update latitude and longitude if location changed
        lat, lng = geocode_location(location)
        form.instance.latitude = lat
        form.instance.longitude = lng
        return super().form_valid(form)

# This class handles deleting an event
class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Event
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('event_list')

    def test_func(self):
        # Check if the current user is the event organizer or has permission to manage all events
        event = self.get_object()
        return self.request.user == event.organizer or self.request.user.has_perm('events.can_manage_all_events')