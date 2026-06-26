from django.test import TestCase, Client
from django.urls import reverse
from .models import User


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(email='user@test.com', password='StrongPass123!',
              role='SmallBusiness', first_name='Test', last_name='User'):
    return User.objects.create_user(
        username=email, email=email, password=password,
        role=role, first_name=first_name, last_name=last_name,
    )


REGISTER_URL = reverse('accounts:register')
LOGIN_URL    = reverse('accounts:login')
LOGOUT_URL   = reverse('accounts:logout')
PROFILE_URL  = reverse('accounts:profile')


# ===========================================================================
# 1. REGISTRATION TESTS
# ===========================================================================

class RegistrationTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.valid_data = {
            'first_name': 'John',
            'last_name':  'Doe',
            'email':      'john@example.com',
            'phone':      '0123456789',
            'role':       'SmallBusiness',
            'password1':  'StrongPass123!',
            'password2':  'StrongPass123!',
        }

    # --- GET ----------------------------------------------------------------

    def test_register_page_loads(self):
        """Register page returns 200 for anonymous users."""
        res = self.client.get(REGISTER_URL)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'accounts/register.html')

    def test_register_page_redirects_when_logged_in(self):
        """Authenticated users are redirected away from the register page."""
        make_user()
        self.client.login(username='user@test.com', password='StrongPass123!')
        res = self.client.get(REGISTER_URL)
        self.assertRedirects(res, PROFILE_URL)

    # --- POST: success ------------------------------------------------------

    def test_register_small_business_success(self):
        """Valid Small Business registration creates user and redirects to profile."""
        res = self.client.post(REGISTER_URL, self.valid_data)
        self.assertRedirects(res, PROFILE_URL)
        self.assertTrue(User.objects.filter(email='john@example.com').exists())

    def test_register_enterprise_buyer_success(self):
        """Valid Enterprise Buyer registration creates user with correct role."""
        data = {**self.valid_data, 'email': 'enterprise@example.com', 'role': 'EnterpriseBuyer'}
        self.client.post(REGISTER_URL, data)
        user = User.objects.get(email='enterprise@example.com')
        self.assertEqual(user.role, 'EnterpriseBuyer')

    def test_register_password_is_hashed(self):
        """Password must never be stored as plain text."""
        self.client.post(REGISTER_URL, self.valid_data)
        user = User.objects.get(email='john@example.com')
        self.assertNotEqual(user.password, 'StrongPass123!')
        self.assertTrue(user.password.startswith('pbkdf2_') or
                        user.password.startswith('bcrypt') or
                        user.password.startswith('argon2'))

    def test_register_logs_user_in_automatically(self):
        """User is authenticated immediately after registration."""
        self.client.post(REGISTER_URL, self.valid_data)
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, 200)   # not redirected to login

    def test_register_without_phone_succeeds(self):
        """Phone is optional — registration must succeed without it."""
        data = {**self.valid_data, 'phone': ''}
        res = self.client.post(REGISTER_URL, data)
        self.assertRedirects(res, PROFILE_URL)

    # --- POST: failures -----------------------------------------------------

    def test_register_duplicate_email_fails(self):
        """Duplicate email must be rejected with a form error."""
        make_user(email='john@example.com')
        res = self.client.post(REGISTER_URL, self.valid_data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(email='john@example.com').count() > 1)

    def test_register_mismatched_passwords_fails(self):
        """Passwords that don't match must be rejected."""
        data = {**self.valid_data, 'password2': 'DifferentPass999!'}
        res = self.client.post(REGISTER_URL, data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(email='john@example.com').exists())

    def test_register_weak_password_fails(self):
        """Common/short passwords must be rejected by validators."""
        data = {**self.valid_data, 'password1': '12345678', 'password2': '12345678'}
        res = self.client.post(REGISTER_URL, data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(email='john@example.com').exists())

    def test_register_missing_first_name_fails(self):
        """First name is required."""
        data = {**self.valid_data, 'first_name': ''}
        res = self.client.post(REGISTER_URL, data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(email='john@example.com').exists())

    def test_register_invalid_email_format_fails(self):
        """Malformed email must be rejected."""
        data = {**self.valid_data, 'email': 'not-an-email'}
        res = self.client.post(REGISTER_URL, data)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(email='not-an-email').exists())


# ===========================================================================
# 2. LOGIN TESTS
# ===========================================================================

class LoginTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user(email='login@example.com', password='StrongPass123!')

    # --- GET ----------------------------------------------------------------

    def test_login_page_loads(self):
        """Login page returns 200 for anonymous users."""
        res = self.client.get(LOGIN_URL)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'accounts/login.html')

    def test_login_page_redirects_when_logged_in(self):
        """Authenticated users are redirected away from the login page."""
        self.client.login(username='login@example.com', password='StrongPass123!')
        res = self.client.get(LOGIN_URL)
        self.assertRedirects(res, PROFILE_URL)

    # --- POST: success ------------------------------------------------------

    def test_login_valid_credentials_redirects_to_profile(self):
        """Correct email + password redirects to /accounts/me/."""
        res = self.client.post(LOGIN_URL, {
            'username': 'login@example.com',
            'password': 'StrongPass123!',
        })
        self.assertRedirects(res, PROFILE_URL)

    def test_login_creates_session(self):
        """After login, the user is authenticated in subsequent requests."""
        self.client.post(LOGIN_URL, {
            'username': 'login@example.com',
            'password': 'StrongPass123!',
        })
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, 200)

    # --- POST: failures -----------------------------------------------------

    def test_login_wrong_password_fails(self):
        """Wrong password must return 200 with form errors, not redirect."""
        res = self.client.post(LOGIN_URL, {
            'username': 'login@example.com',
            'password': 'WrongPassword!',
        })
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.wsgi_request.user.is_authenticated)

    def test_login_wrong_email_fails(self):
        """Non-existent email must be rejected."""
        res = self.client.post(LOGIN_URL, {
            'username': 'ghost@example.com',
            'password': 'StrongPass123!',
        })
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.wsgi_request.user.is_authenticated)

    def test_login_inactive_user_fails(self):
        """Deactivated accounts must not be able to log in."""
        self.user.is_active = False
        self.user.save()
        res = self.client.post(LOGIN_URL, {
            'username': 'login@example.com',
            'password': 'StrongPass123!',
        })
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.wsgi_request.user.is_authenticated)

    def test_login_empty_fields_fails(self):
        """Empty form submission must not authenticate anyone."""
        res = self.client.post(LOGIN_URL, {'username': '', 'password': ''})
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.wsgi_request.user.is_authenticated)


# ===========================================================================
# 3. LOGOUT TESTS
# ===========================================================================

class LogoutTests(TestCase):

    def setUp(self):
        self.client = Client()
        make_user(email='logout@example.com', password='StrongPass123!')
        self.client.login(username='logout@example.com', password='StrongPass123!')

    def test_logout_redirects_to_login(self):
        """Logout must redirect to the login page."""
        res = self.client.get(LOGOUT_URL)
        self.assertRedirects(res, LOGIN_URL)

    def test_logout_destroys_session(self):
        """After logout, the profile page must redirect to login."""
        self.client.get(LOGOUT_URL)
        res = self.client.get(PROFILE_URL)
        self.assertRedirects(res, f'{LOGIN_URL}?next={PROFILE_URL}')


# ===========================================================================
# 4. PROFILE (ME) TESTS
# ===========================================================================

class ProfileTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = make_user(email='profile@example.com', password='StrongPass123!',
                              role='SmallBusiness', first_name='Jane', last_name='Smith')

    def test_profile_requires_authentication(self):
        """Unauthenticated request must redirect to login with next param."""
        res = self.client.get(PROFILE_URL)
        self.assertRedirects(res, f'{LOGIN_URL}?next={PROFILE_URL}')

    def test_profile_loads_for_authenticated_user(self):
        """Authenticated user sees their profile page (200)."""
        self.client.login(username='profile@example.com', password='StrongPass123!')
        res = self.client.get(PROFILE_URL)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed(res, 'accounts/profile.html')

    def test_profile_shows_user_name(self):
        """Profile page must contain the user's first and last name."""
        self.client.login(username='profile@example.com', password='StrongPass123!')
        res = self.client.get(PROFILE_URL)
        self.assertContains(res, 'Jane')
        self.assertContains(res, 'Smith')

    def test_profile_shows_correct_role_small_business(self):
        """Profile page must display the Small Business role label."""
        self.client.login(username='profile@example.com', password='StrongPass123!')
        res = self.client.get(PROFILE_URL)
        self.assertContains(res, 'Small Business')

    def test_profile_shows_correct_role_enterprise(self):
        """Profile page must display the Enterprise Buyer role label."""
        user = make_user(email='ent@example.com', password='StrongPass123!',
                         role='EnterpriseBuyer')
        self.client.login(username='ent@example.com', password='StrongPass123!')
        res = self.client.get(PROFILE_URL)
        self.assertContains(res, 'Enterprise Buyer')


# ===========================================================================
# 5. RBAC DECORATOR TESTS
# ===========================================================================

class RBACDecoratorTests(TestCase):
    """
    Tests for accounts.decorators.role_required.
    Uses a minimal inline view registered only during the test.
    """

    def setUp(self):
        self.client = Client()
        self.small_biz  = make_user('sb@test.com',  'StrongPass123!', 'SmallBusiness')
        self.enterprise  = make_user('ent@test.com', 'StrongPass123!', 'EnterpriseBuyer')
        self.admin_user  = make_user('adm@test.com', 'StrongPass123!', 'Admin')

    def _get_as(self, email, password, url):
        self.client.login(username=email, password=password)
        return self.client.get(url)

    def test_role_required_blocks_unauthenticated(self):
        """role_required must redirect anonymous users to login."""
        from accounts.decorators import role_required
        from django.http import HttpResponse
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/')
        request.user = type('AnonUser', (), {'is_authenticated': False})()

        @role_required('Admin')
        def dummy_view(req):
            return HttpResponse('ok')

        res = dummy_view(request)
        self.assertEqual(res.status_code, 302)
        self.assertIn('/accounts/login/', res['Location'])

    def test_role_required_allows_correct_role(self):
        """role_required must allow through a user whose role matches."""
        from accounts.decorators import role_required
        from django.http import HttpResponse
        from django.test import RequestFactory

        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.admin_user

        @role_required('Admin')
        def dummy_view(req):
            return HttpResponse('ok')

        res = dummy_view(request)
        self.assertEqual(res.status_code, 200)

    def test_role_required_blocks_wrong_role(self):
        """role_required must redirect a user whose role doesn't match."""
        from accounts.decorators import role_required
        from django.http import HttpResponse
        from django.test import RequestFactory
        from django.contrib.messages.storage.fallback import FallbackStorage
        from django.contrib.sessions.backends.db import SessionStore

        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.small_biz

        # Attach session + message storage so the decorator's messages.error works
        request.session = SessionStore()
        request.session.create()
        messages = FallbackStorage(request)
        request._messages = messages

        @role_required('Admin')
        def dummy_view(req):
            return HttpResponse('ok')

        res = dummy_view(request)
        self.assertEqual(res.status_code, 302)

    def test_superuser_bypasses_role_check(self):
        """A superuser must pass any role_required gate regardless of their role field."""
        from accounts.decorators import role_required
        from django.http import HttpResponse
        from django.test import RequestFactory

        superuser = User.objects.create_superuser(
            username='super@test.com', email='super@test.com', password='Super123!'
        )
        factory = RequestFactory()
        request = factory.get('/')
        request.user = superuser

        @role_required('Admin')
        def dummy_view(req):
            return HttpResponse('ok')

        res = dummy_view(request)
        self.assertEqual(res.status_code, 200)


# ===========================================================================
# 6. USER MODEL TESTS
# ===========================================================================

class UserModelTests(TestCase):

    def test_default_role_is_small_business(self):
        """New users created without a role must default to SmallBusiness."""
        user = User.objects.create_user(
            username='def@test.com', email='def@test.com', password='Pass123!'
        )
        self.assertEqual(user.role, 'SmallBusiness')

    def test_email_is_unique(self):
        """Creating two users with the same email must raise an IntegrityError."""
        from django.db import IntegrityError
        make_user(email='unique@test.com')
        with self.assertRaises(Exception):   # IntegrityError or ValidationError
            make_user(email='unique@test.com')

    def test_str_returns_email(self):
        """User.__str__ must return the email address."""
        user = make_user(email='str@test.com')
        self.assertEqual(str(user), 'str@test.com')

    def test_valid_roles_accepted(self):
        """All three defined roles must be accepted by the model."""
        for role in ('Admin', 'SmallBusiness', 'EnterpriseBuyer'):
            user = make_user(email=f'{role}@test.com', role=role)
            self.assertEqual(user.role, role)
