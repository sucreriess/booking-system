from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts.
    Demonstrates async WebSocket handling and connection lifecycle management.
    """
    
    def __init__(self):
        """Initialize connection manager with empty connection list."""
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept and register a new WebSocket connection.
        
        Args:
            websocket: WebSocket connection to register
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection from active connections.
        
        Args:
            websocket: WebSocket connection to remove
        """
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """
        Send a message to a specific WebSocket connection.
        
        Args:
            message: Message to send
            websocket: Target WebSocket connection
        """
        await websocket.send_text(message)
    
    async def broadcast(self, message: str) -> None:
        """
        Broadcast a message to all connected clients.
        
        Args:
            message: Message to broadcast
        """
        # Iterate over a copy to avoid modification during iteration
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                # Remove failed connection
                if connection in self.active_connections:
                    self.active_connections.remove(connection)
    
    async def broadcast_appointment_event(
        self,
        event_type: str,
        appointment_data: Dict[str, Any]
    ) -> None:
        """
        Broadcast appointment-related events to all connected clients.
        
        Args:
            event_type: Type of event (booked, updated, cancelled)
            appointment_data: Appointment details
        """
        message = json.dumps({
            "event": event_type,
            "data": appointment_data
        })
        
        await self.broadcast(message)
        logger.info(f"Broadcasted {event_type} event to {len(self.active_connections)} clients")


# Global connection manager instance
manager = ConnectionManager()


@router.websocket("/ws/appointments")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time appointment updates.
    
    Clients connect to this endpoint to receive real-time notifications about:
    - New appointments booked
    - Appointment updates
    - Appointment cancellations
    
    Args:
        websocket: WebSocket connection
    """
    await manager.connect(websocket)
    
    try:
        # Send welcome message
        await manager.send_personal_message(
            json.dumps({
                "event": "connected",
                "message": "Successfully connected to appointment updates"
            }),
            websocket
        )
        
        # Keep connection alive and listen for messages
        while True:
            # Receive messages from client (optional ping/pong)
            data = await websocket.receive_text()
            
            # Echo back for testing purposes
            await manager.send_personal_message(
                json.dumps({
                    "event": "echo",
                    "data": data
                }),
                websocket
            )
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)