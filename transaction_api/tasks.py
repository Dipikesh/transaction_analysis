import pandas as pd
import numpy as np
from celery import shared_task
from django.db import transaction
from .models import TransactionUpload
import logging

logger = logging.getLogger(__name__)

@shared_task
def analyze_transactions(upload_id):
    print(f"Analyzing transactions for upload {upload_id}")
    logger.info(f"Analyzing transactions for upload {upload_id}")
    upload = TransactionUpload.objects.get(id=upload_id)
    
    try:
        upload.status = 'processing'
        upload.save()

        logger.info(f"Upload status updated to 'processing'")

        # Read CSV file
        df = pd.read_csv(upload.file.path)
        logger.info(f"CSV file loaded successfully with {len(df)} rows")
        
        # Basic validation
        required_columns = ['transaction_id', 'date', 'amount', 'category']
        logger.info(f"Required columns: {required_columns}")
        if not all(col in df.columns for col in required_columns):
            logger.error(f"Missing required columns in CSV file: {df.columns}")
            raise ValueError("Missing required columns in CSV file")
        logger.info(f"CSV file loaded successfully with {len(df)} rows")

        # Convert date column
        df['date'] = pd.to_datetime(df['date'])
        logger.info(f"Date column converted to datetime: {df['date'].dtype}")
        logger.info(f"Total amount: {df['amount'].sum()}")
        logger.info(f"Average amount: {df['amount'].mean()}")
        logger.info(f"Median amount: {df['amount'].median()}")
        logger.info(f"Outliers: {detect_outliers(df)}")
        logger.info(f"Category summary: {get_category_summary(df)}")
        logger.info(f"Monthly trends: {get_monthly_trends(df)}")
        
        # Perform analysis
        analysis_results = {
            'total_transactions': int(len(df)),
            'total_amount': float(df['amount'].sum()),
            'average_amount': float(df['amount'].mean()),
            'median_amount': float(df['amount'].median()),
            
            # Outlier detection using IQR method
            'outliers': detect_outliers(df),
            
            # Category analysis
            'category_summary': get_category_summary(df),
            
            # Time-based analysis
            'monthly_trends': get_monthly_trends(df)
        }

        upload.status = 'completed'
        upload.result = analysis_results
        upload.save()

    except Exception as e:
        logger.error(f"Error processing upload {upload_id}: {str(e)}")
        upload.status = 'failed'
        upload.result = {'error': str(e)}
        upload.save()
        raise

def detect_outliers(df):
    Q1 = df['amount'].quantile(0.25)
    Q3 = df['amount'].quantile(0.75)
    IQR = Q3 - Q1
    outliers = df[
        (df['amount'] < (Q1 - 1.5 * IQR)) | 
        (df['amount'] > (Q3 + 1.5 * IQR))
    ]
    return {
        'count': int(len(outliers)),
        'transactions': [str(x) for x in outliers['transaction_id'].tolist()]
    }

def get_category_summary(df):
    category_summary = df.groupby('category').agg({
        'amount': ['count', 'sum', 'mean', 'median']
    }).round(2)
    
    # Flatten the MultiIndex columns before converting to dict
    category_summary.columns = [f'amount_{col}' for col in ['count', 'sum', 'mean', 'median']]
    return category_summary.to_dict('index')

def get_monthly_trends(df):
    monthly = df.set_index('date').resample('ME')['amount'].agg(['sum', 'count'])
    result = {}
    for timestamp in monthly.index:
        date_str = timestamp.strftime('%Y-%m-%d')
        result[date_str] = {
            'sum': float(monthly.loc[timestamp, 'sum']),
            'count': int(monthly.loc[timestamp, 'count'])
        }
    return result