"""Interactive CLI for creating and revising shift handoff briefs."""

try:  # Support both `python -m lib.shift_cli` and direct script execution.
    from .ai_client import OllamaChatClient
    from .brief_builder import HandoffBriefBuilder
except ImportError:  # pragma: no cover - exercised by direct script execution
    from ai_client import OllamaChatClient
    from brief_builder import HandoffBriefBuilder


class ShiftBriefCLI:
    """Handle terminal commands and display responses from the brief builder."""

    def __init__(self, ai_client, brief_builder=None):
        self.ai_client = ai_client
        self.brief_builder = (
            brief_builder if brief_builder is not None else HandoffBriefBuilder()
        )
        self.running = True

    def command_help(self):
        """Return guidance for all supported commands."""
        return (
            "Commands:\n"
            "- brief <shift notes>  Create a new shift handoff brief.\n"
            "- revise <feedback>    Revise the previous brief.\n"
            "- history              Show the conversation message count.\n"
            "- reset                Clear conversation history.\n"
            "- help                 Show this command list.\n"
            "- exit or quit         Stop the program."
        )

    def display_welcome(self):
        """Print the welcome heading and command guidance."""
        print("Shift Handoff Brief CLI")
        print("Create and revise AI-assisted shift handoff briefs.\n")
        print(self.command_help())

    def handle_command(self, raw_input):
        """Validate and route a command, converting expected failures to messages."""
        if not isinstance(raw_input, str) or not raw_input.strip():
            return "Input Error: Enter a command. Type 'help' to see available commands."

        parts = raw_input.strip().split(maxsplit=1)
        command = parts[0].lower()
        payload = parts[1].strip() if len(parts) > 1 else ""

        if command == "help":
            return self.command_help()
        if command == "history":
            return f"Conversation messages: {self.ai_client.message_count()}"
        if command == "reset":
            self.ai_client.reset()
            return "Conversation history reset."
        if command in {"exit", "quit"}:
            self.running = False
            return "Goodbye!"

        if command == "brief":
            if not payload:
                return "Input Error: Please provide shift notes after 'brief'."
            try:
                return self.brief_builder.create_brief(self.ai_client, payload)
            except ValueError as error:
                return f"Input Error: {error}"
            except RuntimeError as error:
                return f"Service Error: {error}"

        if command == "revise":
            if not payload:
                return "Input Error: Please provide revision feedback after 'revise'."
            try:
                return self.brief_builder.revise_brief(self.ai_client, payload)
            except ValueError as error:
                return f"Input Error: {error}"
            except RuntimeError as error:
                return f"Service Error: {error}"

        return (
            f"Input Error: Unknown command '{command}'. "
            "Type 'help' to see available commands."
        )

    def run(self):
        """Display the CLI and handle commands until exit or end-of-input."""
        self.display_welcome()
        while self.running:
            try:
                raw_input = input("> ")
            except EOFError:
                self.running = False
                print("Goodbye!")
                break
            except KeyboardInterrupt:
                self.running = False
                print("\nGoodbye!")
                break

            result = self.handle_command(raw_input)
            if result:
                print(result)


def main():
    """Create the default AI client and start the interactive application."""
    client = OllamaChatClient(model_name="llama3.2")
    app = ShiftBriefCLI(client)
    app.run()


if __name__ == "__main__":
    main()
