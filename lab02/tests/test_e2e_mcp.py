"""
Part 7 — End-to-End Testing with MCP
======================================
Goal: Write E2E tests that exercise the full API workflow
(create task, retrieve tasks, handle errors) using MCP tooling.
"""

import pytest


class TestApiEndToEnd:

    def test_api_post_creates_task(self):
        # TODO: POST a new task via the API and verify it was created
        pytest.skip("TODO: implement in Part 7 using MCP")

    def test_api_get_returns_tasks(self):
        # TODO: GET tasks from the API and verify the response
        pytest.skip("TODO: implement in Part 7 using MCP")

    def test_api_error_handling(self):
        # TODO: Send an invalid request and verify proper error response
        pytest.skip("TODO: implement in Part 7 using MCP")
