"""
S3 handler for CAIS platform.
Provides functions for uploading, downloading, and managing data in S3.
"""

import boto3
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import tempfile
from botocore.exceptions import ClientError, NoCredentialsError

from config import config


class S3Handler:
    """Handler for S3 operations in CAIS platform."""
    
    def __init__(self, bucket_name: str = None):
        """
        Initialize S3 handler.
        
        Args:
            bucket_name: S3 bucket name, defaults to config value
        """
        self.bucket_name = bucket_name or config.S3_BUCKET_NAME
        self._client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize S3 client with credentials."""
        try:
            session = boto3.Session(
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                region_name=config.AWS_REGION
            )
            self._client = session.client('s3')
            
            # Test connection
            self._client.head_bucket(Bucket=self.bucket_name)
            
        except NoCredentialsError:
            print("Warning: AWS credentials not found. S3 operations will fail.")
            self._client = None
        except ClientError as e:
            print(f"Warning: Failed to connect to S3 bucket {self.bucket_name}: {e}")
            self._client = None
    
    def is_available(self) -> bool:
        """Check if S3 is available and configured."""
        return self._client is not None
    
    def upload_file(self, file_path: str, s3_key: str) -> bool:
        """
        Upload a file to S3.
        
        Args:
            file_path: Local path to the file
            s3_key: S3 key (path) for the uploaded file
            
        Returns:
            True if upload successful, False otherwise
        """
        if not self.is_available():
            print("S3 not available for upload")
            return False
        
        try:
            self._client.upload_file(file_path, self.bucket_name, s3_key)
            return True
        except Exception as e:
            print(f"Failed to upload {file_path} to S3: {e}")
            return False
    
    def download_file(self, s3_key: str, file_path: str) -> bool:
        """
        Download a file from S3.
        
        Args:
            s3_key: S3 key (path) of the file to download
            file_path: Local path where file should be saved
            
        Returns:
            True if download successful, False otherwise
        """
        if not self.is_available():
            print("S3 not available for download")
            return False
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            self._client.download_file(self.bucket_name, s3_key, file_path)
            return True
        except Exception as e:
            print(f"Failed to download {s3_key} from S3: {e}")
            return False
    
    def upload_json(self, data: Dict[str, Any], s3_key: str) -> bool:
        """
        Upload JSON data to S3.
        
        Args:
            data: Dictionary to upload as JSON
            s3_key: S3 key for the JSON file
            
        Returns:
            True if upload successful, False otherwise
        """
        if not self.is_available():
            print("S3 not available for JSON upload")
            return False
        
        try:
            json_data = json.dumps(data, indent=2, default=str)
            self._client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data,
                ContentType='application/json'
            )
            return True
        except Exception as e:
            print(f"Failed to upload JSON to S3: {e}")
            return False
    
    def download_json(self, s3_key: str) -> Optional[Dict[str, Any]]:
        """
        Download and parse JSON data from S3.
        
        Args:
            s3_key: S3 key of the JSON file
            
        Returns:
            Parsed JSON data or None if failed
        """
        if not self.is_available():
            print("S3 not available for JSON download")
            return None
        
        try:
            response = self._client.get_object(Bucket=self.bucket_name, Key=s3_key)
            content = response['Body'].read().decode('utf-8')
            return json.loads(content)
        except Exception as e:
            print(f"Failed to download JSON from S3: {e}")
            return None
    
    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> List[str]:
        """
        List objects in S3 bucket with given prefix.
        
        Args:
            prefix: S3 key prefix to filter objects
            max_keys: Maximum number of keys to return
            
        Returns:
            List of S3 keys
        """
        if not self.is_available():
            print("S3 not available for listing")
            return []
        
        try:
            response = self._client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            if 'Contents' in response:
                return [obj['Key'] for obj in response['Contents']]
            return []
            
        except Exception as e:
            print(f"Failed to list S3 objects: {e}")
            return []
    
    def delete_object(self, s3_key: str) -> bool:
        """
        Delete an object from S3.
        
        Args:
            s3_key: S3 key of the object to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.is_available():
            print("S3 not available for deletion")
            return False
        
        try:
            self._client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception as e:
            print(f"Failed to delete S3 object: {e}")
            return False
    
    def save_analysis_result(self, analysis_result: Dict[str, Any]) -> str:
        """
        Save analysis result to S3.
        
        Args:
            analysis_result: Analysis result dictionary
            
        Returns:
            S3 key of the saved result
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_name = analysis_result.get('company_name', 'unknown').replace(' ', '_')
        user_name = analysis_result.get('user_name', 'unknown').replace(' ', '_')
        
        s3_key = f"{config.S3_ANALYSIS_RESULTS_PREFIX}{timestamp}_{user_name}_{company_name}.json"
        
        if self.upload_json(analysis_result, s3_key):
            return s3_key
        return ""
    
    def save_training_data(self, training_example: Dict[str, Any]) -> str:
        """
        Save training data to S3.
        
        Args:
            training_example: Training example dictionary
            
        Returns:
            S3 key of the saved training data
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        example_id = training_example.get('id', timestamp)
        
        s3_key = f"{config.S3_TRAINING_DATA_PREFIX}{example_id}.json"
        
        if self.upload_json(training_example, s3_key):
            return s3_key
        return ""
    
    def save_feedback(self, feedback: Dict[str, Any]) -> str:
        """
        Save user feedback to S3.
        
        Args:
            feedback: Feedback dictionary
            
        Returns:
            S3 key of the saved feedback
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        s3_key = f"{config.S3_FEEDBACK_PREFIX}feedback_{timestamp}.json"
        
        if self.upload_json(feedback, s3_key):
            return s3_key
        return ""
    
    def load_training_data(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        Load training data from S3 within date range.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of training examples
        """
        training_data = []
        
        # List all training data files
        keys = self.list_objects(prefix=config.S3_TRAINING_DATA_PREFIX)
        
        for key in keys:
            # Load each training example
            data = self.download_json(key)
            if data:
                # Filter by date if specified
                if start_date or end_date:
                    try:
                        created_at = data.get('created_at', '')
                        if created_at:
                            file_date = created_at.split('T')[0]  # Extract date part
                            if start_date and file_date < start_date:
                                continue
                            if end_date and file_date > end_date:
                                continue
                    except:
                        continue  # Skip if date parsing fails
                
                training_data.append(data)
        
        return training_data
    
    def upload_document(self, file_path: str, user_name: str, company_name: str) -> str:
        """
        Upload a document file to S3 with organized naming.
        
        Args:
            file_path: Local path to the document
            user_name: Name of the user uploading
            company_name: Name of the company
            
        Returns:
            S3 key of the uploaded document
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = Path(file_path).name
        safe_user = user_name.replace(' ', '_')
        safe_company = company_name.replace(' ', '_')
        
        s3_key = f"{config.S3_DOCUMENTS_PREFIX}{safe_user}/{safe_company}/{timestamp}_{file_name}"
        
        if self.upload_file(file_path, s3_key):
            return s3_key
        return ""