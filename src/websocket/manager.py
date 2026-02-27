"""WebSocket connection manager for real-time updates."""
from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """Manage WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.user_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str | None = None):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.add(websocket)
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str | None = None):
        """Remove WebSocket connection."""
        self.active_connections.discard(websocket)
        
        if user_id and user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        dead_connections = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)
        
        # Clean up dead connections
        for connection in dead_connections:
            self.active_connections.discard(connection)
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to specific user."""
        if user_id not in self.user_connections:
            return
        
        dead_connections = set()
        
        for connection in self.user_connections[user_id]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_connections.add(connection)
        
        # Clean up
        for connection in dead_connections:
            self.user_connections[user_id].discard(connection)


# Global instance
manager = ConnectionManager()


async def notify_ticket_status(ticket_id: str, status: str, external_id: str | None = None):
    """Notify all clients of ticket status change."""
    await manager.broadcast({
        "event": "ticket:status_changed",
        "data": {
            "ticket_id": ticket_id,
            "status": status,
            "external_platform_id": external_id,
        }
    })


async def notify_deployment_started(ticket_id: str, task_id: str):
    """Notify deployment started."""
    await manager.broadcast({
        "event": "deployment:started",
        "data": {
            "ticket_id": ticket_id,
            "task_id": task_id,
        }
    })


async def notify_deployment_completed(ticket_id: str, external_id: str):
    """Notify deployment completed."""
    await manager.broadcast({
        "event": "deployment:completed",
        "data": {
            "ticket_id": ticket_id,
            "external_platform_id": external_id,
        }
    })


async def notify_deployment_failed(ticket_id: str, error: str):
    """Notify deployment failed."""
    await manager.broadcast({
        "event": "deployment:failed",
        "data": {
            "ticket_id": ticket_id,
            "error": error,
        }
    })
