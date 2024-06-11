"""__init__.py module for the Req QA plugin."""

# WARNING - DO NOT EDIT - YOUR CHANGES WILL NOT BE PROTECTED.
# This file is auto-generated by the aac gen-plugin and may be overwritten.

from os.path import join, dirname
from typing import Any

from aac.context.definition import Definition
from aac.context.language_context import LanguageContext
from aac.execute import hookimpl
from aac.execute.aac_execution_result import ExecutionResult, ExecutionStatus
from aac.execute.plugin_runner import PluginRunner

from aac_req_qa.req_qa_impl import plugin_name, eval_req
from aac_req_qa.req_qa_impl import shall_statement_quality


req_qa_aac_file_name = "req_qa.aac"


def run_eval_req(architecture_file: str) -> ExecutionResult:
    """
     Perform AI analysis on requirements and provides feedback on each.

     Args:
         architecture_file (str): A path to a YAML file containing an AaC-defined requirements to evaluate.


    Returns:
         The results of the execution of the plugin eval-req command.
    """

    result = ExecutionResult(plugin_name, "eval-req", ExecutionStatus.SUCCESS, [])

    eval_req_result = eval_req(architecture_file)
    if not eval_req_result.is_success():
        return eval_req_result
    else:
        result.add_messages(eval_req_result.messages)

    return result


def run_shall_statement_quality(
    instance: Any, definition: Definition, defining_schema: Any, arguments: Any
) -> ExecutionResult:
    """
    Check requirement shall statement to ensure it meets good system engineering quality standards.

    Args:
        instance (Any): The instance to be checked.
        definition (Definition): The definition of the instance.
        defining_schema (Any): The schema that defines the instance.
        arguments (Any): The arguments to be used in the constraint.

    Returns:
        The results of the execution of the plugin schema constraint.
    """

    return shall_statement_quality(instance, definition, defining_schema)


@hookimpl
def register_plugin() -> None:
    """Registers information about the plugin for use in the CLI."""

    active_context = LanguageContext()
    req_qa_aac_file = join(dirname(__file__), req_qa_aac_file_name)
    definitions = active_context.parse_and_load(req_qa_aac_file)

    req_qa_plugin_definition = [
        definition for definition in definitions if definition.name == plugin_name
    ][0]

    plugin_instance = req_qa_plugin_definition.instance
    for file_to_load in plugin_instance.definition_sources:
        active_context.parse_and_load(file_to_load)

    plugin_runner = PluginRunner(plugin_definition=req_qa_plugin_definition)
    plugin_runner.add_command_callback("eval-req", run_eval_req)

    plugin_runner.add_constraint_callback(
        "Shall statement quality", run_shall_statement_quality
    )

    active_context.register_plugin_runner(plugin_runner)
