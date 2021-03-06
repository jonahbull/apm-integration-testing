#!/usr/bin/env python
import pytest
import json
from tests.fixtures.transactions import minimal
from tests.fixtures.apm_server import apm_server
from tests.fixtures.es import es
from tests.fixtures.kibana import kibana
from tests.fixtures.agents import flask
from tests.fixtures.agents import django
from tests.fixtures.agents import express
from tests.fixtures.agents import rails
from tests.fixtures.agents import go_nethttp
from tests.fixtures.agents import java_spring
from tests.fixtures.agents import rum



def pytest_addoption(parser):
    parser.addoption(
        "--run-upgrade", action="store_true", default=False, help="run upgrade tests"
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-upgrade"):
        return
    skip_upgrade = pytest.mark.skip(reason="need --run-upgrade option to run")
    for item in items:
        if item.get_marker("upgradetest"):
            item.add_marker(skip_upgrade)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_logreport(report):
    yield
    if report.when == "call" and report.failed:
        rs = es().es.search(index="apm-*", size=1000)
        name = report.nodeid.split(":",2)[-1]
        try:
            with open("/app/tests/results/data-{}.json".format(name), 'w') as outFile:
                json.dump(rs, outFile, sort_keys=True, indent=4, ensure_ascii=False)
        except IOError:
            pass
