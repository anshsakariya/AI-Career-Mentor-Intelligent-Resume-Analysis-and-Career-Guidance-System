from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

# Remove default username character validation from User model
User._meta.get_field('username').validators = []

class UserRegistrationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Username'}),
        validators=[]
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'name@example.com'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '+1 555-0199 (Optional)'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].validators = []
        for field_name, field in self.fields.items():
            field.help_text = ''
            current_class = field.widget.attrs.get('class', 'form-control form-control-custom')
            if self.is_bound and self.errors.get(field_name):
                if 'is-invalid' not in current_class:
                    field.widget.attrs['class'] = f"{current_class} is-invalid"
            else:
                field.widget.attrs['class'] = current_class

    def clean_username(self):
        # Allow duplicate usernames (do not raise error if username exists)
        return self.cleaned_data.get('username')

    def validate_unique(self):
        # Exclude username from ModelForm unique validation so duplicate usernames are permitted
        exclude = self._get_validation_exclusions()
        if isinstance(exclude, set):
            exclude.add('username')
        elif isinstance(exclude, list):
            if 'username' not in exclude:
                exclude.append('username')
        try:
            self.instance.validate_unique(exclude=exclude)
        except forms.ValidationError as e:
            self._update_errors(e)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email address already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        base_username = self.cleaned_data.get('username')
        
        # Resolve database username uniqueness
        if User.objects.filter(username__iexact=base_username).exists():
            count = 1
            new_username = f"{base_username}_{count}"
            while User.objects.filter(username__iexact=new_username).exists():
                count += 1
                new_username = f"{base_username}_{count}"
            user.username = new_username
        else:
            user.username = base_username

        if commit:
            user.save()
            if hasattr(user, 'profile'):
                user.profile.full_name = base_username
                if self.cleaned_data.get('phone'):
                    user.profile.phone = self.cleaned_data.get('phone')
                user.profile.save()
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control form-control-custom'}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control form-control-custom'}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control form-control-custom'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A user with that email address already exists.")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'full_name', 'phone', 'location', 'bio',
            'linkedin_url', 'github_url', 'portfolio_url',
            'education', 'degree', 'university', 'graduation_year',
            'experience_level', 'current_role', 'target_role', 
            'years_of_experience', 'key_skills', 'preferred_work_mode',
            'notice_period', 'expected_salary', 'career_goal'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'John Doe'}),
            'phone': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '+1 555-0199'}),
            'location': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'New York, USA'}),
            'bio': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 2, 'placeholder': 'Brief professional summary / bio...'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'https://linkedin.com/in/username'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'https://github.com/username'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'https://yourportfolio.com'}),
            'education': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'MCA / B.Tech / B.Sc CS'}),
            'degree': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Master of Computer Applications'}),
            'university': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'State University'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '2025'}),
            'experience_level': forms.Select(attrs={'class': 'form-select form-select-custom'}),
            'current_role': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Junior Developer / Student'}),
            'target_role': forms.Select(attrs={'class': 'form-select form-select-custom'}),
            'years_of_experience': forms.NumberInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '1'}),
            'key_skills': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': 'Python, Django, REST API, React, SQL'}),
            'preferred_work_mode': forms.Select(attrs={'class': 'form-select form-select-custom'}),
            'notice_period': forms.Select(attrs={'class': 'form-select form-select-custom'}),
            'expected_salary': forms.TextInput(attrs={'class': 'form-control form-control-custom', 'placeholder': '$80,000 / yr or ₹10 LPA'}),
            'career_goal': forms.Textarea(attrs={'class': 'form-control form-control-custom', 'rows': 3, 'placeholder': 'Describe your primary career objective...'}),
        }
