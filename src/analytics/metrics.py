from collections import defaultdict
from datetime import datetime
import time
import logging

class LoginAnalytics:
    '''
    This module processes login events and generates periodic metrics reports including:
    Message processing counts and error rates
    Device, location, and app version distributions
    Unique user counts and growth
    '''

    def __init__(self, config):
        self.config = config
        # Original metrics
        self.device_counts = defaultdict(int)
        self.locale_counts = defaultdict(int)
        self.version_counts = defaultdict(int)
        self.total_messages_processed = 0
        self.interval_messages = 0
        self.error_count = 0
        self.last_sent = time.time()
        
        # User tracking
        self.unique_users = set()
        self.last_user_count = 0
        
        self.logger = logging.getLogger(__name__)

    def update(self, message):
        """Update metrics based on message content"""
        self.total_messages_processed += 1
        self.interval_messages += 1
        
        if 'error_type' in message or 'error' in message:
            self.error_count += 1
            return

        # Update regular metrics
        self.device_counts[message['device_type']] += 1
        self.locale_counts[message['locale']] += 1
        self.version_counts[message['app_version']] += 1
        
        # Track unique users
        if 'user_id' in message:
            self.unique_users.add(message['user_id'])

    def should_send_metrics(self):
        now = time.time()
        if now - self.last_sent >= self.config['analytics_interval']['metrics']:
            self.last_sent = now
            return True
        return False

    def get_metrics(self):
        """Get all metrics including user stats"""
        current_user_count = len(self.unique_users)
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'messages_in_interval': self.interval_messages,
            'total_processed': self.total_messages_processed,
            'error_count': self.error_count,
            'error_rate': round((self.error_count / max(self.total_messages_processed, 1)), 4),
            'device_distribution': dict(self.device_counts),
            'location_distribution': dict(self.locale_counts),
            'version_distribution': dict(self.version_counts),
            'total_unique_users': current_user_count,
            'new_users_since_last': current_user_count - self.last_user_count
        }
        
        self.interval_messages = 0
        self.last_user_count = current_user_count
        
        self.logger.info(f"Generated metrics: {metrics}")
        return metrics