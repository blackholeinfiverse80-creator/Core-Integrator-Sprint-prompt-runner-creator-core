import sys

sys.path.append(r"C:/Users/pc44/Desktop/prompt-runner01")

import api
from fastapi import HTTPException


class MockLLM:
    available = True

    def generate_instruction(self, prompt):
        return {
            "prompt": prompt,
            "module": "education",
            "intent": "explain_concept",
            "topic": "newton_law",
            "tasks": ["a"],
            "output_format": "step_by_step_guide",
            "product_context": "creator_core",
        }


api._get_llm = lambda: MockLLM()
api.send_to_creator_core = lambda instruction: {
    "status": "error",
    "message": "Creator Core request failed",
}

try:
    api.run_prompt(api.RunRequest(prompt="Explain newton law"))
    print("unexpected success")
except HTTPException as exc:
    print(f"status={exc.status_code} detail={exc.detail}")
