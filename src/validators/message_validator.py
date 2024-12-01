from datetime import datetime
import logging
import ipaddress
from typing import Dict, List, Tuple, Union

class MessageValidator:
    """Validates incoming messages and categorizes errors"""
    
    # Update timestamp to accept either str or int
    REQUIRED_FIELDS = {
        'user_id': str,
        'timestamp': (str, int),  # Accept either string or integer
        'device_type': str,
        'locale': str,
        'app_version': str,
        'ip': str,
        'device_id': str
    }
    
    VALID_DEVICE_TYPES = {'android', 'ios', 'web'}
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    def validate_message(self, message: Dict) -> Tuple[bool, List[Dict]]:
        errors = []
        
        # Modified type checking to handle multiple allowed types
        for field, expected_type in self.REQUIRED_FIELDS.items():
            if field not in message:
                errors.append({
                    'error_type': 'missing_field',
                    'field': field
                })
            elif field == 'timestamp':
                if not isinstance(message[field], (str, int)):
                    errors.append({
                        'error_type': 'invalid_type',
                        'field': field,
                        'expected': 'str or int',
                        'received': type(message[field]).__name__
                    })
            elif not isinstance(message[field], expected_type):
                errors.append({
                    'error_type': 'invalid_type',
                    'field': field,
                    'expected': expected_type.__name__,
                    'received': type(message[field]).__name__
                })

        # Validate timestamp value regardless of type
        if 'timestamp' in message:
            try:
                # Convert to int if it's a string
                timestamp = int(message['timestamp']) if isinstance(message['timestamp'], str) else message['timestamp']
                if timestamp <= 0:
                    errors.append({
                        'error_type': 'invalid_timestamp',
                        'value': message['timestamp']
                    })
            except ValueError:
                errors.append({
                    'error_type': 'invalid_timestamp_format',
                    'value': message['timestamp']
                })

        # Rest of your validation code remains the same...
        if 'ip' in message:
            try:
                ipaddress.ip_address(message['ip'])
            except ValueError:
                errors.append({
                    'error_type': 'invalid_ip_format',
                    'value': message['ip']
                })

        if 'app_version' in message:
            version = message['app_version']
            if not all(part.isdigit() for part in version.split('.')):
                errors.append({
                    'error_type': 'invalid_version_format',
                    'value': version
                })

        if 'device_type' in message and message['device_type'].lower() not in self.VALID_DEVICE_TYPES:
            errors.append({
                'error_type': 'invalid_device_type',
                'value': message['device_type'],
                'valid_values': list(self.VALID_DEVICE_TYPES)
            })

        if 'locale' in message:
            locale = message['locale']
            if not (len(locale) == 2 or (len(locale) == 5 and locale[2] == '_')):
                errors.append({
                    'error_type': 'invalid_locale_format',
                    'value': locale
                })

        return len(errors) == 0, errors

    def enrich_error_message(self, original_message: Dict, errors: List[Dict]) -> Dict:
        return {
            'original_message': original_message,
            'errors': errors,
            'error_count': len(errors),
            'timestamp': datetime.now().isoformat(),
            'error_summary': [e['error_type'] for e in errors]
        }