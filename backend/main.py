import os
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from mangum import Mangum
import boto3
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError
from datetime import datetime

app = FastAPI(title="Event Management API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('EVENTS_TABLE_NAME', 'EventsTable')
table = dynamodb.Table(table_name)


class EventCreate(BaseModel):
    eventId: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    date: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    capacity: int = Field(..., gt=0)
    organizer: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v not in ['active', 'cancelled', 'completed']:
            raise ValueError('Status must be active, cancelled, or completed')
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    date: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = Field(None, gt=0)
    organizer: Optional[str] = None
    status: Optional[str] = None
    
    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in ['active', 'cancelled', 'completed']:
            raise ValueError('Status must be active, cancelled, or completed')
        return v


@app.get("/")
def read_root():
    return {"message": "Event Management API", "version": "1.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/events")
def list_events(status: Optional[str] = None):
    """List all events, optionally filtered by status"""
    try:
        if status:
            # Use FilterExpression to avoid reserved keyword issues
            response = table.scan(
                FilterExpression=Attr('eventStatus').eq(status)
            )
        else:
            response = table.scan()
        
        return {"events": response.get('Items', [])}
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.get("/events/{event_id}")
def get_event(event_id: str):
    """Get a specific event by ID"""
    try:
        response = table.get_item(Key={'eventId': event_id})
        
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        return response['Item']
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(event: EventCreate):
    """Create a new event"""
    try:
        # Check if event already exists
        response = table.get_item(Key={'eventId': event.eventId})
        if 'Item' in response:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Event with ID {event.eventId} already exists"
            )
        
        # Store with mapped attribute names to avoid reserved keywords
        item = {
            'eventId': event.eventId,
            'title': event.title,
            'description': event.description,
            'eventDate': event.date,  # Renamed from 'date'
            'location': event.location,
            'eventCapacity': event.capacity,  # Renamed from 'capacity'
            'organizer': event.organizer,
            'eventStatus': event.status,  # Renamed from 'status'
            'createdAt': datetime.utcnow().isoformat()
        }
        
        table.put_item(Item=item)
        
        return {"eventId": event.eventId, "message": "Event created successfully"}
    except HTTPException:
        raise
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.put("/events/{event_id}")
def update_event(event_id: str, event: EventUpdate):
    """Update an existing event"""
    try:
        # Check if event exists
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        # Build update expression dynamically
        update_parts = []
        expression_values = {}
        expression_names = {}
        
        if event.title is not None:
            update_parts.append("#title = :title")
            expression_values[':title'] = event.title
            expression_names['#title'] = 'title'
        
        if event.description is not None:
            update_parts.append("description = :description")
            expression_values[':description'] = event.description
        
        if event.date is not None:
            update_parts.append("eventDate = :eventDate")
            expression_values[':eventDate'] = event.date
        
        if event.location is not None:
            update_parts.append("#location = :location")
            expression_values[':location'] = event.location
            expression_names['#location'] = 'location'
        
        if event.capacity is not None:
            update_parts.append("eventCapacity = :eventCapacity")
            expression_values[':eventCapacity'] = event.capacity
        
        if event.organizer is not None:
            update_parts.append("organizer = :organizer")
            expression_values[':organizer'] = event.organizer
        
        if event.status is not None:
            update_parts.append("eventStatus = :eventStatus")
            expression_values[':eventStatus'] = event.status
        
        if not update_parts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_parts.append("updatedAt = :updatedAt")
        expression_values[':updatedAt'] = datetime.utcnow().isoformat()
        
        update_expression = "SET " + ", ".join(update_parts)
        
        kwargs = {
            'Key': {'eventId': event_id},
            'UpdateExpression': update_expression,
            'ExpressionAttributeValues': expression_values,
            'ReturnValues': 'ALL_NEW'
        }
        
        if expression_names:
            kwargs['ExpressionAttributeNames'] = expression_names
        
        response = table.update_item(**kwargs)
        
        return response['Attributes']
    except HTTPException:
        raise
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.delete("/events/{event_id}")
def delete_event(event_id: str):
    """Delete an event"""
    try:
        # Check if event exists
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        table.delete_item(Key={'eventId': event_id})
        
        return {"message": "Event deleted successfully"}
    except HTTPException:
        raise
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# Lambda handler
handler = Mangum(app)
