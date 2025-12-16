"""
Bank Management API Client
===========================
This program demonstrates how to interact with the Bank Management RESTful API
using the requests library to perform CRUD operations.

Author: Nick Psyrras
Date: 2025
"""

import requests
from typing import Optional, Dict, List

# Base URL for the API (adjust if running on different host/port)
BASE_URL = "http://localhost:5001/api"


class BankAPIClient:
    """
    Client class for interacting with the Bank Management RESTful API.
    Provides methods for all CRUD operations.
    """

    def __init__(self, base_url: str = BASE_URL):
        """
        Initialize the API client.
        """
        self.base_url = base_url
        self.session = requests.Session()
        # Set default headers for JSON communication
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def get_all_banks(self) -> Optional[List[Dict]]:
        """
        Retrieve all banks from the API.

        Returns:
            List of bank dictionaries or None if request fails
        """
        try:
            # Send GET request to retrieve all banks
            response = self.session.get(f"{self.base_url}/banks")

            # Raise exception for HTTP errors (4xx, 5xx)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            if data.get("success"):
                print(f"Successfully retrieved {data.get('count', 0)} banks")
                return data.get("data", [])
            else:
                print(f"API returned error: {data.get('error')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching banks: {e}")
            return None

    def get_bank_by_id(self, bank_id: int) -> Optional[Dict]:
        """
        Retrieve a specific bank by ID.

        Args:
            bank_id (int): ID of the bank to retrieve

        Returns:
            Bank dictionary or None if not found or request fails
        """
        try:
            # Send GET request to retrieve specific bank
            response = self.session.get(f"{self.base_url}/banks/{bank_id}")

            # Check if bank was found (404 means not found)
            if response.status_code == 404:
                print(f"Bank with ID {bank_id} not found")
                return None

            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                print(f"Successfully retrieved bank: {data['data']['name']}")
                return data.get("data")
            else:
                print(f"API returned error: {data.get('error')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching bank {bank_id}: {e}")
            return None

    def create_bank(self, name: str, location: str) -> Optional[Dict]:
        """
        Create a new bank record.

        Args:
            name (str): Name of the bank
            location (str): Location of the bank

        Returns:
            Created bank dictionary with ID or None if request fails
        """
        try:
            # Prepare request payload
            payload = {"name": name, "location": location}

            # Send POST request to create new bank
            response = self.session.post(
                f"{self.base_url}/banks",
                json=payload,  # Automatically serializes to JSON
            )

            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                print(
                    f"Successfully created bank: {data['data']['name']} (ID: {data['data']['id']})"
                )
                return data.get("data")
            else:
                print(f"API returned error: {data.get('error')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error creating bank: {e}")
            return None

    def update_bank(self, bank_id: int, name: str, location: str) -> Optional[Dict]:
        """
        Update an existing bank record.

        Args:
            bank_id (int): ID of the bank to update
            name (str): Updated name of the bank
            location (str): Updated location of the bank

        Returns:
            Updated bank dictionary or None if request fails
        """
        try:
            # Prepare request payload
            payload = {"name": name, "location": location}

            # Send PUT request to update bank
            response = self.session.put(
                f"{self.base_url}/banks/{bank_id}", json=payload
            )

            # Check if bank was found
            if response.status_code == 404:
                print(f"Bank with ID {bank_id} not found")
                return None

            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                print(f"Successfully updated bank {bank_id}")
                return data.get("data")
            else:
                print(f"PI returned error: {data.get('error')}")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Error updating bank {bank_id}: {e}")
            return None

    def delete_bank(self, bank_id: int) -> bool:
        """
        Delete a bank record.

        Args:
            bank_id (int): ID of the bank to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Send DELETE request to remove bank
            response = self.session.delete(f"{self.base_url}/banks/{bank_id}")

            # Check if bank was found
            if response.status_code == 404:
                print(f"Bank with ID {bank_id} not found")
                return False

            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                print(f"Successfully deleted bank {bank_id}")
                return True
            else:
                print(f"API returned error: {data.get('error')}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Error deleting bank {bank_id}: {e}")
            return False


def demonstrate_api_usage():
    """
    Demonstration function showing how to use the API client
    to perform all CRUD operations.
    """
    print("=" * 70)
    print("Bank Management API Client - Demonstration")
    print("=" * 70)
    print()

    # Initialize API client
    client = BankAPIClient()

    # CREATE: Add new banks
    print("1. CREATE OPERATION - Adding new banks")
    print("-" * 70)

    bank1 = client.create_bank("Wells Fargo", "San Francisco, CA")
    bank2 = client.create_bank("Bank of America", "Charlotte, NC")
    bank3 = client.create_bank("JPMorgan Chase", "New York, NY")

    print()

    # READ: Retrieve all banks
    print("2. READ OPERATION - Retrieving all banks")
    print("-" * 70)

    all_banks = client.get_all_banks()

    if all_banks:
        print("\nAll Banks in Database:")
        for bank in all_banks:
            print(
                f"  ID: {bank['id']}, Name: {bank['name']}, Location: {bank['location']}"
            )

    print()

    # READ: Retrieve specific bank
    print("3. READ OPERATION - Retrieving specific bank")
    print("-" * 70)

    if bank1:
        specific_bank = client.get_bank_by_id(bank1["id"])
        if specific_bank:
            print("\nBank Details:")
            print(f"  ID: {specific_bank['id']}")
            print(f"  Name: {specific_bank['name']}")
            print(f"  Location: {specific_bank['location']}")

    print()

    # UPDATE: Modify existing bank
    print("4. UPDATE OPERATION - Modifying bank information")
    print("-" * 70)

    if bank2:
        updated_bank = client.update_bank(
            bank2["id"], "Bank of America (Updated)", "Charlotte, North Carolina"
        )

    print()

    # DELETE: Remove a bank
    print("5. DELETE OPERATION - Removing a bank")
    print("-" * 70)

    if bank3:
        client.delete_bank(bank3["id"])

    print()

    # VERIFY: List all banks after operations
    print("6. VERIFICATION - Final state of database")
    print("-" * 70)

    final_banks = client.get_all_banks()

    if final_banks:
        print("\nRemaining Banks:")
        for bank in final_banks:
            print(
                f"  ID: {bank['id']}, Name: {bank['name']}, Location: {bank['location']}"
            )

    print()
    print("=" * 70)
    print("Demonstration Complete")
    print("=" * 70)


if __name__ == "__main__":
    """
    Main entry point for the API client program.
    This program automatically performs all CRUD operations
    """

    print("\nBank Management API Client")
    print("Make sure the Flask application is running on http://localhost:5001")

    # Run demonstration
    demonstrate_api_usage()
