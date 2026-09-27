"""Shift handoff prompt construction and response validation."""


class HandoffBriefBuilder:
    """Build prompts and verify output for shift handoff briefs."""

    REQUIRED_SECTIONS = (
        "Shift Summary:",
        "Open Issues:",
        "Action Items:",
        "Follow-Up Questions:",
        "Risk Notes:",
    )

    def build_brief_prompt(self, notes):
        """Create a structured handoff prompt from the manager's shift notes."""
        if not isinstance(notes, str) or not notes.strip():
            raise ValueError("Shift notes cannot be empty")

        sections = "\n".join(self.REQUIRED_SECTIONS)
        return (
            "Create a concise shift handoff brief from the notes below. "
            "Use only details supported by the notes; do not invent unsupported details. "
            'Use "Unknown" when a detail is not provided. Keep the following sections '
            f"and labels exactly:\n{sections}\n\n"
            f"Shift notes:\n{notes.strip()}"
        )

    def build_revision_prompt(self, feedback):
        """Ask for a revision that uses the prior conversation and supplied feedback."""
        if not isinstance(feedback, str) or not feedback.strip():
            raise ValueError("Revision feedback cannot be empty")

        sections = "\n".join(self.REQUIRED_SECTIONS)
        return (
            "Revise the previous shift handoff brief using the manager's feedback. "
            "Use the previous brief and earlier conversation as context. Preserve facts, "
            "do not invent unsupported details, and use \"Unknown\" when details are "
            f"not provided. Keep these sections and labels exactly:\n{sections}\n\n"
            f"Revision feedback:\n{feedback.strip()}"
        )

    def is_usable_brief(self, response_text):
        """Return whether a nonblank response contains every required section."""
        return isinstance(response_text, str) and bool(response_text.strip()) and all(
            section in response_text for section in self.REQUIRED_SECTIONS
        )

    def format_brief(self, response_text):
        """Add a readable heading while preserving the model's response content."""
        return f"\nShift Handoff Brief\n\n{response_text.strip()}"

    def create_brief(self, ai_client, notes):
        """Build, send, validate, and format a new shift handoff brief."""
        prompt = self.build_brief_prompt(notes)
        response = ai_client.send(prompt)
        if not self.is_usable_brief(response):
            raise RuntimeError("AI response did not include required sections")
        return self.format_brief(response)

    def revise_brief(self, ai_client, feedback):
        """Build, send, validate, and format a revision to the previous brief."""
        prompt = self.build_revision_prompt(feedback)
        response = ai_client.send(prompt)
        if not self.is_usable_brief(response):
            raise RuntimeError("AI response did not include required sections")
        return f"\nRevised Shift Handoff Brief\n\n{response.strip()}"
