from django.test import TestCase
from django.contrib.auth.models import User
from accounts.models import Profile

class AccountsTestCases(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password123',
            first_name='Test',
            last_name='User'
        )

    def test_profile_signal_creation(self):
        """Test that profile is automatically created when a User is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.full_name, 'Test User')
        self.assertEqual(self.user.profile.target_role, 'Python Developer')

    def test_profile_update(self):
        """Test updating profile target role and career goal."""
        profile = self.user.profile
        profile.target_role = 'Django Developer'
        profile.years_of_experience = 3
        profile.save()

        updated_profile = Profile.objects.get(user=self.user)
        self.assertEqual(updated_profile.target_role, 'Django Developer')
        self.assertEqual(updated_profile.years_of_experience, 3)

    def test_registration_form_relaxed_validations(self):
        """Test registration allows simple numeric/short passwords and custom usernames."""
        from accounts.forms import UserRegistrationForm
        form_data = {
            'username': 'testuser123',
            'email': 'newuser@example.com',
            'password1': '123',
            'password2': '123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors.as_text())

    def test_register_view_redirects_to_login(self):
        """Test successful registration redirects user to login page."""
        from django.urls import reverse
        response = self.client.post(reverse('register'), {
            'username': 'newuser99',
            'email': 'newuser99@example.com',
            'password1': '123',
            'password2': '123',
        })
    def test_duplicate_email_disallowed(self):
        """Test registration rejects an email address that is already registered."""
        from accounts.forms import UserRegistrationForm
        form_data = {
            'username': 'unique_user',
            'email': 'test@example.com', # existing email from setUp
            'password1': '123',
            'password2': '123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertEqual(form.errors['email'], ['A user with that email address already exists.'])

    def test_duplicate_username_allowed(self):
        """Test registration allows two users to register with the exact same username."""
        from accounts.forms import UserRegistrationForm
        from django.contrib.auth import authenticate
        
        # Register User 1 with username 'same_user'
        form1 = UserRegistrationForm(data={
            'username': 'same_user',
            'email': 'user1@example.com',
            'password1': 'pass123',
            'password2': 'pass123',
        })
        self.assertTrue(form1.is_valid(), msg=form1.errors.as_text())
        user1 = form1.save()

        # Register User 2 with the SAME username 'same_user' but different email
        form2 = UserRegistrationForm(data={
            'username': 'same_user',
            'email': 'user2@example.com',
            'password1': 'pass456',
            'password2': 'pass456',
        })
        self.assertTrue(form2.is_valid(), msg=form2.errors.as_text())
        user2 = form2.save()

        # Verify both users were created successfully
        self.assertNotEqual(user1.pk, user2.pk)
        
        # Verify both users can authenticate using their email addresses
        auth_u1 = authenticate(username='user1@example.com', password='pass123')
        auth_u2 = authenticate(username='user2@example.com', password='pass456')
        self.assertEqual(auth_u1, user1)
        self.assertEqual(auth_u2, user2)




