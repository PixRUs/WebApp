from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from pixrus.DatabaseDrivers.models.UserProfile import Buyer, Seller
from pixrus.DatabaseDrivers.models.Products import Subscription
from pixrus.DatabaseDrivers.service.subscriber_manager import create_new_subscription, end_current_subscription
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class SubscriptionTestCase(TestCase):

    def setUp(self):
        # Create Buyer and Seller instances
        self.buyer = Buyer.objects.create(user=User.objects.create(username="test_buyer"))
        self.seller = Seller.objects.create(user=User.objects.create(username="test_seller"))

        # Create an active subscription
        self.active_subscription = Subscription.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            subscribed_at=timezone.now() - timedelta(days=5),
            subscribed_until=timezone.now() + timedelta(days=5)
        )

    def test_create_new_subscription(self):
        """Test that a new subscription is created with valid data."""
        start_time = timezone.now()
        end_time = start_time + timedelta(days=30)
        subscription = create_new_subscription(start_time, end_time, self.buyer, self.seller, meta_data={'plan': 'premium'})

        self.assertIsNotNone(subscription.id)
        self.assertEqual(subscription.buyer, self.buyer)
        self.assertEqual(subscription.seller, self.seller)
        self.assertEqual(subscription.meta_data, {'plan': 'premium'})
        self.assertGreater(subscription.subscribed_until, start_time)

    def test_create_subscription_with_invalid_dates(self):
        """Test that an invalid date range raises a ValueError."""
        start_time = timezone.now()
        end_time = start_time - timedelta(days=1)  # Invalid: end before start

        with self.assertRaises(ValueError):
            create_new_subscription(start_time, end_time, self.buyer, self.seller)

    def test_end_active_subscription(self):
        """Test that an active subscription is ended successfully."""
        result = end_current_subscription(buyer=self.buyer, seller=self.seller)
        self.assertTrue(result)

        # Refresh from the database to check updated value
        self.active_subscription.refresh_from_db()
        self.assertLessEqual(self.active_subscription.subscribed_until, timezone.now())

    def test_end_expired_subscription(self):
        """Test that trying to end an already expired subscription does nothing."""
        # Create an expired subscription
        expired_subscription = Subscription.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            subscribed_at=timezone.now() - timedelta(days=30),
            subscribed_until=timezone.now() - timedelta(days=5)
        )

        # Attempt to end the expired subscription
        result = end_current_subscription(buyer=self.buyer, seller=self.seller)
        self.assertFalse(result)

    def test_end_subscription_no_subscription(self):
        """Test that trying to end a subscription when none exists for the buyer/seller returns False."""
        # Create a new buyer and seller with no subscriptions
        new_buyer = Buyer.objects.create(user=User.objects.create(username="new_buyer"))
        new_seller = Seller.objects.create(user=User.objects.create(username="new_seller"))

        result = end_current_subscription(buyer=new_buyer, seller=new_seller)
        self.assertFalse(result)

    def test_multiple_active_subscriptions(self):
        """Test that the most recent active subscription is ended when multiple active subscriptions exist."""
        # Create an additional active subscription
        additional_active_subscription = Subscription.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            subscribed_at=timezone.now() - timedelta(days=1),
            subscribed_until=timezone.now() + timedelta(days=20)
        )

        result = end_current_subscription(buyer=self.buyer, seller=self.seller)
        self.assertTrue(result)

        # Verify that only the most recent active subscription was ended
        additional_active_subscription.refresh_from_db()
        self.assertLessEqual(additional_active_subscription.subscribed_until, timezone.now())
        
        # Check the initial active subscription is still active
        self.active_subscription.refresh_from_db()
        self.assertGreater(self.active_subscription.subscribed_until, timezone.now())

    # Error handling tests

    def test_end_subscription_with_invalid_buyer(self):
        """Test that passing an invalid buyer raises an error."""
        with self.assertRaises(TypeError):
            end_current_subscription(buyer="invalid_buyer", seller=self.seller)

    def test_end_subscription_with_invalid_seller(self):
        """Test that passing an invalid seller raises an error."""
        with self.assertRaises(TypeError):
            end_current_subscription(buyer=self.buyer, seller="invalid_seller")

    def test_end_subscription_with_deleted_buyer(self):
        """Test behavior when trying to end a subscription for a buyer who has been deleted."""
        # Delete the buyer
        self.buyer.delete()

        # Attempt to end the subscription (should return False)
        result = end_current_subscription(buyer=self.buyer, seller=self.seller)
        self.assertFalse(result)

    def test_end_subscription_with_deleted_seller(self):
        """Test behavior when trying to end a subscription for a seller who has been deleted."""
        # Delete the seller
        self.seller.delete()

        # Attempt to end the subscription (should return False)
        result = end_current_subscription(buyer=self.buyer, seller=self.seller)
        self.assertFalse(result)

    def test_create_subscription_with_invalid_buyer_or_seller(self):
        """Test that creating a subscription with an invalid buyer or seller raises an error."""
        start_time = timezone.now()
        end_time = start_time + timedelta(days=30)

        with self.assertRaises(ValidationError):
            create_new_subscription(start_time, end_time, "invalid_buyer", self.seller)

        with self.assertRaises(ValidationError):
            create_new_subscription(start_time, end_time, self.buyer, "invalid_seller")
