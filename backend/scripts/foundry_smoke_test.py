"""
Microsoft Foundry Connectivity Preflight Smoke Test (Phase B4A).
Completely isolated from application routing, ManagerAgent, specialist agents, and frontend.
Validates environment configuration, Azure CLI authentication, and Agent Framework Foundry invocation.
"""

import os
import sys
import time
import asyncio
from pathlib import Path
from typing import Dict, Any

# Pre-load local environment from backend/.env if available

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.is_file():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv()
except ImportError:
    pass


async def run_smoke_test() -> Dict[str, Any]:
    """
    Executes an isolated preflight connectivity verification to Microsoft Foundry.
    Uses the exact AzureCliCredential instance for both token acquisition and FoundryChatClient.
    """
    # 1. Configuration check from environment
    endpoint = os.environ.get("FOUNDRY_PROJECT_ENDPOINT", "").strip()
    model = os.environ.get("FOUNDRY_MODEL", "").strip()

    if not endpoint:
        return {
            "status": "error",
            "code": "FOUNDRY_ENDPOINT_MISSING",
            "message": "FOUNDRY_PROJECT_ENDPOINT is not configured.",
            "remediation": "Set FOUNDRY_PROJECT_ENDPOINT in backend/.env to the team Microsoft Foundry project endpoint."
        }

    if not model:
        return {
            "status": "error",
            "code": "MODEL_DEPLOYMENT_MISSING",
            "message": "FOUNDRY_MODEL is not configured.",
            "remediation": "Set FOUNDRY_MODEL in backend/.env to the deployed model deployment name (e.g. gpt-5-mini)."
        }

    # 2. Azure identity token acquisition preflight
    from azure.identity import AzureCliCredential, CredentialUnavailableError
    from azure.core.exceptions import ClientAuthenticationError

    credential = AzureCliCredential()

    try:
        # Perform actual token acquisition against Azure AI scope
        _ = credential.get_token("https://ai.azure.com/.default")
    except CredentialUnavailableError as exc:
        err_msg = str(exc)
        if "not found" in err_msg.lower():
            return {
                "status": "error",
                "code": "AZURE_CLI_NOT_AVAILABLE",
                "message": "Azure CLI ('az') executable was not found on PATH.",
                "remediation": "Install Azure CLI from https://aka.ms/installazurecliwindows or run 'winget install -e --id Microsoft.AzureCLI'."
            }
        return {
            "status": "error",
            "code": "AZURE_NOT_LOGGED_IN",
            "message": "Azure CLI is installed, but no active login session was found.",
            "remediation": "Run 'az login' with your authorized team account in your shell."
        }
    except ClientAuthenticationError as exc:
        return {
            "status": "error",
            "code": "AUTHENTICATION_FAILED",
            "message": f"Azure authentication failed: {exc}",
            "remediation": "Re-authenticate using 'az login'."
        }
    except Exception as exc:
        return {
            "status": "error",
            "code": "AUTHENTICATION_FAILED",
            "message": f"Unexpected authentication error: {exc}",
            "remediation": "Check your Azure CLI configuration and run 'az login'."
        }

    # 3. Microsoft Agent Framework FoundryChatClient & Agent invocation
    try:
        from agent_framework import Agent
        from agent_framework.foundry import FoundryChatClient

        # Reuse the exact verified AzureCliCredential instance
        client = FoundryChatClient(
            project_endpoint=endpoint,
            model=model,
            credential=credential,
        )

        agent = Agent(
            client=client,
            name="NexusConnectivityAgent",
            instructions=(
                "You are a connectivity-test agent for Nexus. "
                "Respond briefly and do not use tools."
            ),
        )

        test_prompt = "Reply with the text NEXUS_FOUNDRY_OK and nothing else."
        t0 = time.perf_counter()
        response = await agent.run(test_prompt)
        elapsed = time.perf_counter() - t0

        response_text = getattr(response, "text", str(response)).strip()

        return {
            "status": "success",
            "code": "OK",
            "authentication_succeeded": True,
            "project_connection": True,
            "deployment": model,
            "response_text": response_text,
            "elapsed_seconds": round(elapsed, 2)
        }

    except Exception as e:
        elapsed = time.perf_counter() - t0 if 't0' in locals() else 0.0
        err_msg = str(e)
        err_lower = err_msg.lower()

        if "401" in err_msg or "403" in err_msg or "unauthorized" in err_lower or "forbidden" in err_lower or "accessdenied" in err_lower:
            code = "AUTHORIZATION_FAILED"
        elif "project" in err_lower and ("not found" in err_lower or "404" in err_msg):
            code = "PROJECT_NOT_FOUND"
        elif "deployment" in err_lower and ("not found" in err_lower or "404" in err_msg or "model" in err_lower):
            code = "MODEL_NOT_FOUND"
        elif "429" in err_msg or "rate limit" in err_lower or "quota" in err_lower:
            code = "QUOTA_OR_RATE_LIMIT"
        elif "connection" in err_lower or "timeout" in err_lower or "dns" in err_lower or "unreachable" in err_lower:
            code = "NETWORK_ERROR"
        else:
            code = "MODEL_INVOCATION_ERROR"

        return {
            "status": "error",
            "code": code,
            "message": f"Foundry model invocation failed: {code}.",
            "deployment": model,
            "elapsed_seconds": round(elapsed, 2),
            "remediation": "Verify that the endpoint, model deployment, and Azure permissions are valid."
        }


def main():
    print("==================================================")
    print("Nexus — Microsoft Foundry Connectivity Preflight")
    print("==================================================")

    res = asyncio.run(run_smoke_test())

    if res.get("status") == "success":
        print("Authentication:     OK")
        print("Project connection: OK")
        print(f"Deployment:         {res.get('deployment')}")
        print(f"Response:           {res.get('response_text')}")
        print(f"Elapsed time:       {res.get('elapsed_seconds')}s")
        print("==================================================")
        print("NEXUS FOUNDRY PREFLIGHT OK")
        print("==================================================")
        sys.exit(0)
    else:
        print("Authentication:     FAILED" if "AUTH" in res.get("code", "") else "Authentication:     OK")
        print(f"Status:             {res.get('status').upper()}")
        print(f"Error Code:         {res.get('code')}")
        print(f"Failure Reason:     {res.get('message')}")
        print(f"Remediation:        {res.get('remediation')}")
        print("==================================================")
        sys.exit(1)


if __name__ == "__main__":
    main()
