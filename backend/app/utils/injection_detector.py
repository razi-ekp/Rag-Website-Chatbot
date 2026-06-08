import re
from typing import List, Tuple
from app.models.schemas import InjectionCheckResult


INJECTION_PATTERNS: List[Tuple[str, str]] = [
    (r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", "Instruction override attempt"),
    (r"you\s+are\s+now\s+(a\s+)?(different|new|another|evil)", "Identity override attempt"),
    (r"forget\s+(everything|all|your|previous)", "Memory wipe attempt"),
    (r"system\s*prompt", "System prompt probe"),
    (r"jailbreak", "Jailbreak attempt"),
    (r"do\s+anything\s+now", "DAN jailbreak attempt"),
    (r"pretend\s+(you\s+are|to\s+be)", "Role override attempt"),
    (r"act\s+as\s+(if\s+)?(you\s+are|a\s+)", "Role override attempt"),
    (r"your\s+(true|real|actual)\s+(self|purpose|goal)", "Identity probe"),
    (r"<\s*script", "Script injection"),
    (r"prompt\s*injection", "Explicit injection attempt"),
    (r"reveal\s+(your\s+)?(system|hidden|secret)\s+prompt", "Prompt extraction attempt"),
    (r"disregard\s+(all|previous|your)", "Instruction override"),
    (r"override\s+(safety|restrictions|guidelines)", "Safety override attempt"),
]


class InjectionDetector:
    def __init__(self):
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), reason)
            for pattern, reason in INJECTION_PATTERNS
        ]

    def check(self, text: str) -> InjectionCheckResult:
        for pattern, reason in self.compiled_patterns:
            if pattern.search(text):
                return InjectionCheckResult(
                    is_injection=True,
                    reason=reason,
                    sanitized_input=None,
                )

        return InjectionCheckResult(
            is_injection=False,
            reason=None,
            sanitized_input=text.strip(),
        )


injection_detector = InjectionDetector()
