from django.test import TestCase
from django.urls import reverse
from automation_app.models import User


class LoginTestCase(TestCase):
    def setUp(self):
        # Create a user with username 'admin' and password 'admin'
        self.user = User.objects.create_user(username='admin', password='admin')

    def test_login(self):
        # Test cases
        test_cases = [
            {'username': '', 'password': '', 'expected': False},
            {'username': '', 'password': 'admin', 'expected': False},
            {'username': 'admin', 'password': '', 'expected': False},
            {'username': 'Admin', 'password': 'Admin', 'expected': False},
            {'username': 'Admin', 'password': 'admin', 'expected': False},
            {'username': 'admin', 'password': 'Admin', 'expected': False},
            {'username': 'admin', 'password': 'admin', 'expected': True},
        ]

        for case in test_cases:
            with self.subTest(case=case):
                # Prepare login data
                login_data = {
                    'username': case['username'] if case['username'] is not None else '',
                    'password': case['password'] if case['password'] is not None else ''
                }
                # Perform login
                response = self.client.post(reverse('login'), login_data)
                # Check login status
                is_logged_in = response.wsgi_request.user.is_authenticated

                # Debugging output
                if is_logged_in != case['expected']:
                    print(f"Failed case: {case}")
                    print(f"Response status code: {response.status_code}")
                    print(f"Response content: {response.content.decode()}")

                self.assertEqual(is_logged_in, case['expected'])

# To run the tests, use the command: python manage.py test


from django.test import TestCase
from django.urls import reverse
from automation_app.models import User, AutomationType, Automation, UserAutomation


class AddAutomationTestCase(TestCase):
    def setUp(self):
        # Create a user with role 'order_processing'
        self.user = User.objects.create_user(username='order_user', password='password', role='order_processing')

        # Create an automation type 'Orders'
        self.automation_type_orders = AutomationType.objects.create(name='Orders')

        # Create an automation 'Orders_Depo' of type 'Orders'
        self.automation_orders_depo = Automation.objects.create(name='Orders_Depo',
                                                                description='Process orders from Depo',
                                                                automation_type=self.automation_type_orders,
                                                                created_by=self.user)

        # Create an automation type 'Invoices'
        self.automation_type_invoices = AutomationType.objects.create(name='Invoices')

        # Create an automation 'Invoices_Legrand' of type 'Invoices'
        self.automation_invoices_legrand = Automation.objects.create(name='Invoices_Legrand',
                                                                     description='Process invoices from Legrand',
                                                                     automation_type=self.automation_type_invoices,
                                                                     created_by=self.user)

    def test_add_order_automation(self):
        # Log in as the created user
        self.client.login(username='order_user', password='password')

        # Post request to add order automation
        response = self.client.post(reverse('add_automation'), {
            'automation_id': self.automation_orders_depo.id
        })

        # Check if the order automation was added to the user's list
        self.assertTrue(UserAutomation.objects.filter(user=self.user, automation=self.automation_orders_depo).exists())

        # Check if the response is a redirect to the home page
        self.assertRedirects(response, reverse('home'))

    def test_cannot_add_invoice_automation(self):
        # Log in as the created user
        self.client.login(username='order_user', password='password')

        # Post request to add invoice automation
        response = self.client.post(reverse('add_automation'), {
            'automation_id': self.automation_invoices_legrand.id
        })

        # Check if the invoice automation was not added to the user's list
        self.assertFalse(
            UserAutomation.objects.filter(user=self.user, automation=self.automation_invoices_legrand).exists())

        # Check if the response contains the appropriate error message
        self.assertContains(response, 'You do not have rights to add this automation.')


from django.test import TestCase
from django.urls import reverse
from automation_app.models import User, AutomationType, Automation, UserAutomation


class DeleteAutomationTestCase(TestCase):
    def setUp(self):
        # Create a user with role 'order_processing'
        self.user = User.objects.create_user(username='order_user', password='password', role='order_processing')

        # Create an automation type 'Orders'
        self.automation_type_orders = AutomationType.objects.create(name='Orders')

        # Create an automation 'Orders_Depo' of type 'Orders'
        self.automation_orders_depo = Automation.objects.create(name='Orders_Depo',
                                                                description='Process orders from Depo',
                                                                automation_type=self.automation_type_orders,
                                                                created_by=self.user)

        # Add the automation to the user's list
        self.user_automation = UserAutomation.objects.create(user=self.user, automation=self.automation_orders_depo)

    def test_delete_automation(self):
        # Log in as the created user
        self.client.login(username='order_user', password='password')

        # Send a POST request to delete the automation
        response = self.client.post(reverse('delete_automation', args=[self.automation_orders_depo.id]))

        # Check if the automation was deleted from the user's list
        self.assertFalse(UserAutomation.objects.filter(user=self.user, automation=self.automation_orders_depo).exists())

        # Check if the response is a redirect to the home page
        self.assertRedirects(response, reverse('home'))



from django.test import TestCase
from django.urls import reverse
from automation_app.models import User

class UpdateProfileTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testUser', password='password', first_name='Test', last_name='User', email='testuser@example.com')

    def test_update_profile(self):
        # Log in as the created user
        self.client.login(username='testUser', password='password')

        # Send a POST request to update the profile
        response = self.client.post(reverse('profile'), {
            'username': 'changedUser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'changeduser@example.com'
        })

        # Check if the user was redirected to the home page
        self.assertRedirects(response, reverse('home'))

        # Fetch the updated user data
        self.user.refresh_from_db()

        # Check if the username was updated
        self.assertEqual(self.user.username, 'changedUser')

        # Check if the home page displays the updated username
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Welcome changedUser')





from django.test import TestCase
from django.urls import reverse
from automation_app.models import User

class ChangePasswordTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(username='testUser', password='password')

    def test_change_password(self):
        # Log in as the created user
        self.client.login(username='testUser', password='password')

        # Send a POST request to change the password
        response = self.client.post(reverse('change_password'), {
            'old_password': 'password',
            'new_password1': 'NewPassword123!',
            'new_password2': 'NewPassword123!'
        })

        # Debugging output
        if response.status_code != 302:
            print(f"Form errors: {response.context['password_form'].errors}")

        # Check if the user was redirected to the home page
        self.assertRedirects(response, reverse('home'))

        # Log out the user
        self.client.logout()

        # Attempt to log in with the new password
        login_response = self.client.post(reverse('login'), {
            'username': 'testUser',
            'password': 'NewPassword123!'
        })

        # Check if the login was successful with the new password
        is_logged_in = login_response.wsgi_request.user.is_authenticated
        self.assertTrue(is_logged_in)



