from collections import defaultdict


MAX_MESSAGES = 10


class ConversationManager:

    def __init__(self):

        self.sessions = defaultdict(list)

    def add_message(
        self,
        session_id,
        role,
        content
    ):

        self.sessions[session_id].append(
            {
                "role": role,
                "content": content
            }
        )

        # Keep only latest messages
        self.sessions[session_id] = (
            self.sessions[session_id]
            [-MAX_MESSAGES:]
        )

    def get_messages(
        self,
        session_id
    ):

        return self.sessions.get(
            session_id,
            []
        )

    def clear(
        self,
        session_id
    ):

        if session_id in self.sessions:

            del self.sessions[
                session_id
            ]


conversation_manager = ConversationManager()