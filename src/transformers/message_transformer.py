from datetime import datetime
import logging
from typing import Dict, Any

class MessageTransformer:
    """
    Transforms raw Kafka messages by:
    1. Converting Unix timestamps to human-readable format
    2. Adding device categorization (mobile/web)
    3. Adding processing timestamp
    4. Maintaining original message structure
    """
    
    def __init__(self):
        """Initialize transformer with logging setup"""
        self.logger = logging.getLogger(__name__)

    def transform_timestamp(self, timestamp: str) -> str:
        """
        Convert Unix timestamp to human-readable format
            
        Returns:
            str: Formatted datetime string (YYYY-MM-DD HH:MM:SS)
            
        Note:
            Returns original timestamp if conversion fails
        """
        try:
            dt = datetime.fromtimestamp(int(timestamp))
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            self.logger.error(f"Error transforming timestamp {timestamp}: {str(e)}")
            return timestamp

    def get_device_category(self, device_type: str) -> str:
        """
        Determine high-level device category
            
        Returns:
            str: 'mobile' for android/ios, 'web' for others
        """
        return 'mobile' if device_type in ['android', 'iOS'] else 'web'

    def transform_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply all transformations to incoming message
            
        Returns:
            Dict[str, Any]: Transformed message with:
                - Readable timestamps
                - Device categorization
                - All original fields preserved
                
        Raises:
            Exception: If transformation fails
        """
        try:
            transformed = {
                'user_id': message['user_id'],
                'device_id': message['device_id'],
                'ip': message['ip'],
                'locale': message['locale'],
                'timestamp': self.transform_timestamp(message['timestamp']),
                'device_type': message['device_type'],
                'device_category': self.get_device_category(message['device_type']),
                'app_version': message['app_version'],
                'processed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            self.logger.info(f"Successfully transformed message for user {message['user_id']}")
            return transformed
            
        except Exception as e:
            self.logger.error(f"Error transforming message: {str(e)}")
            raise