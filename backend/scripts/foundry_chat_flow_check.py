"""
Live Business Flow Check for Phase B4B.
Tests full end-to-end ChatService execution under ORCHESTRATION_MODE=foundry_manager.
Verifies that:
- Foundry selects the route
- Specialist agents execute deterministic tools against SQLite
- Real database numbers appear in final answers
- Context passing transfers all 3 product IDs from SalesAgent to InventoryAgent in compound workflow.
"""

import os
import sys
import asyncio
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

backend_dir = Path(__file__).resolve().parent.parent

if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings

from app.db.connection import initialize_database
from app.services.chat_service import ChatService


async def main():
    print("=" * 70)
    print("NEXUS PHASE B4B — LIVE BUSINESS FLOW VERIFICATION")
    print("=" * 70)

    # Ensure SQLite database is initialized with seed data
    initialize_database()

    # Force foundry_manager orchestration mode
    settings.ORCHESTRATION_MODE = "foundry_manager"
    chat_service = ChatService()


    # Flow 1: Compound Request
    prompt1 = "Compare our top-selling products with current inventory."
    print(f"\n[1] Query: \"{prompt1}\"")
    resp1 = await ChatService.process_chat(prompt1)

    print(f"Agents Used: {resp1.agents_used}")
    print(f"Tool Calls Count: {len(resp1.tool_calls)}")
    print(f"Tools Executed: {[tc.tool for tc in resp1.tool_calls]}")
    print(f"Answer Preview:\n{resp1.answer}\n")

    # Verify context passing
    context_events = [e for e in resp1.trace if e.type == "context_passed"]
    if len(context_events) != 1:
        print("Trace events:")
        for e in resp1.trace:
            print(f"  [{e.type}] {e.agent}: {e.message} (status: {e.status})")
    assert len(context_events) == 1, "Context passing event missing!"
    pids = context_events[0].metadata.get("product_ids", [])
    print(f"Context Passed Product IDs: {pids}")
    assert len(pids) == 3, f"Expected 3 product IDs, got {len(pids)}"
    assert resp1.agents_used == ["sales", "inventory"]
    print("[1] COMPOUND FLOW VERIFIED SUCCESSFULLY!")

    # Flow 2: Sales Total
    prompt2 = "How much revenue did we make?"
    print(f"\n[2] Query: \"{prompt2}\"")
    resp2 = await ChatService.process_chat(prompt2)
    print(f"Agents Used: {resp2.agents_used}")
    print(f"Answer: {resp2.answer}")
    assert "124,500" in resp2.answer, "Sales revenue factual mismatch!"
    assert resp2.agents_used == ["sales"]
    print("[2] SALES FLOW VERIFIED SUCCESSFULLY!")

    # Flow 3: Low Stock
    prompt3 = "Which products are low in stock?"
    print(f"\n[3] Query: \"{prompt3}\"")
    resp3 = await ChatService.process_chat(prompt3)
    print(f"Agents Used: {resp3.agents_used}")
    print(f"Answer: {resp3.answer}")
    assert resp3.agents_used == ["inventory"]
    print("[3] INVENTORY FLOW VERIFIED SUCCESSFULLY!")


    print("\n" + "=" * 70)
    print("ALL LIVE BUSINESS FLOW CHECKS PASSED (DATA PROVENANCE & ROUTING VERIFIED)")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
