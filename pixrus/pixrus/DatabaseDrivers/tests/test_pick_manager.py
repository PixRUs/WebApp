from django.test import TestCase
from datetime import datetime
from pixrus.DatabaseDrivers.models import Pick, Seller,Buyer
from django.contrib.auth.models import User

from pixrus.DatabaseDrivers.pick_manager import add_pick, get_all_pending_picks_for_buyer, get_all_processed_picks_for_seller, get_all_pending_picks_for_seller,get_all_processed_picks_for_buyer,give_buyer_access_to_pick

class PickModelTest(TestCase):
    
    def setUp(self):
        # Create a sample Seller instance for testing
        self.seller_user = User.objects.create_user(
            username="dummy seller",
            email="testuser@example.com",
            first_name="Test",
            last_name="Seller",
            password=""
        )
        self.seller = Seller.objects.create(
            user = self.seller_user, 
            meta_data = {"Favorite books": "BET365"},
        )
        self.user_buyer = User.objects.create_user(
            username="dummy Buyer",
            email="testBuyer@example.com",
            first_name="Test",
            last_name="Buyer",
            password=""
        )
        self.buyer = Buyer.objects.create(user=self.user_buyer, 
            meta_data= {"Picks won" : 4})
        self.meta_data = {
            "book" : "BET365", 
            "sport": "basketball", 
            "type_of_bet": "moneyline",
            "team1": "Lakers",
            "team2": "Celtics", 
            "team1_odds": "-220", 
            "team2_odds": "+540", 
            "event_time": datetime.now().isoformat()
        }

    def test_add_pick_and_retrieving_based_off_seller(self):
        """
        Test adding a Pick instance to the database.
        """
        # Create a new Pick instance

        pick = add_pick(
            api_id="unique_api_id_123",
            api_vendor_id="vendor_123",
            seller=self.seller, 
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        
        # Fetch the pick from the database
        retrieved_seller_proccessed_picks = get_all_processed_picks_for_seller(self.seller)
        self.assertEqual(retrieved_seller_proccessed_picks.count(), 0)
        
        retrieved_seller_unproccessed_picks = get_all_pending_picks_for_seller(self.seller)
        self.assertFalse(any(pick.has_happened for pick in retrieved_seller_unproccessed_picks))
        self.assertEqual(retrieved_seller_unproccessed_picks.count(), 1)
        
        retrieved_pick = retrieved_seller_unproccessed_picks[0]
        self.assertEqual(retrieved_pick.id, pick.id)
        self.assertEqual(retrieved_pick.api_id, pick.api_id)
        self.assertEqual(retrieved_pick.api_vendor_id, pick.api_vendor_id)
        self.assertEqual(retrieved_pick.seller, pick.seller)
        self.assertEqual(retrieved_pick.event_time, pick.event_time)
        self.assertEqual(retrieved_pick.has_happened, pick.has_happened)
        self.assertEqual(retrieved_pick.meta_data, pick.meta_data)
        
    def test_add_pick_and_retrieving_based_off_buyer(self):
        pick = add_pick(
            api_id="unique_api_id_123",
            api_vendor_id="vendor_123",
            seller=self.seller, 
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        give_buyer_access_to_pick(self.buyer,pick=pick)
        
        retrieved_buyer_proccessed_picks = get_all_processed_picks_for_buyer(self.buyer)
        self.assertEqual(retrieved_buyer_proccessed_picks.count(), 0)
        
        retrieved_buyer_unproccessed_picks = get_all_pending_picks_for_buyer(self.buyer)
        self.assertFalse(any(pick.has_happened for pick in retrieved_buyer_unproccessed_picks))
        self.assertEqual(retrieved_buyer_unproccessed_picks.count(), 1)   
        
        retrieved_pick = retrieved_buyer_unproccessed_picks[0]
        self.assertEqual(retrieved_pick.id, pick.id)
        self.assertEqual(retrieved_pick.api_id, pick.api_id)
        self.assertEqual(retrieved_pick.api_vendor_id, pick.api_vendor_id)
        self.assertEqual(retrieved_pick.seller, pick.seller)
        self.assertEqual(retrieved_pick.event_time, pick.event_time)
        self.assertEqual(retrieved_pick.has_happened, pick.has_happened)
        self.assertEqual(retrieved_pick.meta_data, pick.meta_data)
