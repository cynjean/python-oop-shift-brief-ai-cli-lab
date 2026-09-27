"""Reusable client for sending conversational prompts to Ollama."""

import ollama


class OllamaChatClient:
    """Manage one model's chat requests and successful conversation history."""

    def __init__(self, model_name="llama3.2"):
        self.model_name = model_name
        # Keep state on each instance so clients never share conversations.
        self.history = []

    @staticmethod
    def _assistant_content(response):
        """Read response content from either mappings or Ollama-style objects."""
        message = (
            response.get("message")
            if isinstance(response, dict)
            else getattr(response, "message", None)
        )
        if isinstance(message, dict):
            content = message.get("content")
        else:
            content = getattr(message, "content", None)

        if not isinstance(content, str) or not content.strip():
            raise ValueError("AI service returned no usable assistant content")
        return content.strip()

    def send(self, prompt):
        """Send a prompt and return usable assistant text, recording both turns."""
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        user_message = {"role": "user", "content": prompt.strip()}
        self.history.append(user_message)
        try:
            response = ollama.chat(model=self.model_name, messages=self.history)
            assistant_content = self._assistant_content(response)
        except Exception as error:
            # The failed turn must not damage earlier successful conversation state.
            if self.history and self.history[-1] is user_message:
                self.history.pop()
            raise RuntimeError(f"AI service request failed: {error}") from error

        self.history.append({"role": "assistant", "content": assistant_content})
        return assistant_content

    def reset(self):
        """Clear all stored conversation messages."""
        self.history.clear()

    def message_count(self):
        """Return the number of user and assistant messages in the transcript."""
        return len(self.history)

    def get_transcript(self):
        """Return copied message dictionaries so callers cannot mutate this history."""
        return [message.copy() for message in self.history]
