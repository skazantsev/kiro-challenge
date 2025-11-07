# Event Management API

A serverless event management system built with FastAPI, AWS Lambda, API Gateway, and DynamoDB.

## Architecture

- **Backend**: FastAPI REST API
- **Compute**: AWS Lambda (Python 3.11)
- **API Gateway**: AWS API Gateway (REST API)
- **Database**: Amazon DynamoDB
- **Infrastructure**: AWS CDK (Python)

## Features

- Full CRUD operations for events
- Serverless architecture for automatic scaling
- Pay-per-use pricing model
- CORS enabled for web access
- Input validation with Pydantic
- Proper error handling
- DynamoDB reserved keyword handling

## Event Schema

Events have the following properties:
- `eventId` (string, required): Unique identifier
- `title` (string, required): Event title
- `description` (string, required): Event description
- `date` (string, required): Event date (YYYY-MM-DD format)
- `location` (string, required): Event location
- `capacity` (integer, required): Maximum attendees
- `organizer` (string, required): Event organizer name
- `status` (string, required): Event status (active, cancelled, completed)

## Prerequisites

- Python 3.11+
- Node.js 18+ (for AWS CDK)
- AWS CLI configured with credentials
- Docker (for Lambda bundling)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Infrastructure Dependencies

```bash
cd infrastructure
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Deploy to AWS

```bash
cd infrastructure
source venv/bin/activate
cdk bootstrap  # Only needed once per AWS account/region
cdk deploy
```

After deployment, note the API URL from the output:
```
Outputs:
BackendStack.ApiUrl = https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/
```

## API Endpoints

### Base URL
```
https://<api-id>.execute-api.us-east-1.amazonaws.com/prod/
```

### Endpoints

#### 1. List All Events
```bash
GET /events
```

**Query Parameters:**
- `status` (optional): Filter by status (active, cancelled, completed)

**Response:** 200 OK
```json
{
  "events": [
    {
      "eventId": "event-123",
      "title": "Tech Conference 2024",
      "description": "Annual technology conference",
      "eventDate": "2024-12-15",
      "location": "San Francisco",
      "eventCapacity": 500,
      "organizer": "Tech Corp",
      "eventStatus": "active",
      "createdAt": "2024-11-07T10:30:00"
    }
  ]
}
```

#### 2. Get Event by ID
```bash
GET /events/{eventId}
```

**Response:** 200 OK (returns single event object)

#### 3. Create Event
```bash
POST /events
Content-Type: application/json

{
  "eventId": "event-123",
  "title": "Tech Conference 2024",
  "description": "Annual technology conference",
  "date": "2024-12-15",
  "location": "San Francisco",
  "capacity": 500,
  "organizer": "Tech Corp",
  "status": "active"
}
```

**Response:** 201 Created
```json
{
  "eventId": "event-123",
  "message": "Event created successfully"
}
```

#### 4. Update Event
```bash
PUT /events/{eventId}
Content-Type: application/json

{
  "title": "Updated Tech Conference 2024",
  "capacity": 600
}
```

**Response:** 200 OK (returns updated event object)

#### 5. Delete Event
```bash
DELETE /events/{eventId}
```

**Response:** 200 OK
```json
{
  "message": "Event deleted successfully"
}
```

## Usage Examples

### Create an Event
```bash
curl -X POST https://your-api-url/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "api-test-event-456",
    "title": "API Gateway Test Event",
    "description": "Testing API Gateway integration",
    "date": "2024-12-15",
    "location": "API Test Location",
    "capacity": 200,
    "organizer": "API Test Organizer",
    "status": "active"
  }'
```

### List All Events
```bash
curl https://your-api-url/prod/events
```

### Filter Events by Status
```bash
curl https://your-api-url/prod/events?status=active
```

### Get Specific Event
```bash
curl https://your-api-url/prod/events/api-test-event-456
```

### Update Event
```bash
curl -X PUT https://your-api-url/prod/events/api-test-event-456 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated API Gateway Test Event",
    "capacity": 250
  }'
```

### Delete Event
```bash
curl -X DELETE https://your-api-url/prod/events/api-test-event-456
```

## Local Development

### Run Locally with Uvicorn
```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation
Once running locally, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── docs/                # Generated API documentation
├── infrastructure/
│   ├── app.py              # CDK app entry point
│   ├── requirements.txt    # CDK dependencies
│   └── stacks/
│       └── backend_stack.py # Infrastructure definition
└── README.md
```

## Infrastructure Details

The CDK stack creates:
- **DynamoDB Table**: On-demand billing, partition key: `eventId`
- **Lambda Function**: Python 3.11 runtime, 512MB memory, 30s timeout
- **API Gateway**: REST API with Lambda proxy integration
- **IAM Roles**: Least-privilege permissions for Lambda to access DynamoDB

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request (validation errors)
- `404`: Not Found
- `409`: Conflict (duplicate eventId)
- `500`: Internal Server Error

## Cleanup

To remove all AWS resources:
```bash
cd infrastructure
cdk destroy
```

## License

MIT
