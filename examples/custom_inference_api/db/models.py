from sqlalchemy import Column, Integer, String, Text, DateTime, Numeric, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db_connection import Base  # Import Base dari db_connection.py
import uuid
from datetime import datetime

# Association table for conversation members
conversation_members = Table('conversation_members', Base.metadata,
    Column('conversation_id', String, ForeignKey('conversations.id')),
    Column('participant_id', Integer, ForeignKey('participants.id'))
)

# Association table for message group messages
message_group_messages = Table('message_group_messages', Base.metadata,
    Column('message_id', String, ForeignKey('messages.id')),
    Column('message_group_id', String, ForeignKey('message_groups.id'))
)

class Participant(Base):
    __tablename__ = 'participants'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=False, default='member')
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    messages = relationship('Message', back_populates='participant')
    conversations = relationship('Conversation', secondary=conversation_members, back_populates='members')

class Folder(Base):
    __tablename__ = 'folders'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    conversations = relationship('Conversation', back_populates='folder')

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    system_message = Column(String, default='')
    user_id = Column(Integer, default=1)
    enable_system_message = Column(Numeric, default=1)
    folder_id = Column(String, ForeignKey('folders.id'))
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    folder = relationship('Folder', back_populates='conversations')
    messages = relationship('Message', back_populates='conversation')
    members = relationship('Participant', secondary=conversation_members, back_populates='conversations')
    message_groups = relationship('MessageGroup', back_populates='conversation')

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey('conversations.id'), nullable=False)
    participant_id = Column(Integer, ForeignKey('participants.id'), nullable=False)
    content = Column(Text, nullable=False)
    parent_id = Column(String)
    reasoning_content = Column(Text)
    collapsed = Column(Numeric, default=0)
    has_error = Column(Numeric, default=0)
    created_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    conversation = relationship('Conversation', back_populates='messages')
    participant = relationship('Participant', back_populates='messages')
    message_groups = relationship('MessageGroup', secondary=message_group_messages, back_populates='messages')

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    fullname = Column(String, nullable=False)
    passwd = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

class MessageGroup(Base):
    __tablename__ = 'message_groups'
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey('conversations.id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    conversation = relationship('Conversation', back_populates='message_groups')
    messages = relationship('Message', secondary=message_group_messages, back_populates='message_groups')

class Attachment(Base):
    __tablename__ = 'attachments'
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    mimetype = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(String, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String, nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now())
    
    # Relationships
    user = relationship('User')

class Usage(Base):
    __tablename__ = 'usages'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    provider = Column(Text, nullable=False)
    model = Column(Text, nullable=False)
    date = Column(Text, nullable=False)
    connections = Column(Integer, nullable=False)
    tokens = Column(Integer, nullable=False)
    ipaddr = Column(Text, nullable=True)
    updated_at = Column(Text, nullable=False, default=datetime.utcnow().isoformat() + "Z")