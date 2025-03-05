# Transaction Data Analyzer API

A Django-based REST API service that analyzes transaction data from CSV files using asynchronous processing with Celery.

## Features

- CSV file upload for transaction data analysis
- Asynchronous processing using Celery
- Complex data analysis including outlier detection and category-wise statistics
- Dockerized application stack
- RESTful API endpoints for upload and result retrieval

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository:

2. Build and start the services:

```bash
docker-compose up --build
```


This will start:
- Django application (port 8000)
- Redis broker
- Celery worker

## API Endpoints

### 1. Upload Transaction File
- **URL:** `/api/upload/`
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Request Body:**
  - `file`: CSV file containing transaction data
- **Response:**

```
{
"id": "upload_id",
"status": "pending",
"upload_time": "2024-03-21T10:00:00Z"
}
```


### 2. Check Analysis Status
- **URL:** `/api/uploads/<upload_id>/`
- **Method:** `GET`
- **Response:**

```
{
"id": "upload_id",
"status": "completed",
"upload_time": "2024-03-21T10:00:00Z",
"result": {
"total_transactions": 100,
"total_amount": 50000,
"average_amount": 500,
"outliers": [...],
"category_analysis": {
"category1": {...},
"category2": {...}
}
}
}
```
### 3. Check All Uploads Analysis Status
- **URL:** `/api/uploads/`
- **Method:** `GET`
- **Response:**

```
[{
"id": "upload_id",
"status": "completed",
"upload_time": "2024-03-21T10:00:00Z",
"result": {
"total_transactions": 100,
"total_amount": 50000,
"average_amount": 500,
"outliers": [...],
"category_analysis": {
"category1": {...},
"category2": {...}
}
}
}]
```



## CSV File Format

The uploaded CSV file should contain the following columns:
- transaction_id
- date
- amount
- category

Example:
```
csv
transaction_id,date,amount,category
1,2024-03-21,100.00,groceries
2,2024-03-21,50.00,entertainment
```


# transaction_analysis
