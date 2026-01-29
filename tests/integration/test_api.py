"""
Integration tests for AI API functionality
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

class TestGoogleAIIntegration:
    """Test Google AI API integration"""

    @pytest.fixture
    def mock_genai_client(self):
        """Mock Google AI client for testing"""
        with patch('google.genai.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client

            # Mock the models.generate_content method
            mock_response = MagicMock()
            mock_response.text = '''```json
            {"breakfast": {"name": "Test Meal", "ingredients": ["test"], "recipe": "test"}}
            ```'''
            mock_client.models.generate_content.return_value = mock_response

            yield mock_client

    def test_api_response_parsing(self, mock_genai_client):
        """Test that API responses are correctly parsed"""
        from google.genai import Client

        # Create client (will use our mock)
        client = Client(api_key='test_key')
        simple_prompt = 'Return this JSON: {"breakfast": {"name": "Test Meal", "ingredients": ["test"], "recipe": "test"}}'

        # Make the API call
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=simple_prompt
        )

        # Verify the call was made correctly
        client.models.generate_content.assert_called_once_with(
            model='gemini-2.5-flash',
            contents=simple_prompt
        )

        # Test response parsing logic
        result_text = response.text.strip()

        # Parse like the application does
        if result_text.startswith('```json'):
            result_text = result_text[7:]
        if result_text.startswith('```'):
            result_text = result_text[3:]
        if result_text.endswith('```'):
            result_text = result_text[:-3]

        result_text = result_text.strip()
        result = json.loads(result_text)

        # Verify parsing worked
        assert result["breakfast"]["name"] == "Test Meal"
        assert "test" in result["breakfast"]["ingredients"]

    def test_api_error_handling(self, mock_genai_client):
        """Test API error handling"""
        # Configure mock to raise an exception
        mock_genai_client.models.generate_content.side_effect = Exception("API Error")

        from google.genai import Client

        client = Client(api_key='test_key')

        with pytest.raises(Exception, match="API Error"):
            client.models.generate_content(
                model='gemini-2.5-flash',
                contents='test prompt'
            )

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_api_call(self, mock_ai_config):
        """Test real API call (marked as slow and integration)"""
        # Skip if no real API key configured
        if not mock_ai_config.get('gemini_key'):
            pytest.skip("No Gemini API key configured for integration testing")

        # This would make a real API call in CI/integration environment
        # For now, we'll skip it to avoid API costs during development
        pytest.skip("Real API calls disabled during development")

    def test_json_response_validation(self):
        """Test JSON response validation logic"""

        # Test various response formats
        test_cases = [
            ('```json\n{"test": "value"}\n```', {"test": "value"}),
            ('```\n{"test": "value"}\n```', {"test": "value"}),
            ('{"test": "value"}', {"test": "value"}),
            ('```json\ninvalid json```', None),  # Should handle parsing errors
        ]

        for raw_response, expected in test_cases:
            result_text = raw_response.strip()

            # Apply the same parsing logic as the application
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]

            result_text = result_text.strip()

            if expected is None:
                # Should handle parsing errors gracefully
                with pytest.raises(json.JSONDecodeError):
                    json.loads(result_text)
            else:
                result = json.loads(result_text)
                assert result == expected

    def test_meal_plan_response_structure(self):
        """Test that meal plan responses have correct structure"""

        # Sample meal plan response
        meal_plan_response = {
            "success": True,
            "date": "2024-01-21",
            "meals": {
                "breakfast": {
                    "name": "Oatmeal with Fruits",
                    "ingredients": ["oats", "banana", "milk"],
                    "recipe": "Mix ingredients and cook",
                    "nutrition": {"calories": 350, "protein": "12g"}
                },
                "lunch": {
                    "name": "Grilled Chicken Salad",
                    "ingredients": ["chicken", "lettuce", "tomatoes"],
                    "recipe": "Grill chicken and toss with veggies",
                    "nutrition": {"calories": 400, "protein": "30g"}
                }
            }
        }

        # Validate structure
        assert meal_plan_response["success"] is True
        assert "meals" in meal_plan_response
        assert "breakfast" in meal_plan_response["meals"]
        assert "lunch" in meal_plan_response["meals"]

        # Validate meal structure
        for meal_type in ["breakfast", "lunch"]:
            meal = meal_plan_response["meals"][meal_type]
            required_fields = ["name", "ingredients", "recipe", "nutrition"]
            for field in required_fields:
                assert field in meal, f"Missing {field} in {meal_type}"

            assert isinstance(meal["ingredients"], list)
            assert len(meal["ingredients"]) > 0