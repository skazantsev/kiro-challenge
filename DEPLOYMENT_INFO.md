# Deployment Information

## Deployed API Endpoint

**Base URL:** `https://iohh4xiow7.execute-api.us-east-1.amazonaws.com/prod/`

## AWS Resources Created

- **API Gateway:** EventsApi (REST API)
- **Lambda Function:** EventsApiFunction (Python 3.11, 512MB, 30s timeout)
- **DynamoDB Table:** BackendStack-EventsTableD24865E5-U6KD6GBBRH44
- **IAM Role:** Lambda execution role with DynamoDB read/write permissions

## Test the API

### 1. List all events
```bash
curl https://iohh4xiow7.execute-api.us-east-1.amazonaws.com/prod/events
```

### 2. Create an event
```bash
curl -X POST https://iohh4xiow7.execute-api.us-east-1.amazonaws.com/prod/events \
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

### 3. Get specific event
```bash
curl https://iohh4xiow7.execute-api.us-east-1.amazonaws.com/prod/events/api-test-event-456
```

### 4. Filter by status
```bash
curl https://iohh4xiow7.execute-api.us-east-1.amazonaws.com/prod/events?status=active
```

### 5. Update event
```bash
curl -X PUT https://iohh4xiow7.execute-api.us-east-1.amazonaws.com/prod/events/api-test-event-456 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated API Gateway Test Event",
    "capacity": 250
  }'
```

### 6. Delete event
```bash
curl -X DELETE https://iohh4xiow7.execute-api.us-east-1.amazonaws.com/prod/events/api-test-event-456
```

## Expected Test Results

Based on your test requirements:

| Test | Expected Status | Notes |
|------|----------------|-------|
| GET /events | 200 | Returns list of all events |
| GET /events?status=active | 200 | Returns filtered events |
| POST /events | 201 | Creates event with eventId in response |
| GET /events/api-test-event-456 | 200 | Returns specific event |
| PUT /events/api-test-event-456 | 200 | Updates and returns event |
| DELETE /events/api-test-event-456 | 200 | Deletes event successfully |

## Architecture Highlights

- **Serverless**: No servers to manage, automatic scaling
- **Pay-per-use**: Only pay for actual API calls
- **DynamoDB**: NoSQL database with on-demand billing
- **CORS Enabled**: Ready for web application integration
- **Input Validation**: Pydantic models ensure data integrity
- **Reserved Keywords**: Properly handled (status → eventStatus, capacity → eventCapacity)

## Cleanup

To remove all resources and avoid charges:
```bash
cd infrastructure
source venv/bin/activate
cdk destroy
```

## Documentation

- **README.md**: Complete setup and usage guide
- **backend/docs/api_documentation.html**: Detailed API documentation
