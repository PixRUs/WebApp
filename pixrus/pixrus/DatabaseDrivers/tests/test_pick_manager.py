from django.test import TestCase
from datetime import datetime
from pixrus.DatabaseDrivers.models import Pick, Seller,Buyer
from django.contrib.auth.models import User

from pixrus.DatabaseDrivers.pick_manager import add_pick, get_all_pending_picks_for_buyer, get_all_processed_picks_for_seller, get_all_pending_picks_for_seller,get_all_processed_picks_for_buyer,give_buyer_access_to_pick,update_pick_with_result

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
    
    def test_multiple_picks_and_retrieving_off_seller_1(self):
    # Create 4 picks with unique API IDs
        pick1 = add_pick(
            api_id="unique_api_id_123",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick2 = add_pick(
            api_id="unique_api_id_124",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick3 = add_pick(
            api_id="unique_api_id_125",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick4 = add_pick(
            api_id="unique_api_id_126",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )

        # Retrieve processed and unprocessed picks
        retrieved_seller_processed_picks = get_all_processed_picks_for_seller(self.seller)
        self.assertEqual(retrieved_seller_processed_picks.count(), 0)  # No processed picks

        # Retrieve unprocessed picks and assert their count
        retrieved_seller_unprocessed_picks = get_all_pending_picks_for_seller(self.seller).order_by('api_id')
        self.assertEqual(retrieved_seller_unprocessed_picks.count(), 4)  # 4 unprocessed picks

        # Assert each pick's data individually
        expected_picks = sorted([pick1, pick2, pick3, pick4], key=lambda x: x.api_id)

        for retrieved_pick, expected_pick in zip(retrieved_seller_unprocessed_picks, expected_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertEqual(retrieved_pick.has_happened, expected_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)

        self.assertFalse(any(pick.has_happened for pick in retrieved_seller_unprocessed_picks))
        
    def test_multiple_picks_and_retrieving_off_buyer_1(self):
        pick1 = add_pick(
            api_id="unique_api_id_123",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick2 = add_pick(
            api_id="unique_api_id_124",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick3 = add_pick(
            api_id="unique_api_id_125",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick4 = add_pick(
            api_id="unique_api_id_126",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        give_buyer_access_to_pick(self.buyer,pick=pick2)
        give_buyer_access_to_pick(self.buyer,pick=pick3)
        give_buyer_access_to_pick(self.buyer,pick=pick4)
        give_buyer_access_to_pick(self.buyer,pick=pick1)
        retrieved_buyer_proccessed_picks = get_all_processed_picks_for_buyer(self.buyer)
        self.assertEqual(retrieved_buyer_proccessed_picks.count(), 0)
        
        retrieved_buyer_unproccessed_picks = get_all_pending_picks_for_buyer(self.buyer).order_by('api_id')
        self.assertFalse(any(pick.has_happened for pick in retrieved_buyer_unproccessed_picks))
        self.assertEqual(retrieved_buyer_unproccessed_picks.count(), 4)   
        expected_picks = sorted([pick1, pick2, pick3, pick4], key=lambda x: x.api_id)

        for retrieved_pick, expected_pick in zip(retrieved_buyer_unproccessed_picks, expected_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertEqual(retrieved_pick.has_happened, expected_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)
    
    def test_multiple_picks_and_retrieving_off_seller_2(self):
    # Create 4 picks with unique API IDs
        pick1 = add_pick(
            api_id="unique_api_id_123",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick2 = add_pick(
            api_id="unique_api_id_124",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick3 = add_pick(
            api_id="unique_api_id_125",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick4 = add_pick(
            api_id="unique_api_id_126",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )

        # Mark some picks as processed
        pick1.has_happened = True
        pick1.save()
        pick3.has_happened = True
        pick3.save()

        # Retrieve processed picks and assert their count and data
        retrieved_seller_processed_picks = get_all_processed_picks_for_seller(self.seller).order_by('api_id')
        self.assertEqual(retrieved_seller_processed_picks.count(), 2)  # 2 processed picks

        expected_processed_picks = sorted([pick1, pick3], key=lambda x: x.api_id)
        for retrieved_pick, expected_pick in zip(retrieved_seller_processed_picks, expected_processed_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertEqual(retrieved_pick.has_happened, expected_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)

        # Retrieve unprocessed picks and assert their count and data
        retrieved_seller_unprocessed_picks = get_all_pending_picks_for_seller(self.seller).order_by('api_id')
        self.assertEqual(retrieved_seller_unprocessed_picks.count(), 2)  # 2 unprocessed picks

        expected_unprocessed_picks = sorted([pick2, pick4], key=lambda x: x.api_id)
        for retrieved_pick, expected_pick in zip(retrieved_seller_unprocessed_picks, expected_unprocessed_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertEqual(retrieved_pick.has_happened, expected_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)

        # Final assertion to confirm no picks in the unprocessed list have happened
        self.assertFalse(any(pick.has_happened for pick in retrieved_seller_unprocessed_picks))
 
    def test_multiple_picks_and_retrieving_off_buyer_2(self):
    # Create 4 picks with unique API IDs
        pick1 = add_pick(
            api_id="unique_api_id_123",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick2 = add_pick(
            api_id="unique_api_id_124",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick3 = add_pick(
            api_id="unique_api_id_125",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick4 = add_pick(
            api_id="unique_api_id_126",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )

        pick1.has_happened = True
        pick1.save()
        pick3.has_happened = True
        pick3.save()

        # Grant buyer access to all picks
        give_buyer_access_to_pick(self.buyer, pick1)
        give_buyer_access_to_pick(self.buyer, pick2)
        give_buyer_access_to_pick(self.buyer, pick3)
        give_buyer_access_to_pick(self.buyer, pick4)

        # Retrieve processed picks for the buyer and assert count and data
        retrieved_buyer_processed_picks = get_all_processed_picks_for_buyer(self.buyer).order_by('api_id')
        self.assertEqual(retrieved_buyer_processed_picks.count(), 2)  # 2 processed picks

        expected_processed_picks = sorted([pick1, pick3], key=lambda x: x.api_id)
        for retrieved_pick, expected_pick in zip(retrieved_buyer_processed_picks, expected_processed_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertEqual(retrieved_pick.has_happened, expected_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)

        # Retrieve unprocessed picks for the buyer and assert count and data
        retrieved_buyer_unprocessed_picks = get_all_pending_picks_for_buyer(self.buyer).order_by('api_id')
        self.assertEqual(retrieved_buyer_unprocessed_picks.count(), 2)  # 2 unprocessed picks

        expected_unprocessed_picks = sorted([pick2, pick4], key=lambda x: x.api_id)
        for retrieved_pick, expected_pick in zip(retrieved_buyer_unprocessed_picks, expected_unprocessed_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertEqual(retrieved_pick.has_happened, expected_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)

        # Final assertion to confirm no picks in the unprocessed list have happened
        self.assertFalse(any(pick.has_happened for pick in retrieved_buyer_unprocessed_picks))

    def test_multiple_picks_and_retrieving_off_buyer_3(self):
        
        # Create 4 picks with unique API IDs
        pick1 = add_pick(
            api_id="unique_api_id_123",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick2 = add_pick(
            api_id="unique_api_id_124",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick3 = add_pick(
            api_id="unique_api_id_125",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick4 = add_pick(
            api_id="unique_api_id_126",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )

        # Define result data for processed picks and update them
        pick1_result_data = {
            "Sport": "Basketball",
            "Team winner": "Lakers",
            "Team loser": "Clippers",
            "Point differential": "12"
        }
        pick4_result_data = {
            "Sport": "Baseball",
            "Team winner": "Yankees",
            "Team loser": "Mets",
            "Point differential": "1"
        }

        # Update pick1 and pick4 with result data, marking them as processed
        update_pick_with_result(pick1, result_data=pick1_result_data)
        update_pick_with_result(pick4, result_data=pick4_result_data)

        # Grant buyer access to all picks
        for pick in [pick1, pick2, pick3, pick4]:
            give_buyer_access_to_pick(self.buyer, pick)

        # Retrieve processed picks for the buyer and assert count and data
        retrieved_buyer_processed_picks = get_all_processed_picks_for_buyer(self.buyer).order_by('api_id')
        self.assertEqual(retrieved_buyer_processed_picks.count(), 2)  # 2 processed picks

        # Check that the processed picks have expected data and results
        expected_processed_picks = sorted([pick1, pick4], key=lambda x: x.api_id)
        for retrieved_pick, expected_pick in zip(retrieved_buyer_processed_picks, expected_processed_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertTrue(retrieved_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)
            # Assert result data matches expected values
            self.assertEqual(retrieved_pick.event_result.result_data, expected_pick.event_result.result_data)

        # Retrieve unprocessed picks for the buyer and assert count and data
        retrieved_buyer_unprocessed_picks = get_all_pending_picks_for_buyer(self.buyer).order_by('api_id')
        self.assertEqual(retrieved_buyer_unprocessed_picks.count(), 2)  # 2 unprocessed picks

        # Check that the unprocessed picks have expected data
        expected_unprocessed_picks = sorted([pick2, pick3], key=lambda x: x.api_id)
        for retrieved_pick, expected_pick in zip(retrieved_buyer_unprocessed_picks, expected_unprocessed_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertFalse(retrieved_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)
    def test_multiple_picks_and_retrieving_off_seller_3(self):
        # Create 4 picks with unique API IDs
        pick1 = add_pick(
            api_id="unique_api_id_123",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick2 = add_pick(
            api_id="unique_api_id_124",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick3 = add_pick(
            api_id="unique_api_id_125",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )
        pick4 = add_pick(
            api_id="unique_api_id_126",
            api_vendor_id="vendor_123",
            seller=self.seller,
            event_time=datetime.now(),
            meta_data=self.meta_data
        )

        # Define result data for processed picks and update them
        pick1_result_data = {
            "Sport": "Basketball",
            "Team winner": "Lakers",
            "Team loser": "Clippers",
            "Point differential": "12"
        }
        pick4_result_data = {
            "Sport": "Baseball",
            "Team winner": "Yankees",
            "Team loser": "Mets",
            "Point differential": "1"
        }

        # Update pick1 and pick4 with result data, marking them as processed
        update_pick_with_result(pick1, result_data=pick1_result_data)
        update_pick_with_result(pick4, result_data=pick4_result_data)

        # Retrieve processed picks for the seller and assert count and data
        retrieved_seller_processed_picks = get_all_processed_picks_for_seller(self.seller).order_by('api_id')
        self.assertEqual(retrieved_seller_processed_picks.count(), 2)  # 2 processed picks

        # Check that the processed picks have expected data and results
        expected_processed_picks = sorted([pick1, pick4], key=lambda x: x.api_id)
        for retrieved_pick, expected_pick in zip(retrieved_seller_processed_picks, expected_processed_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertTrue(retrieved_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)
            # Assert result data matches expected values
            self.assertEqual(retrieved_pick.event_result.result_data, expected_pick.event_result.result_data)

        # Retrieve unprocessed picks for the seller and assert count and data
        retrieved_seller_unprocessed_picks = get_all_pending_picks_for_seller(self.seller).order_by('api_id')
        self.assertEqual(retrieved_seller_unprocessed_picks.count(), 2)  # 2 unprocessed picks

        # Check that the unprocessed picks have expected data
        expected_unprocessed_picks = sorted([pick2, pick3], key=lambda x: x.api_id)
        for retrieved_pick, expected_pick in zip(retrieved_seller_unprocessed_picks, expected_unprocessed_picks):
            self.assertEqual(retrieved_pick.api_id, expected_pick.api_id)
            self.assertEqual(retrieved_pick.api_vendor_id, expected_pick.api_vendor_id)
            self.assertEqual(retrieved_pick.seller, expected_pick.seller)
            self.assertEqual(retrieved_pick.event_time, expected_pick.event_time)
            self.assertFalse(retrieved_pick.has_happened)
            self.assertEqual(retrieved_pick.meta_data, expected_pick.meta_data)

        # Final assertion to confirm no picks in the unprocessed list have happened
        self.assertFalse(any(pick.has_happened for pick in retrieved_seller_unprocessed_picks))

                
