import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  IconButton,
  Typography,
  Avatar,
  Chip,
  Divider,
  CircularProgress,
  Card,
  CardContent,
  Button,
  Grid,
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Lightbulb as TipIcon,
  TrendingUp as TrendingIcon,
  Security as SecurityIcon,
  AccountBalance as BankIcon,
} from '@mui/icons-material';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

import { sendChatMessage } from '../services/chat';

const ChatInterface = ({ userProfile }) => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: `Hello! I'm your AI superannuation advisor. I'm here to help you make informed decisions about your retirement investments. 

${userProfile ? `I can see you're ${userProfile.age} years old with ${userProfile.retirement_age_goal - userProfile.age} years until retirement. ` : ''}

What would you like to know about your superannuation strategy?`,
      timestamp: new Date(),
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const suggestedQuestions = [
    {
      icon: <TrendingIcon />,
      text: "What's the best investment strategy for my age?",
      category: "Strategy"
    },
    {
      icon: <SecurityIcon />,
      text: "How should I balance risk and return?",
      category: "Risk"
    },
    {
      icon: <BankIcon />,
      text: "Should I make additional contributions?",
      category: "Contributions"
    },
    {
      icon: <TipIcon />,
      text: "What are the key things to consider for retirement planning?",
      category: "Planning"
    }
  ];

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (messageText = null) => {
    const messageContent = messageText || inputMessage.trim();
    
    if (!messageContent) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: messageContent,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage(messageContent, userProfile, messages);
      
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: response.response,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Failed to send message. Please try again.');
      
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: "I apologize, but I'm experiencing technical difficulties. Please try again or contact support if the issue persists.",
        timestamp: new Date(),
        isError: true,
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSendMessage();
    }
  };

  const formatMessageContent = (content) => {
    // Simple formatting for bot messages
    const lines = content.split('\n');
    return lines.map((line, index) => {
      if (line.startsWith('**') && line.endsWith('**')) {
        // Bold text
        return (
          <Typography key={index} variant="subtitle2" fontWeight="bold" gutterBottom>
            {line.slice(2, -2)}
          </Typography>
        );
      } else if (line.startsWith('• ')) {
        // Bullet points
        return (
          <Typography key={index} variant="body2" sx={{ ml: 2, mb: 0.5 }}>
            {line}
          </Typography>
        );
      } else if (line.trim()) {
        // Regular text
        return (
          <Typography key={index} variant="body2" paragraph>
            {line}
          </Typography>
        );
      }
      return <br key={index} />;
    });
  };

  return (
    <Box sx={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        AI Investment Advisor
      </Typography>
      
      {userProfile && (
        <Card sx={{ mb: 2, bgcolor: 'primary.50' }}>
          <CardContent>
            <Typography variant="subtitle2" color="primary">
              Your Profile: {userProfile.age} years old • ${userProfile.annual_income?.toLocaleString()} income • 
              {userProfile.retirement_age_goal - userProfile.age} years to retirement • 
              {userProfile.risk_tolerance} risk tolerance
            </Typography>
          </CardContent>
        </Card>
      )}

      <Paper 
        sx={{ 
          flexGrow: 1, 
          display: 'flex', 
          flexDirection: 'column',
          mb: 2,
          maxHeight: 'calc(100vh - 300px)'
        }}
      >
        {/* Messages Area */}
        <Box
          sx={{
            flexGrow: 1,
            overflowY: 'auto',
            p: 2,
            bgcolor: 'grey.50'
          }}
        >
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    mb: 2,
                    justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  {message.type === 'bot' && (
                    <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                      <BotIcon />
                    </Avatar>
                  )}
                  
                  <Paper
                    sx={{
                      p: 2,
                      maxWidth: '70%',
                      bgcolor: message.type === 'user' 
                        ? 'primary.main' 
                        : message.isError 
                          ? 'error.light'
                          : 'white',
                      color: message.type === 'user' ? 'white' : 'text.primary',
                    }}
                  >
                    {message.type === 'bot' ? 
                      formatMessageContent(message.content) :
                      <Typography variant="body2">{message.content}</Typography>
                    }
                    <Typography variant="caption" sx={{ opacity: 0.7, display: 'block', mt: 1 }}>
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                  </Paper>

                  {message.type === 'user' && (
                    <Avatar sx={{ ml: 1, bgcolor: 'secondary.main' }}>
                      <PersonIcon />
                    </Avatar>
                  )}
                </Box>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                <BotIcon />
              </Avatar>
              <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography variant="body2">Thinking...</Typography>
              </Paper>
            </Box>
          )}

          <div ref={messagesEndRef} />
        </Box>

        <Divider />

        {/* Suggested Questions */}
        {messages.length <= 1 && (
          <Box sx={{ p: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Suggested Questions:
            </Typography>
            <Grid container spacing={1}>
              {suggestedQuestions.map((question, index) => (
                <Grid item xs={12} sm={6} key={index}>
                  <Button
                    variant="outlined"
                    size="small"
                    startIcon={question.icon}
                    onClick={() => handleSendMessage(question.text)}
                    sx={{ 
                      justifyContent: 'flex-start',
                      textAlign: 'left',
                      width: '100%',
                      textTransform: 'none'
                    }}
                  >
                    {question.text}
                  </Button>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}

        {/* Input Area */}
        <Box sx={{ p: 2, bgcolor: 'white' }}>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <TextField
              fullWidth
              multiline
              maxRows={4}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about your superannuation strategy, investment options, risk management, or any other retirement planning questions..."
              disabled={isLoading}
              variant="outlined"
              size="small"
            />
            <IconButton
              onClick={() => handleSendMessage()}
              disabled={!inputMessage.trim() || isLoading}
              color="primary"
              sx={{ 
                bgcolor: 'primary.main',
                color: 'white',
                '&:hover': { bgcolor: 'primary.dark' },
                '&:disabled': { bgcolor: 'grey.300' }
              }}
            >
              <SendIcon />
            </IconButton>
          </Box>
          
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
            Press Enter to send, Shift+Enter for new line
          </Typography>
        </Box>
      </Paper>

      {/* Disclaimer */}
      <Paper sx={{ p: 2, bgcolor: 'warning.50' }}>
        <Typography variant="caption" color="text.secondary">
          <strong>Important:</strong> This AI assistant provides general information only and should not be considered as personal financial advice. 
          Please consult with a qualified financial advisor for advice tailored to your specific circumstances.
        </Typography>
      </Paper>
    </Box>
  );
};

export default ChatInterface;