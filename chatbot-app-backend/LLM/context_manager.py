import json
import mysql.connector
from typing import List, Dict, Any, Optional
from datetime import datetime

class ContextManager:
    """
    Manages global context window for chat conversations with database persistence
    """
    
    def __init__(self, db_config: dict):
        self.db_config = db_config
    
    def get_db_connection(self):
        """Get database connection"""
        return mysql.connector.connect(**self.db_config)
    
    def load_context(self, username: str, max_messages: int = 20) -> List[Dict[str, Any]]:
        """
        Load conversation context from database
        
        Args:
            username: User identifier
            max_messages: Maximum number of messages to load (default: 20)
            
        Returns:
            List of message dictionaries in OpenAI format
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT context FROM chat_history WHERE username = %s", (username,))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not row or not row["context"]:
                return []
            
            # Parse JSON context
            context = row["context"] if isinstance(row["context"], list) else json.loads(row["context"])
            
            # Return last N messages to manage token limits
            return context[-max_messages:] if len(context) > max_messages else context
            
        except Exception as e:
            print(f"Error loading context for {username}: {e}")
            return []
    
    def save_context(self, username: str, context: List[Dict[str, Any]]) -> bool:
        """
        Save conversation context to database
        
        Args:
            username: User identifier
            context: List of message dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        import traceback
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            context_json = json.dumps(context)
            print(f"[save_context] Username: {username}, Context length: {len(context)}")
            cursor.execute("SELECT username FROM chat_history WHERE username = %s", (username,))
            exists = cursor.fetchone()
            print(f"[save_context] User exists: {exists}")
            if exists:
                sql = "UPDATE chat_history SET context = %s WHERE username = %s"
                print(f"[save_context] SQL: {sql}, params: ({context_json}, {username})")
                cursor.execute(sql, (context_json, username))
                print(f"[save_context] Updated context for user: {username}")
            else:
                sql = "INSERT INTO chat_history (username, context) VALUES (%s, %s)"
                # print(f"[save_context] SQL: {sql}, params: ({username}, {context_json})")
                cursor.execute(sql, (username, context_json))
                print(f"[save_context] Inserted new context for user: {username}")
            conn.commit()
            print(f"[save_context] Commit successful for user: {username}")
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving context for {username}: {e}")
            traceback.print_exc()
            return False
    
    def add_message(self, username: str, role: str, content: str, max_context_size: int = 50) -> bool:
        """
        Add a new message to the conversation context.
        When context exceeds 20 messages, keeps first 10 and last 10 messages.
        
        Args:
            username: User identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            max_context_size: Maximum number of messages to keep (legacy param, now uses 20)
            
        Returns:
            True if successful, False otherwise
        """
        import traceback
        try:
            print(f"[add_message] Adding message for user: {username}, role: {role}")
            context = self.load_context(username, 1000)  # Load all messages first
            print(f"[add_message] Loaded context length: {len(context)}")
            
            new_message = {
                "role": role,
                "content": content
            }
            print(f"[add_message] New message: {new_message}")
            context.append(new_message)
            
            # If context exceeds 20 messages, keep first 10 + last 10
            if len(context) > 20:
                print(f"[add_message] Context too long ({len(context)}), applying first 10 + last 10 strategy")
                first_10 = context[:10]
                last_10 = context[-10:]
                context = first_10 + last_10
                print(f"[add_message] Context reduced to {len(context)} messages (first 10 + last 10)")
            
            print(f"[add_message] Final context length: {len(context)}")
            result = self.save_context(username, context)
            print(f"[add_message] Save context result: {result}")
            return result
        except Exception as e:
            print(f"Error adding message for {username}: {e}")
            traceback.print_exc()
            return False
    
    def clear_context(self, username: str) -> bool:
        """
        Clear conversation context for a user
        
        Args:
            username: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE chat_history SET context = %s WHERE username = %s",
                ('[]', username)
            )
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error clearing context for {username}: {e}")
            return False
    
    def get_context_for_llm(self, username: str, max_messages: int = 10) -> List[Dict[str, str]]:
        """
        Get context formatted for LLM consumption (without timestamps)
        
        Args:
            username: User identifier
            max_messages: Maximum number of messages to include
            
        Returns:
            List of messages in OpenAI format (role, content only)
        """
        try:
            context = self.load_context(username, max_messages)
            
            # Remove timestamps and keep only role/content for LLM
            llm_context = []
            for msg in context:
                llm_context.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            return llm_context
            
        except Exception as e:
            print(f"Error formatting context for LLM: {e}")
            return []