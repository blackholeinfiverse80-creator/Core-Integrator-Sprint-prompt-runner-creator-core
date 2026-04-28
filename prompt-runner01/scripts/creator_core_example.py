"""Example integration: generate instruction and send to Creator Core.

This script demonstrates a clean integration layer without modifying core
generation logic. It obtains an instruction from the Prompt Runner pipeline
and calls `send_to_creator_core()` to request a blueprint.
"""

from platform_adapter import PlatformAdapter
from creator_core_client import send_to_creator_core


def main():
    adapter = PlatformAdapter()
    # generate instruction (Prompt Runner remains the instruction generator)
    result = adapter.process("Design the database schema for a scalable web application.")
    instruction = result.get("instruction")

    if not instruction:
        print({"status": "error", "message": "Failed to generate instruction"})
        return

    # send to Creator Core (integration layer)
    blueprint = send_to_creator_core(instruction)
    print(blueprint)


if __name__ == "__main__":
    main()
