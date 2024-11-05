from django.test import TestCase
from pixrus.DatabaseDrivers.service.auth_login_manager import register_or_update_user
from pixrus.DatabaseDrivers.models import Buyer, Seller 

class UserProfileTests(TestCase):
    def setUp(self):
        # Buyer and Seller setup data
        self.buyer_type = "buyer"
        self.buyer_auth_data = {
            "email": "buyer@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "google_id": "1234567890"
        }
        self.buyer_meta_data = {
            "Preferences": "Basketball",
            "Profile_picture": "/image.png",
            "username": "buyerDothan"
        }

        self.seller_type = "seller"
        self.seller_auth_data = {
            "email": "seller@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
            "google_id": "987654321"
        }
        self.seller_meta_data = {
            "Preferences": "Basketball",
            "Profile_picture": "/image.png",
            "username": "sellerSmith"
        }

    def test_register_or_update_buyer(self):
        # Register buyer and verify
        buyer = register_or_update_user(
            user_auth_data=self.buyer_auth_data,
            user_meta_data=self.buyer_meta_data,
            type_of_user=self.buyer_type
        )[0]
        
        # Verify buyer is created with correct details
        self.assertIsInstance(buyer, Buyer)
        self.assertEqual(buyer.user.email, self.buyer_auth_data["email"])
        self.assertEqual(buyer.user.first_name, self.buyer_auth_data["first_name"])
        self.assertEqual(buyer.user.last_name, self.buyer_auth_data["last_name"])
        self.assertEqual(buyer.meta_data["Preferences"], self.buyer_meta_data["Preferences"])
        self.assertEqual(buyer.meta_data["Profile_picture"], self.buyer_meta_data["Profile_picture"])
        self.assertEqual(buyer.meta_data["username"], self.buyer_meta_data["username"])

    def test_register_or_update_seller(self):
        # Register seller and verify
        seller = register_or_update_user(
            user_auth_data=self.seller_auth_data,
            user_meta_data=self.seller_meta_data,
            type_of_user=self.seller_type
        )[0]
        
        # Verify seller is created with correct details
        self.assertIsInstance(seller, Seller)
        self.assertEqual(seller.user.email, self.seller_auth_data["email"])
        self.assertEqual(seller.user.first_name, self.seller_auth_data["first_name"])
        self.assertEqual(seller.user.last_name, self.seller_auth_data["last_name"])
        self.assertEqual(seller.meta_data["Preferences"], self.seller_meta_data["Preferences"])
        self.assertEqual(seller.meta_data["Profile_picture"], self.seller_meta_data["Profile_picture"])
        self.assertEqual(seller.meta_data["username"], self.seller_meta_data["username"])

    def test_update_existing_buyer(self):
        # Register buyer, then update
        buyer = register_or_update_user(
            user_auth_data=self.buyer_auth_data,
            user_meta_data=self.buyer_meta_data,
            type_of_user=self.buyer_type
        )

        updated_auth_data = {
            "email": "buyer@example.com",  # same email to update the existing record
            "first_name": "UpdatedFirst",
            "last_name": "UpdatedLast",
            "google_id": "1234567890"
        }
        updated_meta_data = {
            "Preferences": "Soccer",
            "Profile_picture": "/updated_image.png",
            "username": "updatedBuyer"
        }

        buyer = register_or_update_user(
            user_auth_data=updated_auth_data,
            user_meta_data=updated_meta_data,
            type_of_user=self.buyer_type
        )[0]

        # Verify the update
        self.assertEqual(buyer.user.first_name, updated_auth_data["first_name"])
        self.assertEqual(buyer.user.last_name, updated_auth_data["last_name"])
        self.assertEqual(buyer.meta_data["Preferences"], updated_meta_data["Preferences"])
        self.assertEqual(buyer.meta_data["Profile_picture"], updated_meta_data["Profile_picture"])
        self.assertEqual(buyer.meta_data["username"], updated_meta_data["username"])

    def test_update_existing_seller(self):
        # Register seller, then update
        seller = register_or_update_user(
            user_auth_data=self.seller_auth_data,
            user_meta_data=self.seller_meta_data,
            type_of_user=self.seller_type
        )

        updated_auth_data = {
            "email": "seller@example.com",  # same email to update the existing record
            "first_name": "UpdatedJane",
            "last_name": "UpdatedSmith",
            "google_id": "987654321"
        }
        updated_meta_data = {
            "Preferences": "Tennis",
            "Profile_picture": "/updated_image.png",
            "username": "updatedSeller"
        }

        seller = register_or_update_user(
            user_auth_data=updated_auth_data,
            user_meta_data=updated_meta_data,
            type_of_user=self.seller_type
        )[0]

        # Verify the update
        self.assertEqual(seller.user.first_name, updated_auth_data["first_name"])
        self.assertEqual(seller.user.last_name, updated_auth_data["last_name"])
        self.assertEqual(seller.meta_data["Preferences"], updated_meta_data["Preferences"])
        self.assertEqual(seller.meta_data["Profile_picture"], updated_meta_data["Profile_picture"])
        self.assertEqual(seller.meta_data["username"], updated_meta_data["username"])
