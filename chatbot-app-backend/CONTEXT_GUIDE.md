# Global Context Window Implementation Guide

## Overview
The global context window system automatically saves and retrieves conversation history from the MySQL database using the `chat_history` table's JSON `context` field.

## Database Schema (from tales.sql)
```sql
CREATE TABLE chat_history(
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    context JSON,
    CONSTRAINT fk_users FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);
```

## Key Components

### 1. ContextManager Class (`LLM/context_manager.py`)
- **Purpose**: Handles all database operations for conversation context
- **Key Methods**:
  - `load_context(username, max_messages)`: Load conversation history from DB
  - `save_context(username, context)`: Save conversation history to DB
  - `add_message(username, role, content)`: Add new message to context
  - `clear_context(username)`: Clear all conversation history
  - `get_context_for_llm(username)`: Get formatted context for LLM consumption

### 2. Enhanced LLM Functions
- **LLM1 & LLM2**: Updated to accept `username` parameter
- **Auto-save**: Automatically saves user and assistant messages to database
- **Context loading**: Retrieves last 10 messages for conversation continuity

### 3. API Endpoints

#### Chat with Context
```
POST /chat
{
    "message": "Hello, how are you?",
    "userData": {...},
    "username": "user123"
}
```

#### Get Chat History
```
GET /api/chat-history/{username}
Returns: {"context": [...]}
```

#### Clear Chat History
```
DELETE /api/chat-history/{username}
Returns: {"status": "success", "message": "Chat history cleared"}
```

#### Get Context Statistics
```
GET /api/context-stats/{username}
Returns: {
    "username": "user123",
    "total_messages": 10,
    "user_messages": 5,
    "assistant_messages": 5,
    "context_available": true
}
```

## How It Works

### 1. **Message Flow**
```
User sends message → API receives → Context loaded from DB → 
LLM processes with context → Response generated → 
Both user message and response saved to DB
```

### 2. **Context Management**
- **Automatic**: Messages are automatically saved when `username` is provided
- **Persistent**: Context survives server restarts
- **Limited**: Only last N messages kept to manage token limits
- **Per-user**: Each user has separate conversation context

### 3. **Token Management**
- **LLM calls**: Limited to last 10 messages
- **Database storage**: Can store up to 50 messages (configurable)
- **Automatic trimming**: Older messages removed when limit exceeded

## Usage Examples

### Frontend Integration
```javascript
// Send chat message with username
const response = await fetch('/chat', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        message: "What's my retirement plan status?",
        userData: userProfileData,
        username: "john_doe"
    })
});
```

### Clear conversation history
```javascript
const response = await fetch('/api/chat-history/john_doe', {
    method: 'DELETE'
});
```

### Get conversation statistics
```javascript
const stats = await fetch('/api/context-stats/john_doe');
const data = await stats.json();
console.log(`Total messages: ${data.total_messages}`);
```

## Configuration

### Database Connection
Update these values in `context_manager.py` and API endpoints:
```python
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Manoj@123",  # Update this
    "database": "UserData"
}
```

### Context Limits
- **max_messages** (LLM): 10 messages (default)
- **max_context_size** (Database): 50 messages (default)
- Adjust these values in the ContextManager methods

## Benefits

1. **Persistence**: Conversations continue across sessions
2. **Scalability**: Each user has separate context
3. **Memory efficient**: Old messages automatically pruned
4. **Easy integration**: Simple API with automatic context management
5. **Debugging**: Context statistics and management endpoints

## Migration from In-Memory

The system maintains backward compatibility:
- If `username` is not provided, falls back to in-memory `conversation_history`
- No changes needed for existing API calls without username
- Gradual migration possible by adding username to frontend calls

## Troubleshooting

1. **Database connection issues**: Check MySQL credentials in db_config
2. **Context not loading**: Verify user exists in `users` table (foreign key constraint)
3. **Token limits**: Reduce `max_messages` parameter if hitting LLM token limits
4. **Performance**: Consider indexing on username column for large datasets