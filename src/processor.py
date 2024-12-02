from datetime import datetime
import logging
import yaml
from src.kafka_client import KafkaClient
from src.analytics.metrics import LoginAnalytics
from src.validators.message_validator import MessageValidator
from src.transformers.message_transformer import MessageTransformer

class LoginProcessor:
    """
    Main processor for login event stream that:
    - Consumes raw login events from Kafka
    - Validates message structure and content
    - Transforms timestamps and adds metadata
    - Routes messages to appropriate topics
    - Generates periodic analytics
    """
    def __init__(self):
        # Load configuration
        with open('config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
            
        # Setup logging
        logging.basicConfig(
            level=self.config['logging']['level'],
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.kafka_client = KafkaClient(self.config)
        self.analytics = LoginAnalytics(self.config)
        self.validator = MessageValidator()
        self.transformer = MessageTransformer()
        

    def process_message(self, message):
        """Process a single message through validation and transformation"""
        try:
            # First validate the message
            is_valid, errors = self.validator.validate_message(message)
            
            if not is_valid:
                error_msg = self.validator.enrich_error_message(message, errors)
                error_msg['error_type'] = 'validation_error'
                self.logger.error(f"User ID {message.get('user_id', 'Unknown')}: Validation errors: {errors}")
                return error_msg

            # Transform valid message
            processed = self.transformer.transform_message(message)
            self.logger.info(f"Successfully processed message: {processed}")
            return processed
            
        except Exception as e:
            self.logger.error(f"User ID {message.get('user_id', 'Unknown')}: Processing error - {str(e)}")
            return {
                'error_type': 'processing_error',
                'error_message': str(e),
                'original_message': message
            }
            
    def run(self):
        """Main processing loop for handling message stream"""
        try:
            self.logger.info("Starting message processor...")
            for message in self.kafka_client.consumer:
                # Process message
                processed = self.process_message(message.value)
                
                # Route to appropriate topic based on processing result
                topic = (self.config['kafka']['topics']['processed'] 
                        if 'error_type' not in processed 
                        else self.config['kafka']['topics']['error'])
                
                # Send to Kafka
                self.kafka_client.send_message(topic, processed)
                
                # Update analytics
                self.analytics.update(processed)
                if self.analytics.should_send_metrics():
                    self.kafka_client.send_message(
                        self.config['kafka']['topics']['analytics'], 
                        self.analytics.get_metrics()
                    )
                    
        except KeyboardInterrupt:
            self.logger.info("Shutting down processor...")
        except Exception as e:
            self.logger.error(f"Unexpected error in processor: {str(e)}")
            raise
        finally:
            self.logger.info("Processor shutdown complete")

if __name__ == "__main__":

    processor = LoginProcessor()
    processor.run()