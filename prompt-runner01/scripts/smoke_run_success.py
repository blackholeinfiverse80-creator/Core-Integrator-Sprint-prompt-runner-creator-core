import sys

sys.path.append(r"C:/Users/pc44/Desktop/prompt-runner01")

import api


class MockLLM:
    available = True

    def generate_instruction(self, prompt):
        return {
            "prompt": prompt,
            "module": "education",
            "intent": "explain_concept",
            "topic": "newton_law",
            "tasks": ["define_newton_law", "describe_first_law"],
            "output_format": "step_by_step_guide",
            "product_context": "creator_core",
        }


api._get_llm = lambda: MockLLM()

result = api.run_prompt(api.RunRequest(prompt="Explain newton law"))
print(result)
