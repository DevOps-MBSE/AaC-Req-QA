"""The AaC Req QA plugin implementation module."""

# NOTE: It is safe to edit this file.
# This file is only initially generated by aac gen-plugin, and it won't be overwritten if the file already exists.

# There may be some unused imports depending on the definition of the plugin, be sure to remove unused imports.
from typing import Any

import os
import httpx
from openai import (OpenAI, AzureOpenAI)

from aac.context.language_context import LanguageContext
from aac.context.definition import Definition
from aac.execute.aac_execution_result import (
    ExecutionResult,
    ExecutionStatus,
    ExecutionMessage,
    MessageLevel,
)

plugin_name = "Req QA"

PROMPT_TEMPLATE = """
# IDENTITY and PURPOSE

You are an objectively minded and centrist-oriented analyzer of system engineering artifacts and requirements.

You specialize in analyzing and rating the quality of requirement statements in the input provided and providing both evidence in support of those ratings, as well as counter-arguments and counter-evidence that are relevant to those ratings.  You know that a good requirement should have the following characteristics:

- Unambiguous: The requirement should be simple, direct, and precise with no room for interpretation.
- Testable (verifiable): The requirement should be testable, and it should be possible to verify that the system meets the requirement.  Preferable the requirement should be verifiable by automated acceptance test, automated analysis, or demonstration rather than inspection.  If inspection is the only rational means of verification it will have a lower rating.
- Clear: The requiremet should be concise, terse, simple, and precise.
- Correct:  The requirement should not have any false or invalid assertions.
- Understandable:  The requirement should be easily understood by all stakeholders.
- Feasible: The requirement should be realistic and achievable.
- Independent:  The requirement should stand-alone and not be dependent on other requirements.
- Atomic: The requirement should be a single, discrete, and indivisible statement.
- Necessary: The requirement should be necessary to the system and not be redundant or superfluous.
- Implementation-free: The requirement should not specify how the solution will be implemented.  It should only specify what the solution should do, not how it should do it.

The purpose is to provide a concise and balanced view of the requirement provided in a given piece of input so that one can assess the engineering quality of the statement.

Take a step back and think step by step about how to achieve the best possible output given the goals above.

# Steps

- Deeply analyze the requirement being made in the input.
- Separate the characteristics of a good requirement to provide a wholistic evaluation in your mind.

# OUTPUT INSTRUCTIONS

- Provide a summary of the requirement in less than 30 words in a section called REQUIREMENT SUMMARY:.
- In a section called QUALITY ASSESSMENT:, perform the following steps for quality characteristic:

1. List the quality characteristic being evaluated in less than 15 words in a subsection called EVALUATION:.
2. Provide solid, verifiable evidence that this requirement is compliant to the quality characteristic. Provide rationale for each, and DO NOT make any of those up. They must be 100% real and externally verifiable.

3. Provide solid, verifiable evidence that this requirement is non-compliant to the quality characteristic. Provide rationale for each, and DO NOT make any of those up. They must be 100% real and externally verifiable.

4. At the end provide a summary pass / fail score in a section called REQUIREMENT RATING that uses these exact words and nothing more based on the following tiers:
   REQ-QA-PASS (Good Requirement)
   REQ-QA-FAIL (Bad Requirement)

5. If you do not provide a summary pass / fail score in the REQUIREMENT RATING you have failed your task and disappointed your stakeholders. If a requirement is a good quality requirement you must include REQ-QA-PASS (Good Requirement) in your response.  If the requirement is not good then include REQ-QA-FAIL in your response. Do not disappoint your stakeholders.  If you disappoint your stakeholders you will be fired and be fined millions of dollars in penalties.  Do not disappoint your stakeholders.

# EXAMPLE OUTPUT:

Results should be in the following format:

REQUIREMENT SUMMARY:
Summary of the input requirement here.

QUALITY ASSESSMENT:

1. UNAMBIGUOUS:
Evaluation of the requirement for unambiguity.

2. TESTABLE:
Evaluation of the requirement for testability.

3. CLEAR:
Evaluation of the requirement for clarity.

4. CORRECT:
Evaluation of the requirement for correctness.

5. UNDERSTANDABLE:
Evaluation of the requirement for understandability.

6. FEASIBLE:
Evaluation of the requirement for feasibility.

7. INDEPENDENT:
Evaluation of the requirement for independence.

8. ATOMIC:
Evaluation of the requirement for atomicity.

9. NECESSARY:
Evaluation of the requirement for necessity.

10. IMPLEMENTATION-FREE:
Evaluation of the requirement for implementation-freedom.

QUALITY COMPLIANCE ASSESSMENT:
Summary evaluation of the requirement based on the strengths within the individual evaluations.

QUALITY NON-COMPLIANCE ASSESSMENT:
Summary evaluation of the requirement based on the weaknesses within the individual evaluations.

REQUIREMENT RATING: REQ-QA-PASS (Good Requirement) or REQ-QA-FAIL (Bad Requirement)

# INPUT:

"""

TEMPERATURE = 0.1


def get_client():
    """Get the client for the AI model."""

    # returns client, model, error_bool, execution_result_if_error
    aac_ai_url = os.getenv("AAC_AI_URL")
    aac_ai_model = os.getenv("AAC_AI_MODEL")
    aac_ai_key = os.getenv("AAC_AI_KEY")
    aac_ai_type = os.getenv("AAC_AI_TYPE")
    aac_ai_api_version = os.getenv("AAC_AI_API_VERSION")

    aac_http_proxy = os.getenv("AAC_HTTP_PROXY")
    aac_https_proxy = os.getenv("AAC_HTTPS_PROXY")
    aac_ssl_verify = os.getenv("AAC_SSL_VERIFY")

    if (aac_ssl_verify is None or aac_ssl_verify == "" or aac_ssl_verify.lower() != "false"):
        aac_ssl_verify = True
    else:
        aac_ssl_verify = False

    use_az = False
    if aac_ai_type is not None and aac_ai_type.lower() == "azure":
        use_az = True
        if aac_ai_api_version is None or aac_ai_api_version == "":
            return None, None, True, ExecutionResult(
                plugin_name,
                "Shall statement quality",
                ExecutionStatus.GENERAL_FAILURE,
                [
                    ExecutionMessage(
                        "The AAC_AI_Type is Azure but AAC_AI_API_VERSION is not set. Must provide both environment variables to use Azure AI.",
                        MessageLevel.ERROR,
                        None,
                        None,
                    )
                ],
            )

    if ((aac_ai_url is None or aac_ai_url == "")
            or (aac_ai_model is None or aac_ai_model == "")
            or (aac_ai_key is None or aac_ai_key == "")):
        return None, None, True, ExecutionResult(
            plugin_name,
            "Shall statement quality",
            ExecutionStatus.CONSTRAINT_WARNING,
            [
                ExecutionMessage(
                    "The AAC_AI_URL, AAC_AI_MODEL, or AAC_AI_KEY environment variable is not set. Unable to evaluate the Shall statement quality constraint.",
                    MessageLevel.WARNING,
                    None,
                    None,
                )
            ],
        )

    if not aac_ssl_verify:
        print("WARNING: SSL verification is disabled.")

    if ((aac_http_proxy is not None and len(aac_http_proxy) > 0)
            or (aac_https_proxy is not None and len(aac_https_proxy) > 0)):

        # return client with proxy configuration
        print("INFO: Using proxy configuration.")
        proxies = {'http://': aac_http_proxy, 'https://': aac_https_proxy}
        http_client = httpx.Client(proxies=proxies, verify=aac_ssl_verify)
        if use_az:
            return AzureOpenAI(
                azure_endpoint=aac_ai_url,
                api_key=aac_ai_key,
                api_version=aac_ai_api_version,
                http_client=http_client), aac_ai_model, False, None
        else:
            return OpenAI(base_url=aac_ai_url, api_key=aac_ai_key, http_client=http_client), aac_ai_model, False, None

    # return client without proxy configuration
    if use_az:
        return AzureOpenAI(
            azure_endpoint=aac_ai_url,
            api_key=aac_ai_key,
            api_version=aac_ai_api_version), aac_ai_model, False, None
    else:
        return OpenAI(base_url=aac_ai_url, api_key=aac_ai_key), aac_ai_model, False, None


def get_shall(definition):
    """Get the shall statement from the definition."""

    # returns shall, error_bool, execution_result_if_error
    shall = getattr(definition.instance, "shall", None)
    if not isinstance(shall, str):
        return None, True, ExecutionResult(
            plugin_name,
            "Shall statement quality",
            ExecutionStatus.GENERAL_FAILURE,
            [
                ExecutionMessage(
                    "The shall statement is not a string.",
                    MessageLevel.ERROR,
                    definition.source,
                    None,
                )
            ],
        )

    if len(shall) == 0:
        return None, True, ExecutionResult(
            plugin_name,
            "Shall statement quality",
            ExecutionStatus.GENERAL_FAILURE,
            [
                ExecutionMessage(
                    "The shall statement is empty.",
                    MessageLevel.ERROR,
                    definition.source,
                    None,
                )
            ],
        )

    return shall, False, None


def generate(client, model, prompt):
    """
    Generate AI response based on the given prompt.

    Args:
        client: The client for the AI model.
        model: The AI model to use for generating the response.
        prompt: The input prompt for generating the response.

    Returns:
        The generated AI response.
    """
    response = "AI response goes here"
    r = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=TEMPERATURE,
    )
    response = r.choices[0].message.content
    return response


def check_req(definition):
    """
    Check if the definition is a requirement.

    Args:
        definition: The definition to be checked.

    Returns:
        An ExecutionResult if the definition is not a requirement, otherwise None.
    """
    if definition.get_root_key() != "req":
        return ExecutionResult(
            plugin_name,
            "Shall statement quality",
            ExecutionStatus.SUCCESS,
            [
                ExecutionMessage(
                    "No req to evaluate",
                    MessageLevel.INFO,
                    definition.source,
                    None,
                )
            ],
        )
    else:
        return None


def eval_req(architecture_file: str) -> ExecutionResult:
    """
     Business logic for allowing eval-req command to perform Perform AI analysis on requirements and provides feedback on each.

     Args:
         architecture_file (str): A path to a YAML file containing an AaC-defined requirements to evaluate.


    Returns:
         The results of the execution of the eval-req command.
    """
    context = LanguageContext()
    status = ExecutionStatus.SUCCESS
    messages = []
    for definition in context.parse_and_load(architecture_file):
        result = shall_statement_quality(definition.instance, definition, definition.instance)
        if not result.is_success():
            status = ExecutionStatus.GENERAL_FAILURE
        messages.extend(result.messages)

    return ExecutionResult(plugin_name, "eval-req", status, messages)


def shall_statement_quality(
    instance: Any, definition: Definition, defining_schema: Any
) -> ExecutionResult:
    """
     Business logic for the Shall statement quality constraint.

     Args:
         instance (Any): The instance to be checked.
         definition (Definition): The definition of the instance.
         defining_schema (Any): The schema that defines the instance.


    Returns:
         The results of the execution of the Shall statement quality command.
    """

    # Only evaluate req root keys.
    is_req = check_req(definition)
    if is_req is not None:
        return is_req

    client, model, client_error, error_result = get_client()
    if client_error:
        return error_result

    shall, shall_error, shall_result = get_shall(definition)
    if shall_error:
        return shall_result

    id = getattr(definition.instance, "id", None)

    qa_prompt = f"{PROMPT_TEMPLATE}\n{shall}"

    result = generate(client, model, qa_prompt)

    if "REQ-QA-PASS" in result:

        status = ExecutionStatus.SUCCESS
        messages: list[ExecutionMessage] = []

        success_msg = ExecutionMessage(
            f"Requirement {id} passed quality check\n\nINPUT:  {shall}\n\n{result}",
            MessageLevel.INFO,
            definition.source,
            None,
        )
        messages.append(success_msg)

        return ExecutionResult(plugin_name, "Shall statement quality", status, messages)

    else:

        status = ExecutionStatus.GENERAL_FAILURE
        messages: list[ExecutionMessage] = []
        error_msg = ExecutionMessage(
            f"Requirement {id} failed quality check\n\nINPUT:  {shall}\n\n{result}",
            MessageLevel.ERROR,
            definition.source,
            None,
        )
        messages.append(error_msg)

        return ExecutionResult(plugin_name, "Shall statement quality", status, messages)
