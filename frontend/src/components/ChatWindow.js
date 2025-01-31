import React from "react";

const ChatWindow = ({ messages }) => {
  return (
    <div className="ChatWindow">
      <h3>Chat Window</h3>
      {messages.length === 0 ? (
        <p>No messages yet...</p>
      ) : (
        messages.map((msg, index) => (
          <div key={index} className="ChatMessage">
            <strong>{msg.role}:</strong> <span>{msg.content}</span>
          </div>
        ))
      )}
    </div>
  );
};

export default ChatWindow;
