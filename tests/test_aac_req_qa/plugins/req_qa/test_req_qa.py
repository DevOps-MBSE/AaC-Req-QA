from click.testing import CliRunner
from typing import Tuple
from unittest import TestCase

from aac.execute.aac_execution_result import ExecutionStatus
from aac.execute.command_line import cli, initialize_cli


from aac_req_qa.plugins.req_qa.req_qa_impl import plugin_name
from aac_req_qa.plugins.req_qa.req_qa_impl import shall_statement_quality


class TestReqQA(TestCase):

    def test_shall_statement_quality_no_req(self):

        # TODO: Write test for non req root key
        self.fail("Test not yet implemented.")

    def test_shall_statement_quality(self):

        # TODO: Write success test for shall_statement_quality
        self.fail("Test not yet implemented.")

    def test_shall_statement_quality_failure(self):

        # TODO: Write failure test for shall_statement_quality
        self.fail("Test not yet implemented.")
