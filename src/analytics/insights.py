from datetime import datetime
from collections import defaultdict
import logging
from typing import Dict, Any

class LoginInsights:
    """
    Analyzes login events to provide behavioral insights and patterns.
    Focuses on user behavior, regional patterns, and app version adoption rate
    All of these analytics logic have been "simplified" for demonstration purposes.
    """
    
    def __init__(self, config):
        """
        Initialize insights analyzer with configuration settings
        Args:
            config: Application configuration containing Kafka and metrics settings
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.last_insights_time = datetime.now()
        
        # Initialize tracking dictionaries
        self.stats = {
            'devices': defaultdict(int),          # Track device usage
            'locations': defaultdict(int),        # Track logins by state
            'previous_logins': defaultdict(dict), # Track user's previous login info
            'users_this_interval': set(),         # Track unique users in current interval
            'previous_users': set(),              # Track users from last interval
            'versions': defaultdict(int),         # Track app version usage
            'version_upgrades': defaultdict(list) # Track version upgrade patterns
        }
        
        # Regional grouping of states
        self.regions = {
            'northeast': {'ME', 'NH', 'VT', 'MA', 'RI', 'CT', 'NY', 'NJ', 'PA'},
            'southeast': {'MD', 'DE', 'VA', 'WV', 'KY', 'NC', 'SC', 'TN', 'GA', 'FL', 'AL', 'MS', 'AR', 'LA'},
            'midwest': {'OH', 'IN', 'IL', 'MI', 'WI', 'MN', 'IA', 'MO', 'ND', 'SD', 'NE', 'KS'},
            'west': {'MT', 'ID', 'WY', 'CO', 'NM', 'AZ', 'UT', 'NV', 'CA', 'OR', 'WA', 'AK', 'HI'}
        }

    def update(self, message):
        """
        Process a new login event and update insights
        Args:
            message: Processed login event containing user and device information
        """
        try:
            if 'error_type' in message:
                return

            # Track basic stats
            self.stats['devices'][message['device_type']] += 1
            self.stats['locations'][message['locale']] += 1
            self.stats['versions'][message['app_version']] += 1
            
            user_id = message['user_id']
            self.stats['users_this_interval'].add(user_id)
            
            # Track device switches and version upgrades
            if user_id in self.stats['previous_logins']:
                prev_login = self.stats['previous_logins'][user_id]
                
                # Check for device switch
                if prev_login['device_type'] != message['device_type']:
                    self.stats['device_switches'] = self.stats.get('device_switches', 0) + 1
                
                # Check for version upgrade
                prev_version = prev_login.get('app_version')
                if prev_version and prev_version != message['app_version']:
                    self.stats['version_upgrades'][user_id].append({
                        'from_version': prev_version,
                        'to_version': message['app_version'],
                        'timestamp': message['timestamp']
                    })
                    
            # Update user's previous login info
            self.stats['previous_logins'][user_id] = {
                'device_type': message['device_type'],
                'timestamp': message['timestamp'],
                'locale': message['locale'],
                'app_version': message['app_version']
            }
            
        except Exception as e:
            self.logger.error(f"Error updating login insights: {str(e)}")

    def _calculate_regional_distribution(self) :
        """
        Calculate login distribution across geographic regions
        Returns:
            Dict containing percentage of logins for each region
        """
        total_logins = sum(self.stats['locations'].values())
        regional_counts = defaultdict(int)
        
        for state, count in self.stats['locations'].items():
            for region, states in self.regions.items():
                if state in states:
                    regional_counts[region] += count
                    
        return {
            region: round((count / total_logins * 100),2) if total_logins > 0 else 0
            for region, count in regional_counts.items()
        }

    def _get_device_loyalty_stats(self) :
        """
        Calculate device usage patterns and platform loyalty
        Returns:
            Dict containing platform preferences and switching rates
        """
        total_devices = sum(self.stats['devices'].values())
        platform_percentages = {
            device: (count / total_devices * 100) if total_devices > 0 else 0
            for device, count in self.stats['devices'].items()
        }
        
        switch_rate = (self.stats.get('device_switches', 0) / 
                      len(self.stats['previous_logins']) * 100) if self.stats['previous_logins'] else 0
        
        return {
            "primary_platform": max(self.stats['devices'].items(), key=lambda x: x[1])[0],
            "platform_shift_rate": f"{switch_rate:.1f}%",
            "platform_preference": {k: f"{v:.1f}%" for k, v in platform_percentages.items()}
        }

    def _get_version_insights(self) :
        """
        Calculate version adoption and upgrade patterns
        Returns:
            Dict containing version distribution and upgrade statistics
        """
        total_logins = sum(self.stats['versions'].values())
        if not total_logins:
            return {}
            
        # Find current/latest version
        latest_version = max(self.stats['versions'].keys())
        
        # Calculate adoption rates
        version_rates = {
            version: (count / total_logins * 100)
            for version, count in self.stats['versions'].items()
        }
        
        # Calculate upgrade metrics
        total_upgrades = sum(len(upgrades) for upgrades in self.stats['version_upgrades'].values())
        
        return {
            "current_version": latest_version,
            "adoption_rates": {k: f"{v:.1f}%" for k, v in version_rates.items()},
            "upgrade_statistics": {
                "total_upgrades": total_upgrades,
                "versions_distribution": dict(self.stats['versions'])
            }
        }

    def should_send_insights(self) -> bool:
        """Check if it's time to send new insights based on configured interval"""
        now = datetime.now()
        if (now - self.last_insights_time).seconds >= self.config['analytics_interval']['insights']:
            self.last_insights_time = now
            return True
        return False

    def get_insights(self):
        """
        Generate comprehensive behavioral insights
        Returns:
            Dict containing behavioral analysis including:
            - User engagement patterns
            - Geographic distribution
            - Device loyalty
            - Version adoption patterns
        """
        try:
            # Sort states by activity
            sorted_states = sorted(
                self.stats['locations'].items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            insights = {
                "timestamp": datetime.now().isoformat(),
                "behavioral_analysis": {
                    "user_engagement": {
                        "device_loyalty": self._get_device_loyalty_stats(),
                        "geographic_patterns": {
                            "highest_activity_states": [state for state, _ in sorted_states[:5]],
                            "lowest_activity_states": [state for state, _ in sorted_states[-4:]],
                            "regional_breakdown": self._calculate_regional_distribution()
                        },
                        "user_loyalty": {
                            "returning_users": len(self.stats['previous_users']),
                            "new_users": len(self.stats['users_this_interval'] - self.stats['previous_users']),
                            "retention_rate": f"{(len(self.stats['previous_users']) / len(self.stats['users_this_interval']) * 100):.1f}%" if self.stats['users_this_interval'] else "0%"
                        }
                    },
                    "app_insights": {
                        "version_adoption": self._get_version_insights()
                    }
                }
            }
            
            # Update previous users for next interval
            self.stats['previous_users'] = self.stats['users_this_interval'].copy()
            self.stats['users_this_interval'] = set()
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {str(e)}")
            return {
                "error": f"Failed to generate insights: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }