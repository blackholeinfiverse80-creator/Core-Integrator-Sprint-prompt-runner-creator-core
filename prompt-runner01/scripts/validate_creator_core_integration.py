"""Validation script for Prompt Runner → Creator Core integration.

Performs:
- instruction shape validation
- send_to_creator_core existence and header/URL check
- full pipeline test (generate instruction + send)
- multi-domain and determinism checks

"""

import sys
import json
from typing import Any, Dict

# ensure repo root on path
sys.path.append(r"C:/Users/pc44/Desktop/prompt-runner01")

from creator_core_client import send_to_creator_core, CREATOR_CORE_URL
from llm_adapter import LLMAdapter
from platform_adapter import PlatformAdapter


def has_required_keys(instr: Dict[str, Any]) -> bool:
    required = ["prompt", "module", "intent", "topic", "tasks", "output_format", "product_context"]
    for k in required:
        if k not in instr:
            return False
        if instr[k] is None:
            return False
    # tasks must be list of strings
    if not isinstance(instr.get("tasks"), list):
        return False
    if not all(isinstance(t, str) for t in instr.get("tasks", [])):
        return False
    if instr.get("product_context") != "creator_core":
        return False
    return True


def generate_instruction(prompt: str) -> Dict[str, Any]:
    # prefer LLMAdapter if available, else PlatformAdapter
    llm = LLMAdapter()
    try:
        if llm.available:
            return llm.generate_instruction(prompt)
    except Exception:
        pass
    # fallback to platform adapter
    pa = PlatformAdapter()
    res = pa.process(prompt)
    instr = res.get("instruction")
    # if PlatformAdapter returns run-style instruction with nested data.topic, try to transform
    if instr and "data" in instr and "topic" in instr["data"]:
        flat = {
            "prompt": prompt,
            "module": instr.get("module"),
            "intent": instr.get("intent"),
            "topic": instr.get("data", {}).get("topic"),
            "tasks": instr.get("tasks"),
            "output_format": instr.get("output_format"),
            "product_context": instr.get("product_context") if instr.get("product_context") else "creator_core",
        }
        return flat
    return instr or {}


def check_send_function():
    ok = callable(send_to_creator_core)
    print("send_to_creator_core exists:", ok)
    print("CREATOR_CORE_URL:", CREATOR_CORE_URL)


def full_flow_test(prompt: str):
    print('\n--- Full flow test:', prompt)
    instr = generate_instruction(prompt)
    print('Instruction keys:', list(instr.keys()))
    valid = has_required_keys(instr)
    print('Instruction valid shape:', valid)
    resp = send_to_creator_core(instr)
    print('Creator Core response:', resp)
    return instr, resp


def multi_domain_test(prompts):
    results = []
    for p in prompts:
        instr = generate_instruction(p)
        results.append((p, instr))
        print(f"Prompt: {p}\n  keys: {list(instr.keys())}\n  topic: {instr.get('topic')}\n  tasks: {instr.get('tasks')}\n")
    # ensure different instructions
    distinct = len({json.dumps(r[1], sort_keys=True) for r in results}) == len(results)
    print('Multi-domain produced distinct instructions:', distinct)
    return results


def determinism_test(prompt: str):
    a = generate_instruction(prompt)
    b = generate_instruction(prompt)
    same = json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    print('Determinism for prompt:', same)
    return same


def main():
    check_send_function()

    # Step 4: Full pipeline
    instr, resp = full_flow_test("Explain Newton's laws of motion")

    # Step 6: Multi-domain
    prompts = [
        "Explain Newton's laws",
        "Calculate tax for 18 lakh",
        "Design customer support workflow",
    ]
    multi_domain_test(prompts)

    # Step 7: Determinism
    determinism_test("Explain Newton's laws of motion")


if __name__ == '__main__':
    main()
