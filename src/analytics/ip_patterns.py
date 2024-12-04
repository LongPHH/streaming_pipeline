from datetime import datetime
from collections import defaultdict
import logging
from typing import Dict, Any

class IPPatternAnalyzer:
    """
    Analyzes IP patterns in login events to detect interesting behaviors.
    Focuses on:
    - Multiple users from same IP
    - High frequency login attempts
    """
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.last_check_time = datetime.now()
        
        # Initialize tracking data
        self.ip_data = {
            'ip_users': defaultdict(set),         # Users per IP
            'login_counts': defaultdict(int),      # Login frequency per IP
            'recent_logins': defaultdict(list)     # Recent login timestamps per IP
        }
        
        # Clear counters for next interval
        self.interval_stats = {
            'high_frequency_ips': set(),          # IPs with unusually high login counts
            'multi_user_ips': set()               # IPs used by multiple users
        }

    def update(self, message):
        """Updates IP tracking data with new login event"""
        try:
            ip = message['ip']
            user_id = message['user_id']
            timestamp = datetime.strptime(message['timestamp'], '%Y-%m-%d %H:%M:%S')
            
            # Track IP-User relationships
            self.ip_data['ip_users'][ip].add(user_id)
            
            # Track login frequency
            self.ip_data['login_counts'][ip] += 1
            
            # Keep last 5 logins for rate analysis
            self.ip_data['recent_logins'][ip].append(timestamp)
            if len(self.ip_data['recent_logins'][ip]) > 5:
                self.ip_data['recent_logins'][ip] = self.ip_data['recent_logins'][ip][-5:]
            
            # Mark suspicious patterns
            if len(self.ip_data['ip_users'][ip]) > 3:
                self.interval_stats['multi_user_ips'].add(ip)
                
            if len(self.ip_data['recent_logins'][ip]) == 5:
                # Check if 5 logins happened within 1 minute
                time_diff = (self.ip_data['recent_logins'][ip][-1] - 
                           self.ip_data['recent_logins'][ip][0]).seconds
                if time_diff < 60:
                    self.interval_stats['high_frequency_ips'].add(ip)
                    
        except Exception as e:
            self.logger.error(f"Error updating IP patterns: {str(e)}")

    def should_send_insights(self):
        """Determines if it's time to send new insights"""
        now = datetime.now()
        if (now - self.last_check_time).seconds >= self.config['analytics_interval']['ippatterns']:
            self.last_check_time = now
            return True
        return False

    def get_insights(self):
        """Generates IP pattern insights"""
        try:
            # Find IPs with most users
            multi_user_ips = [
                (ip, len(users)) 
                for ip, users in self.ip_data['ip_users'].items()
                if len(users) > 1
            ]
            multi_user_ips.sort(key=lambda x: x[1], reverse=True)
            
            insights = {
                "timestamp": datetime.now().isoformat(),
                "ip_patterns": {
                    "suspicious_patterns": {
                        "high_frequency_logins": {
                            "count": len(self.interval_stats['high_frequency_ips']),
                            "ips": list(self.interval_stats['high_frequency_ips'])
                        },
                        "multi_user_access": {
                            "count": len(self.interval_stats['multi_user_ips']),
                            "top_ips": multi_user_ips[:5]  # Top 5 IPs with most users
                        }
                    },
                    "statistics": {
                        "total_unique_ips": len(self.ip_data['ip_users']),
                        "avg_users_per_ip": sum(len(users) for users in self.ip_data['ip_users'].values()) / 
                                          len(self.ip_data['ip_users']) if self.ip_data['ip_users'] else 0
                    }
                }
            }
            
            # Clear interval-specific stats
            self.interval_stats = {
                'high_frequency_ips': set(),
                'multi_user_ips': set()
            }
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating IP insights: {str(e)}")
            return {
                "error": f"Failed to generate IP insights: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }