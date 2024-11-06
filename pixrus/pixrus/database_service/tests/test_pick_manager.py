# pixrus/database_service/tests.py

import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError
from pixrus.database_service.models.UserProfile import (
    Buyer,
    Seller,
    UserSession,
)
from pixrus.database_service.models.Products import (
    Subscription,
    ActivePick,
    HistoricalPick,
    VendorApiRequest
)


class UserProfileTests(TestCase):
    def setUp(self):
        # Create Users
        self.user1 = User.objects.create_user(
            username='buyer1',
            email='buyer1@example.com',
            first_name='Buyer',
            last_name='One',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='seller1',
            email='seller1@example.com',
            first_name='Seller',
            last_name='One',
            password='password123'
        )
        
        # Create Buyer and Seller profiles
        self.buyer1 = Buyer.objects.create(user=self.user1, meta_data={'info': 'buyer1 meta'})
        self.seller1 = Seller.objects.create(user=self.user2, meta_data={'info': 'seller1 meta'})

    def test_create_buyer(self):
        self.assertEqual(self.buyer1.user.email, 'buyer1@example.com')
        self.assertEqual(self.buyer1.meta_data, {'info': 'buyer1 meta'})
    
    def test_create_seller(self):
        self.assertEqual(self.seller1.user.email, 'seller1@example.com')
        self.assertEqual(self.seller1.meta_data, {'info': 'seller1 meta'})
    
    def test_unique_google_id(self):
        # Attempt to create another Buyer with the same google_id
        with self.assertRaises(IntegrityError):
            Buyer.objects.create(
                user=self.user1,
                google_id='duplicate_google_id',
                meta_data={'info': 'duplicate'}
            )
    
    def test_user_session_creation(self):
        # Initially, no session exists
        with self.assertRaises(UserSession.DoesNotExist):
            UserSession.objects.get(user=self.user1)
        
        # Create session
        session = UserSession.objects.create(user=self.user1, is_online=True)
        self.assertTrue(session.is_online)
        self.assertIsNotNone(session.last_logged_in)
    
    def test_user_session_login(self):
        # Simulate user login
        self.buyer1.update_user_session_login(google_id='buyer1_google_id', user_meta_data={'info': 'updated meta'})
        session = UserSession.objects.get(user=self.user1)
        self.assertTrue(session.is_online)
        self.assertIsNotNone(session.last_logged_in)
    
    def test_user_session_logout(self):
        # Simulate user login and then logout
        self.buyer1.update_user_session_login(google_id='buyer1_google_id', user_meta_data={'info': 'updated meta'})
        session_id = self.buyer1.update_user_session_logout()
        session = UserSession.objects.get(id=session_id)
        self.assertFalse(session.is_online)
    
    def test_get_user_profile_by_email(self):
        retrieved_buyer = Buyer.get_by_email('buyer1@example.com')
        self.assertEqual(retrieved_buyer, self.buyer1)
    
    def test_get_user_creation_date(self):
        creation_date = Buyer.get_user_creation_date(email='buyer1@example.com')
        self.assertEqual(creation_date, self.buyer1.created_at)
    
    def test_get_user_name(self):
        user_name = Buyer.get_user_name(email='buyer1@example.com')
        self.assertEqual(user_name, 'Buyer O')  # 'O' is the first letter of last name 'One'


class ActivePickTests(TestCase):
    def setUp(self):
        # Create Users
        self.user_buyer = User.objects.create_user(
            username='buyer2',
            email='buyer2@example.com',
            first_name='Buyer',
            last_name='Two',
            password='password123'
        )
        self.user_seller = User.objects.create_user(
            username='seller2',
            email='seller2@example.com',
            first_name='Seller',
            last_name='Two',
            password='password123'
        )
        
        # Create Buyer and Seller profiles
        self.buyer2 = Buyer.objects.create(user=self.user_buyer, meta_data={'info': 'buyer2 meta'})
        self.seller2 = Seller.objects.create(user=self.user_seller, meta_data={'info': 'seller2 meta'})
        
        # Create ActivePick
        self.active_pick1 = ActivePick.objects.create(
            seller=self.seller2,
            meta_data={'pick_info': 'active_pick1'}
        )
        self.active_pick2 = ActivePick.objects.create(
            seller=self.seller2,
            meta_data={'pick_info': 'active_pick2'}
        )
        
    def test_give_buyer_access(self):
        # Grant access to buyer2 for active_pick1
        result = self.active_pick1.give_buyer_access(self.buyer2)
        self.assertTrue(result)
        self.assertTrue(self.active_pick1.has_access(self.buyer2))
        
        # Attempt to grant access again (should not duplicate)
        result = self.active_pick1.give_buyer_access(self.buyer2)
        self.assertTrue(result)
        self.assertEqual(self.active_pick1.buyers_with_access.count(), 1)
    
    def test_make_historical(self):
        # Grant access before making historical
        self.active_pick1.give_buyer_access(self.buyer2)
        
        # Make historical
        historical_pick = self.active_pick1.make_historical(event_result={'result': 'success'})
        
        # Check that HistoricalPick exists
        self.assertIsInstance(historical_pick, HistoricalPick)
        self.assertEqual(historical_pick.id, self.active_pick1.id)
        self.assertEqual(historical_pick.seller, self.active_pick1.seller)
        self.assertEqual(historical_pick.meta_data, self.active_pick1.meta_data)
        self.assertEqual(historical_pick.event_result, {'result': 'success'})
        
        # Check buyers_with_access transferred
        self.assertTrue(historical_pick.buyers_with_access.filter(id=self.buyer2.id).exists())
        
        # Check ActivePick deleted
        with self.assertRaises(ActivePick.DoesNotExist):
            ActivePick.objects.get(id=self.active_pick1.id)
    
    def test_get_active_picks_for_buyer(self):
        # Initially, buyer2 has no access
        active_picks = ActivePick.get_active_picks_for_buyer(self.buyer2)
        self.assertEqual(active_picks.count(), 0)
        
        # Grant access to active_pick1
        self.active_pick1.give_buyer_access(self.buyer2)
        active_picks = ActivePick.get_active_picks_for_buyer(self.buyer2)
        self.assertEqual(active_picks.count(), 1)
        self.assertIn(self.active_pick1, active_picks)
    
    def test_get_active_picks_for_seller(self):
        active_picks = ActivePick.get_active_picks_for_seller(self.seller2)
        self.assertEqual(active_picks.count(), 2)
        self.assertIn(self.active_pick1, active_picks)
        self.assertIn(self.active_pick2, active_picks)


class HistoricalPickTests(TestCase):
    def setUp(self):
        # Create Users
        self.user_buyer = User.objects.create_user(
            username='buyer3',
            email='buyer3@example.com',
            first_name='Buyer',
            last_name='Three',
            password='password123'
        )
        self.user_seller = User.objects.create_user(
            username='seller3',
            email='seller3@example.com',
            first_name='Seller',
            last_name='Three',
            password='password123'
        )
        
        # Create Buyer and Seller profiles
        self.buyer3 = Buyer.objects.create(user=self.user_buyer, meta_data={'info': 'buyer3 meta'})
        self.seller3 = Seller.objects.create(user=self.user_seller, meta_data={'info': 'seller3 meta'})
        
        # Create ActivePick and make it historical
        self.active_pick3 = ActivePick.objects.create(
            seller=self.seller3,
            meta_data={'pick_info': 'active_pick3'}
        )
        self.active_pick3.give_buyer_access(self.buyer3)
        self.historical_pick1 = self.active_pick3.make_historical(event_result={'result': 'completed'})
    
    def test_get_historical_picks_for_buyer(self):
        historical_picks = HistoricalPick.get_historical_picks_for_buyer(self.buyer3)
        self.assertEqual(historical_picks.count(), 1)
        self.assertIn(self.historical_pick1, historical_picks)
    
    def test_get_historical_picks_for_seller(self):
        historical_picks = HistoricalPick.get_historical_picks_for_seller(self.seller3)
        self.assertEqual(historical_picks.count(), 1)
        self.assertIn(self.historical_pick1, historical_picks)
    
    def test_historical_pick_attributes(self):
        self.assertEqual(self.historical_pick1.seller, self.seller3)
        self.assertEqual(self.historical_pick1.meta_data, {'pick_info': 'active_pick3'})
        self.assertEqual(self.historical_pick1.event_result, {'result': 'completed'})
        self.assertTrue(self.historical_pick1.has_access(self.buyer3))


class VendorApiRequestTests(TestCase):
    def test_create_vendor_api_request(self):
        # Create a VendorApiRequest
        api_request = VendorApiRequest.objects.create(
            vendor='VendorA',
            endpoint='/api/v1/resource/',
            response_status=200,
            response_data={'key': 'value'},
            delta=45
        )
        self.assertEqual(api_request.vendor, 'VendorA')
        self.assertEqual(api_request.endpoint, '/api/v1/resource/')
        self.assertEqual(api_request.response_status, 200)
        self.assertEqual(api_request.response_data, {'key': 'value'})
        self.assertEqual(api_request.delta, 45)
    
    def test_vendor_api_request_ordering(self):
        # Create multiple VendorApiRequests
        VendorApiRequest.objects.create(
            vendor='VendorB',
            endpoint='/api/v1/resource2/',
            response_status=404,
            response_data={'error': 'Not Found'},
            delta=30
        )
        VendorApiRequest.objects.create(
            vendor='VendorC',
            endpoint='/api/v1/resource3/',
            response_status=500,
            response_data={'error': 'Server Error'},
            delta=60
        )
        
        # Test ordering by request_time descending
        api_requests = VendorApiRequest.objects.all()
        self.assertEqual(api_requests[0].vendor, 'VendorC')
        self.assertEqual(api_requests[1].vendor, 'VendorB')
        self.assertEqual(api_requests[2].vendor, 'VendorA')


class SubscriptionTests(TestCase):
    def setUp(self):
        # Create Users
        self.user_buyer = User.objects.create_user(
            username='buyer4',
            email='buyer4@example.com',
            first_name='Buyer',
            last_name='Four',
            password='password123'
        )
        self.user_seller = User.objects.create_user(
            username='seller4',
            email='seller4@example.com',
            first_name='Seller',
            last_name='Four',
            password='password123'
        )
        
        # Create Buyer and Seller profiles
        self.buyer4 = Buyer.objects.create(user=self.user_buyer, meta_data={'info': 'buyer4 meta'})
        self.seller4 = Seller.objects.create(user=self.user_seller, meta_data={'info': 'seller4 meta'})
    
    def test_create_new_subscription(self):
        start_time = timezone.now()
        end_time = start_time + timezone.timedelta(days=30)
        
        subscription = Subscription.create_new_subscription(
            start_time=start_time,
            end_time=end_time,
            buyer=self.buyer4,
            seller=self.seller4,
            meta_data={'plan': 'premium'}
        )
        
        self.assertIsInstance(subscription, Subscription)
        self.assertEqual(subscription.buyer, self.buyer4)
        self.assertEqual(subscription.seller, self.seller4)
        self.assertEqual(subscription.subscribed_at, start_time)
        self.assertEqual(subscription.subscribed_until, end_time)
        self.assertEqual(subscription.meta_data, {'plan': 'premium'})
    
    def test_create_subscription_with_invalid_dates(self):
        start_time = timezone.now()
        end_time = start_time - timezone.timedelta(days=1)  # Invalid: end_time before start_time
        
        with self.assertRaises(ValueError):
            Subscription.create_new_subscription(
                start_time=start_time,
                end_time=end_time,
                buyer=self.buyer4,
                seller=self.seller4,
                meta_data={'plan': 'basic'}
            )
    
    def test_end_current_subscription(self):
        # Create an active subscription
        start_time = timezone.now() - timezone.timedelta(days=10)
        end_time = timezone.now() + timezone.timedelta(days=20)
        subscription = Subscription.create_new_subscription(
            start_time=start_time,
            end_time=end_time,
            buyer=self.buyer4,
            seller=self.seller4,
            meta_data={'plan': 'standard'}
        )
        
        # End the subscription
        result = Subscription.end_current_subscription(
            buyer=self.buyer4,
            seller=self.seller4
        )
        self.assertTrue(result)
        
        # Ensure the subscription is deleted
        with self.assertRaises(Subscription.DoesNotExist):
            Subscription.objects.get(id=subscription.id)
    
    def test_end_nonexistent_subscription(self):
        # Attempt to end a subscription that doesn't exist
        result = Subscription.end_current_subscription(
            buyer=self.buyer4,
            seller=self.seller4
        )
        self.assertFalse(result)
    
    def test_is_active(self):
        # Create an active subscription
        start_time = timezone.now() - timezone.timedelta(days=5)
        end_time = timezone.now() + timezone.timedelta(days=5)
        subscription = Subscription.create_new_subscription(
            start_time=start_time,
            end_time=end_time,
            buyer=self.buyer4,
            seller=self.seller4,
            meta_data={'plan': 'gold'}
        )
        self.assertTrue(subscription.is_active())
        
        # Create an expired subscription
        expired_subscription = Subscription.create_new_subscription(
            start_time=start_time - timezone.timedelta(days=20),
            end_time=start_time - timezone.timedelta(days=10),
            buyer=self.buyer4,
            seller=self.seller4,
            meta_data={'plan': 'silver'}
        )
        self.assertFalse(expired_subscription.is_active())
