from collections import defaultdict
from datetime import datetime
import time
import logging

class LoginAnalytics:
    def __init__(self, config):
        self.config = config
        self.device_counts = defaultdict(int)
        self.locale_counts = defaultdict(int)
        self.version_counts = defaultdict(int)
        self.total_messages_processed = 0  # Total all-time messages
        self.interval_messages = 0  # Messages since last analytics report
        self.error_count = 0
        self.last_sent = time.time()
        self.logger = logging.getLogger(__name__)

    def update(self, message):
        """Update metrics based on message content"""
        self.total_messages_processed += 1
        self.interval_messages += 1  # Increment interval counter
        
        if 'error_type' in message or 'error' in message:
            self.error_count += 1
            return

        self.device_counts[message['device_type']] += 1
        self.locale_counts[message['locale']] += 1
        self.version_counts[message['app_version']] += 1

    def should_send_metrics(self):
        now = time.time()
        if now - self.last_sent >= self.config['metrics']['interval_seconds']:
            self.last_sent = now
            return True
        return False

    def get_metrics(self):
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'messages_in_interval': self.interval_messages,  # Messages since last report
            'total_processed': self.total_messages_processed,
            'error_count': self.error_count,
            'error_rate': round((self.error_count / max(self.total_messages_processed, 1)), 4),
            'device_distribution': dict(self.device_counts),
            'location_distribution': dict(self.locale_counts),
            'version_distribution': dict(self.version_counts)
        }
        
        # Reset interval counter after getting metrics
        self.interval_messages = 0
        
        self.logger.info(f"Generated metrics: {metrics}")
        return metrics