"""
Tests for financial data API endpoints.
"""
import json

from django.test import TestCase


class FinancialAPITestCase(TestCase):
    """Test cases for financial data API."""

    def test_extract_financial_data_endpoint(self):
        """Test the extract financial data endpoint."""
        url = '/api/v1/extract-financial-data'
        data = {'user_document': '12345678901'}

        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.content.decode()}")

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Parse response JSON
        response_data = response.json()

        # Verify response structure
        self.assertIn('user_document', response_data)
        self.assertIn('extraction_date', response_data)
        self.assertIn('accounts', response_data)
        self.assertIn('summary', response_data)

        # Verify user document matches
        self.assertEqual(response_data['user_document'], '12345678901')

        # Verify accounts structure
        self.assertIsInstance(response_data['accounts'], list)
        self.assertGreater(len(response_data['accounts']), 0)

        # Verify first account structure
        account = response_data['accounts'][0]
        self.assertIn('account_id', account)
        self.assertIn('account_type', account)
        self.assertIn('account_status', account)
        self.assertIn('balance', account)
        self.assertIn('transactions', account)

        # Verify summary structure
        summary = response_data['summary']
        self.assertIn('total_accounts', summary)
        self.assertIn('total_transactions', summary)
        self.assertIn('processing_time_ms', summary)
        self.assertIn('errors', summary)
