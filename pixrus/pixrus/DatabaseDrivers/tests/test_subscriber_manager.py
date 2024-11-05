from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from pixrus.DatabaseDrivers.models.UserProfile import Buyer, Seller
from pixrus.DatabaseDrivers.models.Products import Subscription
from pixrus.DatabaseDrivers.service.subscriber_manager import create_new_subscription, end_current_subscription
from django.contrib.auth.models import User


class SubscriptionManagerTestCase(TestCase):

    def setUp(self):
        # Create a Buyer and Seller instance for testing
        self.buyer = Buyer.objects.create(user=User.objects.create(username="test_buyer"))
        self.seller = Seller.objects.create(user=User.objects.create(username="test_seller"))

    # Tests for create_new_subscription function
    def test_create_new_subscription_success(self):
        """Test creating a subscription with valid start and end times."""
        start_time = timezone.now()
        end_time = start_time + timedelta(days=30)
        meta_data = {"plan": "premium"}

        subscription = create_new_subscription(
            start_time=start_time,
            end_time=end_time,
            buyer=self.buyer,
            seller=self.seller,
            meta_data=meta_data
        )

        self.assertIsNotNone(subscription.id)
        self.assertEqual(subscription.buyer, self.buyer)
        self.assertEqual(subscription.seller, self.seller)
        self.assertEqual(subscription.meta_data, meta_data)
        self.assertEqual(subscription.subscribed_at, start_time)
        self.assertEqual(subscription.subscribed_until, end_time)

    def test_create_new_subscription_invalid_dates(self):
        """Test that an invalid date range raises a ValueError."""
        start_time = timezone.now()
        end_time = start_time - timedelta(days=1)  # End time before start time

        with self.assertRaises(ValueError):
            create_new_subscription(
                start_time=start_time,
                end_time=end_time,
                buyer=self.buyer,
                seller=self.seller,
                meta_data={"plan": "premium"}
            )

    # Tests for end_current_subscription function
    def test_end_current_subscription_success(self):
        """Test that an active subscription is ended successfully."""
        start_time = timezone.now() - timedelta(days=10)
        end_time = timezone.now() + timedelta(days=10)
        
        # Create an active subscription
        subscription = create_new_subscription(
            start_time=start_time,
            end_time=end_time,
            buyer=self.buyer,
            seller=self.seller,
            meta_data={"plan": "premium"}
        )
        
        result = end_current_subscription(buyer=self.buyer, seller=self.seller)
        self.assertTrue(result)

        # Refresh from the database to check updated subscribed_until value
        subscription.refresh_from_db()
        self.assertLessEqual(subscription.subscribed_until, timezone.now())

    def test_end_current_subscription_no_active_subscription(self):
        """Test that ending a subscription fails if no active subscription exists."""
        start_time = timezone.now() - timedelta(days=30)
        end_time = timezone.now() - timedelta(days=5)
        
        # Create an expired subscription
        Subscription.objects.create(
            buyer=self.buyer,
            seller=self.seller,
            subscribed_at=start_time,
            subscribed_until=end_time,
            meta_data={"plan": "premium"}
        )
        
        # Attempt to end an expired subscription
        result = end_current_subscription(buyer=self.buyer, seller=self.seller)
        self.assertFalse(result)

    def test_end_current_subscription_no_subscription(self):
        """Test that ending a subscription returns False if no subscription exists at all."""
        # No subscriptions created yet
        result = end_current_subscription(buyer=self.buyer, seller=self.seller)
        self.assertFalse(result)

    def test_end_multiple_active_subscriptions(self):
        """Test that the most recent active subscription is ended when multiple active subscriptions exist."""
        # Create two active subscriptions
        create_new_subscription(
            start_time=timezone.now() - timedelta(days=20),
            end_time=timezone.now() + timedelta(days=5),
            buyer=self.buyer,
            seller=self.seller,
            meta_data={"plan": "standard"}
        )
        
        latest_subscription = create_new_subscription(
            start_time=timezone.now() - timedelta(days=5),
            end_time=timezone.now() + timedelta(days=10),
            buyer=self.buyer,
            seller=self.seller,
            meta_data={"plan": "premium"}
        )

        result = end_current_subscription(buyer=self.buyer, seller=self.seller)
        self.assertTrue(result)

        # Check that only the latest active subscription was ended
        latest_subscription.refresh_from_db()
        self.assertLessEqual(latest_subscription.subscribed_until, timezone.now())
        
        # The earlier subscription should still be active if it ends after now
        earlier_subscription = Subscription.objects.filter(
            buyer=self.buyer,
            seller=self.seller
        ).earliest('subscribed_at')
        self.assertGreater(earlier_subscription.subscribed_until, timezone.now())
