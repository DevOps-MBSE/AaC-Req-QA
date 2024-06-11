from unittest import TestCase
from typing import Tuple

import os
import shutil
import tempfile

from click.testing import CliRunner

from aac.context.language_context import LanguageContext
from aac.execute.command_line import cli, initialize_cli
from aac_req_qa.req_qa_impl import shall_statement_quality

# Thanks to sfc-gh-jcarroll
# openai test mock taken from:  https://github.com/openai/openai-python/issues/715#issuecomment-1809203346
import datetime
from unittest.mock import patch

from openai.types.chat import ChatCompletionMessage
from openai.types.chat.chat_completion import ChatCompletion, Choice
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk, ChoiceDelta
from openai.types.chat.chat_completion_chunk import Choice as StreamChoice


def create_chat_completion(response: str, role: str = "assistant") -> ChatCompletion:
    """
    Create a chat completion object with the given response and role.
    
    Args:
        response (str): The response content.
        role (str, optional): The role of the chat completion. Defaults to "assistant".
    
    Returns:
        ChatCompletion: The created chat completion object.
    """
    return ChatCompletion(
        id="foo",
        model="test-mock",
        object="chat.completion",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content=response,
                    role=role,
                ),
            )
        ],
        created=int(datetime.datetime.now().timestamp()),
    )


def create_stream_chat_completion(response: str, role: str = "assistant"):
    """
    Create a stream chat completion object with the given response and role.
    
    Args:
        response (str): The response content.
        role (str, optional): The role of the chat completion. Defaults to "assistant".
    
    Yields:
        ChatCompletionChunk: The created chat completion chunk object.
    """
    for token in response:
        yield ChatCompletionChunk(
            id="foo",
            model="gpt-3.5-turbo",
            object="chat.completion.chunk",
            choices=[
                StreamChoice(
                    index=0,
                    finish_reason=None,
                    delta=ChoiceDelta(
                        content=token,
                        role=role,
                    )
                ),
            ],
            created=int(datetime.datetime.now().timestamp()),
        )


EXCELLENT_RESPONSE = """
This is a mocked test result for an Excellent shall statement.

REQUIREMENT QUALITY SCORE: A (Excellent)
"""

MEDIUM_RESPONSE = """
This is a mocked test result for a Medium shall statement.

REQUIREMENT QUALITY SCORE: C (Medium)
"""


class TestReqQA(TestCase):

    orig_aac_ai_url = ""
    orig_aac_ai_key = ""
    orig_aac_ai_model = ""

    def setUp(self):

        self.orig_aac_ai_url = os.environ.get("AAC_AI_URL")
        self.orig_aac_ai_key = os.environ.get("AAC_AI_KEY")
        self.orig_aac_ai_model = os.environ.get("AAC_AI_MODEL")
        os.environ["AAC_AI_URL"] = "https://localhost:12345/v1"
        os.environ["AAC_AI_KEY"] = "not-a-real-key"
        os.environ["AAC_AI_MODEL"] = "not-a-model"

    def tearDown(self):
        
        if self.orig_aac_ai_url is not None:
            os.environ["AAC_AI_URL"] = self.orig_aac_ai_url
        if self.orig_aac_ai_key is not None:
            os.environ["AAC_AI_KEY"] = self.orig_aac_ai_key
        if self.orig_aac_ai_model is not None:
            os.environ["AAC_AI_MODEL"] = self.orig_aac_ai_model

    def test_eval_req(self):

        # Let's just test via CLI for now.
        pass

    def run_eval_req_cli_command_with_args(self, args: list[str]) -> Tuple[int, str]:
        """Utility function to invoke the CLI command with the given arguments."""
        initialize_cli()
        runner = CliRunner()
        result = runner.invoke(cli, ["eval-req"] + args)
        exit_code = result.exit_code
        std_out = str(result.stdout)
        output_message = std_out.strip().replace("\x1b[0m", "")
        return exit_code, output_message

    @patch("openai.resources.chat.Completions.create")
    def test_cli_eval_req(self, openai_create):

        openai_create.return_value = create_chat_completion(EXCELLENT_RESPONSE)

        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "good_reqs.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            args = [temp_aac_file_path]
            exit_code, output_message = self.run_eval_req_cli_command_with_args(args)
        
            self.assertEqual(0, exit_code, f"Expected success but failed with message: {output_message}")  # asserts the command ran successfully

    @patch("openai.resources.chat.Completions.create")
    def test_cli_eval_req_failure(self, openai_create):

        openai_create.return_value = create_chat_completion(MEDIUM_RESPONSE)

        with tempfile.TemporaryDirectory() as temp_dir:
            aac_file_path = os.path.join(os.path.dirname(__file__), "bad_reqs.aac")
            temp_aac_file_path = os.path.join(temp_dir, "my_plugin.aac")
            shutil.copy(aac_file_path, temp_aac_file_path)

            args = [temp_aac_file_path]
            exit_code, output_message = self.run_eval_req_cli_command_with_args(args)
        
            self.assertNotEqual(0, exit_code)

    def test_shall_statement_quality_no_req(self):

        context = LanguageContext()
        schema_definition = context.get_definitions_by_name("aac.lang.Schema")
        if len(schema_definition) != 1:
            self.fail("Expected to find one and only one Schema definition")
        schema_definition = schema_definition[0]
        definitions = context.parse_and_load(root_schema)
        result = shall_statement_quality(definitions[0].instance, definitions[0], schema_definition.instance)
        self.assertTrue(result.is_success())

    def test_shall_statement_quality_no_env_vars(self):

        os.environ["AAC_AI_URL"] = ""
        os.environ["AAC_AI_KEY"] = ""
        os.environ["AAC_AI_MODEL"] = ""

        context = LanguageContext()
        requirement_definition = context.get_definitions_by_name("aac.lang.Requirement")
        if len(requirement_definition) != 1:
            self.fail("Expected to find one and only one Requirement definition")
        requirement_definition = requirement_definition[0]
        definitions = context.parse_and_load(req_schema)
        result = shall_statement_quality(definitions[0].instance, definitions[0], requirement_definition.instance)
        self.assertFalse(result.is_success())

    @patch("openai.resources.chat.Completions.create")
    def test_shall_statement_quality(self, openai_create):

        openai_create.return_value = create_chat_completion(EXCELLENT_RESPONSE)

        context = LanguageContext()
        requirement_definition = context.get_definitions_by_name("aac.lang.Requirement")
        if len(requirement_definition) != 1:
            self.fail("Expected to find one and only one Requirement definition")
        requirement_definition = requirement_definition[0]
        definitions = context.parse_and_load(req_schema)
        result = shall_statement_quality(definitions[0].instance, definitions[0], requirement_definition.instance)
        self.assertTrue(result.is_success())

    @patch("openai.resources.chat.Completions.create")
    def test_shall_statement_quality_failure(self, openai_create):

        openai_create.return_value = create_chat_completion(MEDIUM_RESPONSE)

        context = LanguageContext()
        requirement_definition = context.get_definitions_by_name("aac.lang.Requirement")
        if len(requirement_definition) != 1:
            self.fail("Expected to find one and only one Requirement definition")
        requirement_definition = requirement_definition[0]
        definitions = context.parse_and_load(req_schema)
        result = shall_statement_quality(definitions[0].instance, definitions[0], requirement_definition.instance)
        self.assertFalse(result.is_success())


root_schema = """
schema:
  name: TestSchema
  package: test_aac_req_qa.plugins.req_qa
  fields:
    - name: name
      type: string
    - name: test_field
      type: string
"""

req_schema = """
req:
  name: Test Requirement
  id: REQ_TEST_01
  shall:  The req qa shall evaluate the quality of the requirement.
"""
