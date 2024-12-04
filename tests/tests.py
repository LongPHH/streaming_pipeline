import pytest
from src.validators.message_validator import MessageValidator
from src.transformers.message_transformer import MessageTransformer

# Sample valid message for reuse in tests
@pytest.fixture
def valid_message():
    return {
        "user_id": "424cdd21-063a-43a7-b91b-7ca1a833afae",
        "app_version": "2.3.0",
        "device_type": "android",
        "ip": "199.172.111.135",
        "locale": "RU",
        "device_id": "593-47-5928",
        "timestamp": "1694479551"
    }

# Test the validator
def test_valid_message_validation(valid_message):
    validator = MessageValidator()
    is_valid, errors = validator.validate_message(valid_message)
    assert is_valid
    assert len(errors) == 0

def test_invalid_message_validation():
    validator = MessageValidator()
    invalid_message = {
        "user_id": "test-123",
        "device_type": "windows"  # Missing fields and invalid device type
    }
    is_valid, errors = validator.validate_message(invalid_message)
    assert not is_valid
    assert len(errors) > 0

# Test the transformer
def test_message_transformation(valid_message):
    transformer = MessageTransformer()
    transformed = transformer.transform_message(valid_message)
    
    # Check the transformation results
    assert transformed['user_id'] == valid_message['user_id']
    assert 'device_category' in transformed
    assert 'processed_at' in transformed