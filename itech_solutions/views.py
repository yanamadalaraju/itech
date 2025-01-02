from django.shortcuts import render, redirect
from .models import Software
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.conf import settings
from .models import Software

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_confirmation_email(user_email, user_name, software_name):
    subject = 'Download Confirmation - ITech Solutions'
    message = render_to_string('emails/download_confirmation_email.html', {
        'user_name': user_name,
        'software_name': software_name,
          # Include the download URL
    })
    
    send_mail(
        subject,
        message,  # Plain text message (optional)
        settings.EMAIL_HOST_USER,  # The email address that sends the confirmation email
        [user_email],
        html_message=message  # This sends the HTML version of the email
    )


def home(request):
    if request.method == "POST":
        # Get form data from AJAX request
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        city = request.POST.get('city')
        software_name = request.POST.get('software_name')

        # Email content to admin
        subject_admin = f"Download Request for {software_name}"
        message_admin = f"""
        Name: {name}
        Email: {email}
        Mobile: {mobile}
        City: {city}

        Requested Software: {software_name}
        """
        admin_email = 'itechsolutionsknr@gmail.com'  # Replace with admin's email

        try:
            # Send email to admin
            send_mail(subject_admin, message_admin, email, [admin_email])

            # Send email to user (confirmation email)
            send_confirmation_email(email, name, software_name)

            return JsonResponse({'success': True, 'message': "Email sent successfully!"})
        except Exception as e:
            return JsonResponse({'success': False, 'message': "Failed to send email!"})

    softwares = Software.objects.all()
    return render(request, 'index.html', {'softwares': softwares})



def upload_software(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST['description']
        uploaded_file = request.FILES['file']

        if not uploaded_file.name.endswith('.exe'):
            return render(request, 'software_form.html', {
                'error': 'Only .exe files are allowed.',
            })

        # Save data to the database
        software = Software(name=name, description=description, file=uploaded_file)
        software.save()

        return redirect('software_list')  # Redirect to the list page after upload

    return render(request, 'software_form.html')



def software_list(request):
    softwares = Software.objects.all()
    return render(request, 'list.html', {'softwares': softwares})



from django.shortcuts import get_object_or_404
def update_software(request, id):
    software = get_object_or_404(Software, id=id)  # Get the software object by id

    if request.method == 'POST':
        software.name = request.POST.get('name')
        software.description = request.POST.get('description')

        # Handle file upload
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            software.file = uploaded_file  # Replace with the new file

        software.save()  # Save the updated software instance
        return redirect('software_list')  # Redirect to the software list page after updating

    return render(request, 'update_form.html', {'software': software})



def delete_software(request, id):
    software = get_object_or_404(Software, id=id)
    software.delete()
    return redirect('software_list')  # Redirect to the software list


from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages

def contact(request):
    if request.method == "POST":
        # Get data from form
        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        message = request.POST.get('message')

        # Email Subject and Body
        subject = f"New Contact Form Submission from {name}"
        body = f"""
        Name: {name}
        Email: {email}
        Mobile: {mobile}

        Message:
        {message}
        """

        try:
            # Send email to admin
            send_mail(
                subject,
                body,
                email,  # From email (user's email)
                ['itechsolutionsknr@gmail.com'],  # Replace with admin's email
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')  # Redirect to the same page
        except Exception as e:
            messages.error(request, "Failed to send your message. Please try again later.")
    
    return render(request, 'contact.html')

 # Import Profile if you're using it


from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile  # Import the UserProfile model

ROLE_CHOICES = [
    ('Admin', 'Admin'),
    ('User', 'User'),
]
def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        role = request.POST['role']

        if password == confirm_password:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists")
            else:
                # Create a new user
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # Create a UserProfile instance and assign the role
                UserProfile.objects.create(user=user, role=role)

                messages.success(request, "Registration successful! Please log in.")
                return redirect('login')
        else:
            messages.error(request, "Passwords do not match")
    return render(request, 'authentication/register.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Log in the user
            login(request, user)

            # Retrieve the user's profile and set session variables
            user_profile = UserProfile.objects.get(user=user)
            request.session['username'] = user.username  # Store username in session
            request.session['role'] = user_profile.role  # Store role in session

           
            return redirect('home')

        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'authentication/login.html')


@login_required
def logout_view(request):
    # Clear all session data
    request.session.flush()
    logout(request)
    messages.success(request, "You have been logged out")
    return redirect('login')



