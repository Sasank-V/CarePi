import json
import datetime as dt
import logging
from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from database.schemas import get_db, CalendarEvent, Todo, Reminder
from responses.vapi import (
    VapiRequest,
    CalendarEventResponse,
    ReminderResponse,
    TodoResponse,
)

app = FastAPI()

# Configure logging
logger = logging.getLogger("uvicorn.error")
logger.setLevel(logging.DEBUG)


# Raw endpoint to capture real Vapi requests
@app.post("/vapi_raw/")
async def vapi_raw(request: Request):
    body = await request.body()
    headers = dict(request.headers)

    logger.info("=== REAL VAPI REQUEST ===")
    logger.info(f"Headers: {headers}")
    logger.info(f"Raw Body: {body.decode('utf-8')}")

    try:
        json_data = json.loads(body.decode("utf-8"))
        logger.info(f"Parsed JSON: {json.dumps(json_data, indent=2)}")
    except Exception as e:
        logger.error(f"JSON Parse Error: {e}")

    logger.info("========================")

    return {"status": "received", "message": "Check server logs for request details"}


# Todo Routes
@app.post("/create_todo/")
def create_todo(request: VapiRequest, db: Session = Depends(get_db)):
    logger.debug("=== INCOMING REQUEST DEBUG ===")
    logger.debug(f"Request type: {type(request)}")
    logger.debug(f"Request content: {request}")
    if hasattr(request, "dict"):
        logger.debug(f"Request dict: {request.dict()}")
        logger.debug(
            f"Request JSON: {json.dumps(request.dict(), indent=2, default=str)}"
        )
    else:
        logger.debug(f"Request as string: {str(request)}")
    logger.debug("==============================")

    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "createTodo":
            args = tool_call.function.arguments
            break
    else:
        raise HTTPException(status_code=400, detail="Invalid Request")

    title = args.get("title", "")
    description = args.get("description", "")
    todo = Todo(title=title, description=description)

    db.add(todo)
    db.commit()
    db.refresh(todo)  # Optional

    return {"result": [{"toolCallId": tool_call.id, "result": "success"}]}


@app.post("/get_todos/")
def get_todos(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "getTodos":
            todos = db.query(Todo).all()
            return {
                "result": [
                    {
                        "toolCallId": tool_call.id,
                        "result": [
                            TodoResponse.from_orm(todo).dict() for todo in todos
                        ],
                    }
                ]
            }
    else:
        raise HTTPException(status_code=400, detail="Invalid Request")


@app.post("/complete_todo/")
def complete_todo(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "completeTodo":
            args = tool_call.function.arguments
            break
    else:
        raise HTTPException(status_code=400, detail="Invalid Request")

    todo_id = args.get("id")
    if not todo_id:
        raise HTTPException(status_code=400, detail="Missing To-Do Id")

    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    todo.completed = True

    db.commit()
    db.refresh(todo)  # Optional

    return {"result": [{"toolCallId": tool_call.id, "result": "success"}]}


@app.post("/delete_todo/")
def delete_todo(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "deleteTodo":
            args = tool_call.function.arguments
            break
    else:
        raise HTTPException(status_code=400, detail="Invalid Request")

    todo_id = args.get("id")
    if not todo_id:
        raise HTTPException(status_code=400, detail="Missing To-Do Id")

    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    db.delete(todo)
    db.commit()

    return {"result": [{"toolCallId": tool_call.id, "result": "success"}]}


# Remainder Routes
@app.post("/add_reminder/")
def add_reminder(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "addReminder":
            args = tool_call.function.arguments
            reminder_text = args.get("reminder_text")
            importance = args.get("importance")
            if not reminder_text or not importance:
                raise HTTPException(status_code=400, detail="Missing required fields")
            reminder = Reminder(reminder_text=reminder_text, importance=importance)
            db.add(reminder)
            db.commit()
            db.refresh(reminder)
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": ReminderResponse.from_orm(reminder).dict(),
                    }
                ]
            }
    raise HTTPException(status_code=400, detail="Invalid request")


@app.post("/get_reminders/")
def get_reminders(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "getReminders":
            reminders = db.query(Reminder).all()
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": [
                            ReminderResponse.from_orm(reminder).dict()
                            for reminder in reminders
                        ],
                    }
                ]
            }
    raise HTTPException(status_code=400, detail="Invalid request")


@app.post("/delete_reminder/")
def delete_reminder(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "deleteReminder":
            args = tool_call.function.arguments
            reminder_id = args.get("id")
            if not reminder_id:
                raise HTTPException(status_code=400, detail="Missing reminder ID")
            reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
            if not reminder:
                raise HTTPException(status_code=404, detail="Reminder not found")
            db.delete(reminder)
            db.commit()
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": {"id": reminder_id, "deleted": True},
                    }
                ]
            }
    raise HTTPException(status_code=400, detail="Invalid request")


# Calendar Event Routes
@app.post("/add_calendar_entry/")
def add_calendar_entry(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "addCalendarEntry":
            args = tool_call.function.arguments
            title = args.get("title", "")
            description = args.get("description", "")
            event_from_str = args.get("event_from", "")
            event_to_str = args.get("event_to", "")

            if not title or not event_from_str or not event_to_str:
                raise HTTPException(status_code=400, detail="Missing required fields")

            try:
                event_from = dt.datetime.fromisoformat(event_from_str)
                event_to = dt.datetime.fromisoformat(event_to_str)
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid date format. Use ISO format."
                )

            calendar_event = CalendarEvent(
                title=title,
                description=description,
                event_from=event_from,
                event_to=event_to,
            )
            db.add(calendar_event)
            db.commit()
            db.refresh(calendar_event)
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": CalendarEventResponse.from_orm(calendar_event).dict(),
                    }
                ]
            }
    raise HTTPException(status_code=400, detail="Invalid request")


@app.post("/get_calendar_entries/")
def get_calendar_entries(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "getCalendarEntries":
            events = db.query(CalendarEvent).all()
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": [
                            CalendarEventResponse.from_orm(event).dict()
                            for event in events
                        ],
                    }
                ]
            }
    raise HTTPException(status_code=400, detail="Invalid request")


@app.post("/delete_calendar_entry/")
def delete_calendar_entry(request: VapiRequest, db: Session = Depends(get_db)):
    for tool_call in request.message.toolCalls:
        if tool_call.function.name == "deleteCalendarEntry":
            args = tool_call.function.arguments
            event_id = args.get("id")
            if not event_id:
                raise HTTPException(status_code=400, detail="Missing event ID")
            event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
            if not event:
                raise HTTPException(status_code=404, detail="Calendar event not found")
            db.delete(event)
            db.commit()
            return {
                "results": [
                    {
                        "toolCallId": tool_call.id,
                        "result": {"id": event_id, "deleted": True},
                    }
                ]
            }
    raise HTTPException(status_code=400, detail="Invalid request")
