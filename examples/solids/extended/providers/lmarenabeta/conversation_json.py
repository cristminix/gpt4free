import json
import os


class ConversationJson:
    conversation_dir = "examples/logs/conversations/LMArenaBeta"
    id="new_id"
    contents={}
    loaded=False
    def __init__(self,id):
        self.id = id
        self.conversation_filename = f"{self.conversation_dir}/conversation_{self.id}.json"
        os.makedirs(self.conversation_dir, exist_ok=True)

     
    def get_conversation_filename(self):
        return self.conversation_filename

    def load(self):
        if os.path.exists(self.conversation_filename):
            with open(self.conversation_filename, 'r', encoding='utf-8') as f:
                self.contents = json.load(f)
                self.loaded=True
        return self.loaded
        
    def get(self, key):
        self.load()
        if key in self.contents:
            return self.contents[key]
        return None
    
    def set(self,key,value,commit=True):
        self.contents[key] = value
        if commit:
            self.commit()
    def get_or_set_default_config(self,evaluationSessionId,model_id,userMessageId,modelAMessageId):
        _evaluationSessionId = self.get("evaluationSessionId")
        _model_id = self.get("model_id")
        _userMessageId = self.get("userMessageId")
        _modelAMessageId = self.get("modelAMessageId")

        if not _evaluationSessionId:
            self.set("evaluationSessionId",evaluationSessionId)
            _evaluationSessionId = evaluationSessionId
        if not _model_id:
            self.set("model_id",model_id)
            _model_id = model_id
        if not _userMessageId:
            self.set("userMessageId",userMessageId)
            _userMessageId = userMessageId
        if not _modelAMessageId:
            self.set("modelAMessageId",modelAMessageId)
            _modelAMessageId = modelAMessageId
        return _evaluationSessionId,_model_id,_userMessageId,_modelAMessageId
    def attach_assistant_message(self,content):
        _lastMessage = self.get("lastMessage")
        _index =0 
        for message in _lastMessage:
            if message["id"] == self.get("modelAMessageId"):
                _lastMessage[_index]["content"] = content
            _lastMessage[_index]["status"]= "success"
            _index+=1
        
        self.set("messageHistory",_lastMessage)
            
    def commit(self):
        with open(self.conversation_filename, 'w', encoding='utf-8') as f:
            json.dump(self.contents, f, ensure_ascii=False, indent=2)
