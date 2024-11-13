from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from pixrus.database_service.models.UserProfile import Buyer, Seller, UserSession


class UserProfileTests(TestCase):

    def setUp(self):
        self.user_auth_data = {
            'email': 'testuser@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'google_id': 'test_google_id',
        }
        self.user_meta_data = {
            'username': 'testuser'
        }

    def test_register_buyer(self):
        # Register a new buyer
        user_profile, created = Buyer.register_or_update_user(
            user_auth_data=self.user_auth_data,
            user_meta_data=self.user_meta_data,
            type_of_user='buyer'
        )
        self.assertTrue(created)
        self.assertIsInstance(user_profile, Buyer)
        self.assertEqual(user_profile.user.email, 'testuser@example.com')
        self.assertEqual(user_profile.user.first_name, 'Test')
        self.assertEqual(user_profile.user.last_name, 'User')
        self.assertEqual(user_profile.user.username, 'testuser')
        self.assertEqual(user_profile.google_id, 'test_google_id')
        self.assertEqual(user_profile.meta_data, self.user_meta_data)

    def test_register_seller(self):
        # Register a new seller
        user_profile, created = Seller.register_or_update_user(
            user_auth_data=self.user_auth_data,
            user_meta_data=self.user_meta_data,
            type_of_user='seller'
        )
        self.assertTrue(created)
        self.assertIsInstance(user_profile, Seller)
        self.assertEqual(user_profile.user.email, 'testuser@example.com')
        self.assertEqual(user_profile.user.first_name, 'Test')
        self.assertEqual(user_profile.user.last_name, 'User')
        self.assertEqual(user_profile.user.username, 'testuser')
        self.assertEqual(user_profile.google_id, 'test_google_id')
        self.assertEqual(user_profile.meta_data, self.user_meta_data)

    def test_update_user_profile(self):
        # Register a new buyer
        user_profile, created = Buyer.register_or_update_user(
            user_auth_data=self.user_auth_data,
            user_meta_data=self.user_meta_data,
            type_of_user='buyer'
        )

        # Update the user's first name and last name
        updated_auth_data = self.user_auth_data.copy()
        updated_auth_data['first_name'] = 'Updated'
        updated_auth_data['last_name'] = 'Name'
        user_profile, created = Buyer.register_or_update_user(
            user_auth_data=updated_auth_data,
            user_meta_data=self.user_meta_data,
            type_of_user='buyer'
        )
        self.assertFalse(created)
        self.assertEqual(user_profile.user.first_name, 'Updated')
        self.assertEqual(user_profile.user.last_name, 'Name')

    def test_user_session_login(self):
        # Register a new buyer and log in
        user_profile, _ = Buyer.register_or_update_user(
            user_auth_data=self.user_auth_data,
            user_meta_data=self.user_meta_data,
            type_of_user='buyer'
        )
        session_id = user_profile.update_user_session_login(
            google_id='new_google_id',
            user_meta_data=self.user_meta_data
        )
        
        # Check session attributes
        session = UserSession.objects.get(id=session_id)
        self.assertEqual(session.user, user_profile.user)
        self.assertTrue(session.is_online)
        self.assertAlmostEqual(session.last_logged_in, timezone.now(), delta=timezone.timedelta(seconds=5))

    def test_user_session_logout(self):
        # Register a new buyer, log in, and log out
        user_profile, _ = Buyer.register_or_update_user(
            user_auth_data=self.user_auth_data,
            user_meta_data=self.user_meta_data,
            type_of_user='buyer'
        )
        user_profile.update_user_session_login(
            google_id='new_google_id',
            user_meta_data=self.user_meta_data
        )
        
        session_id = user_profile.update_user_session_logout()
        
        # Check session attributes after logout
        session = UserSession.objects.get(id=session_id)
        self.assertFalse(session.is_online)

    def test_get_user_profile_by_email(self):
        # Register a new buyer and retrieve by email
        Buyer.register_or_update_user(
            user_auth_data=self.user_auth_data,
            user_meta_data=self.user_meta_data,
            type_of_user='buyer'
        )
        user_profile = Buyer.get_by_email('testuser@example.com')
        self.assertEqual(user_profile.user.email, 'testuser@example.com')

    def test_get_user_creation_date(self):
        # Register a new buyer and retrieve creation date
        user_profile, _ = Buyer.register_or_update_user(
            user_auth_data=self.user_auth_data,
            user_meta_data=self.user_meta_data,
            type_of_user='buyer'
        )
        creation_date = Buyer.get_user_creation_date(email='testuser@example.com')
        self.assertEqual(creation_date, user_profile.created_at)
