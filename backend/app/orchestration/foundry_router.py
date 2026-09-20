"""
Foundry Manager Router for Phase B4B.
Uses Microsoft Agent Framework and Microsoft Foundry (gpt-5-mini)
to classify user requests into server-approved Nexus intents via structured output.
Does NOT call tools, execute specialists, or generate business answers.
"""

import os
import time
import asyncio
from typing import Optional, Dict, Any, Tuple

from azure.identity import AzureCliCredential, CredentialUnavailableError
from azure.core.exceptions import ClientAuthenticationError
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient


from ..core.config import settings
from ..agents.types import ExecutionPlan
from .intent import NexusIntent, FoundryRoutingDecision, build_execution_plan


class FoundryRoutingError(Exception):
    """Encapsulates categorized routing failures from Microsoft Foundry."""
    def __init__(self, category: str, message: str):
        super().__init__(message)
        self.category = category
        self.message = message


class FoundryManagerRouter:
    """
    Classifies user queries into validated Nexus intents using Microsoft Foundry.
    Follows strict lifecycle rules: client is reused across async calls on the event loop;
    isolated Agent and run state are created per routing request.
    """

    ROUTER_INSTRUCTIONS = (
        "You are the Nexus Manager routing agent.\n"
        "Your only responsibility is to classify the user's request into the provided Nexus routing schema.\n"
        "Nexus supports business requests concerning sales, inventory, HR, business overview, "
        "and the explicitly supported compound workflows.\n\n"
        "Do not answer the business question.\n"
        "Do not invent business data.\n"
        "Do not calculate revenue.\n"
        "Do not invent stock levels.\n"
        "Do not invent employee information.\n"
        "Do not use outside knowledge.\n"
        "Do not use web search.\n"
        "Do not call tools.\n"
        "Do not generate SQL.\n"
        "Do not generate Python.\n"
        "Do not select arbitrary functions.\n\n"
        "Return only a valid structured routing decision.\n"
        "If the request is outside the supported Nexus capabilities, select the unsupported intent."
    )

    def __init__(
        self,
        client: Optional[FoundryChatClient] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None
    ):
        self.model_name = model or settings.FOUNDRY_MODEL or "gpt-5-mini"
        self.timeout_seconds = (
            timeout_seconds
            if timeout_seconds is not None
            else getattr(settings, "FOUNDRY_ROUTING_TIMEOUT_SECONDS", 15.0)
        )

        if client is not None:
            self._client = client
        else:
            endpoint = settings.FOUNDRY_PROJECT_ENDPOINT
            if not endpoint:
                raise FoundryRoutingError(
                    "FOUNDRY_ENDPOINT_MISSING",
                    "FOUNDRY_PROJECT_ENDPOINT is not configured."
                )
            credential = AzureCliCredential()
            self._client = FoundryChatClient(
                project_endpoint=endpoint,
                model=self.model_name,
                credential=credential
            )

    async def route(self, query: str) -> Tuple[ExecutionPlan, Dict[str, Any]]:
        """
        Invokes Microsoft Foundry to classify the query into a structured FoundryRoutingDecision.
        Constructs and returns the trusted server-side ExecutionPlan and audit metadata.
        """
        agent = Agent(
            client=self._client,
            name="NexusManagerRouter",
            instructions=self.ROUTER_INSTRUCTIONS
        )

        t0 = time.perf_counter()
        try:
            # Enforce bounded timeout on model invocation
            response = await asyncio.wait_for(
                agent.run(query, options={"response_format": FoundryRoutingDecision}),
                timeout=self.timeout_seconds
            )
            elapsed = time.perf_counter() - t0

            # Structured Output Validation
            decision = getattr(response, "value", None)
            if not isinstance(decision, FoundryRoutingDecision):
                raise FoundryRoutingError(
                    "INVALID_STRUCTURED_OUTPUT",
                    f"Model response did not contain a valid FoundryRoutingDecision (got {type(decision)})."
                )

            # Build server-side trusted execution plan
            plan = build_execution_plan(
                intent=decision.intent,
                query=query,
                decision=decision,
                policy_name=decision.policy_name
            )


            metadata = {
                "routing_source": "foundry",
                "model": self.model_name,
                "intent": decision.intent.value,
                "elapsed_seconds": round(elapsed, 2)
            }

            return plan, metadata

        except asyncio.TimeoutError:
            elapsed = time.perf_counter() - t0
            raise FoundryRoutingError(
                "TIMEOUT",
                f"Foundry routing timed out after {self.timeout_seconds}s."
            )

        except FoundryRoutingError:
            raise

        except CredentialUnavailableError as exc:
            raise FoundryRoutingError(
                "AUTHENTICATION_FAILED",
                f"Azure CLI credentials unavailable: {exc}"
            )

        except ClientAuthenticationError as exc:
            raise FoundryRoutingError(
                "AUTHENTICATION_FAILED",
                f"Azure authentication failed: {exc}"
            )

        except Exception as exc:
            elapsed = time.perf_counter() - t0
            err_msg = str(exc)
            err_lower = err_msg.lower()

            if "401" in err_msg or "403" in err_msg or "unauthorized" in err_lower or "forbidden" in err_lower:
                category = "AUTHORIZATION_FAILED"
            elif "404" in err_msg or "not found" in err_lower:
                category = "PROJECT_OR_MODEL_NOT_FOUND"
            elif "429" in err_msg or "rate limit" in err_lower or "quota" in err_lower:
                category = "QUOTA_OR_RATE_LIMIT"
            elif "connection" in err_lower or "timeout" in err_lower or "dns" in err_lower:
                category = "NETWORK_ERROR"
            else:
                category = "MODEL_ROUTING_ERROR"

            raise FoundryRoutingError(category, f"Foundry routing failed ({category}): {err_msg}")


# Singleton client/router caching for application lifecycle
_foundry_router_instance: Optional[FoundryManagerRouter] = None


def get_foundry_router() -> FoundryManagerRouter:
    """Provides a singleton FoundryManagerRouter instance reusing the FoundryChatClient."""
    global _foundry_router_instance
    if _foundry_router_instance is None:
        _foundry_router_instance = FoundryManagerRouter()
    return _foundry_router_instance


def reset_foundry_router():
    """Resets the cached router instance (used in tests/config switching)."""
    global _foundry_router_instance
    _foundry_router_instance = None
