import importlib
import json
import sys
from unittest.mock import MagicMock, patch

import pytest
import xml.etree.ElementTree as ET


MODULE_NAME = "JsonToXml_demo"


@pytest.fixture
def module_under_test():
    """Import and return the target module for testing."""
    if MODULE_NAME in sys.modules:
        return importlib.reload(sys.modules[MODULE_NAME])
    return importlib.import_module(MODULE_NAME)


@pytest.fixture
def sample_invoice_dict():
    """Provide a representative invoice payload used by multiple tests."""
    return {
        "invoiceId": "INV-2024-0042",
        "customerName": "Acme Corp",
        "invoiceTotal": 1250.0,
        "currency": "USD",
        "lineItems": [
            {"sku": "WIDGET-A", "qty": 10, "unitPrice": 50.0},
            {"sku": "GADGET-B", "qty": 5, "unitPrice": 150.0},
        ],
    }


def test_prettify_xml_returns_pretty_printed_xml_string(module_under_test):
    """_prettify_xml should convert an XML element into an indented XML string."""
    root = ET.Element("Invoice")
    child = ET.SubElement(root, "InvoiceId")
    child.text = "INV-1"

    result = module_under_test._prettify_xml(root)

    assert isinstance(result, str)
    assert result.startswith("<?xml")
    assert "<Invoice>" in result
    assert "<InvoiceId>INV-1</InvoiceId>" in result
    assert "  <InvoiceId>INV-1</InvoiceId>" in result


def test_json_to_xml_demo_writes_expected_xml_and_trailing_newline(module_under_test, sample_invoice_dict):
    """json_to_xml_demo should transform invoice JSON into XML and write it to stdout with a newline."""
    stdout_mock = MagicMock()

    with patch.object(module_under_test.json, "loads", return_value=sample_invoice_dict) as loads_mock, \
         patch.object(module_under_test.sys, "stdout", stdout_mock), \
         patch.object(module_under_test.logger, "info") as info_mock:
        module_under_test.json_to_xml_demo()

    loads_mock.assert_called_once()
    assert stdout_mock.write.call_count == 1

    written_xml = stdout_mock.write.call_args_list[0].args[0]
    assert written_xml.endswith("\n")
    assert "<Invoice>" in written_xml
    assert "<InvoiceId>INV-2024-0042</InvoiceId>" in written_xml
    assert "<Customer>Acme Corp</Customer>" in written_xml
    assert '<Total currency="USD">1250.0</Total>' in written_xml
    assert '<Line sku="WIDGET-A" qty="10" unitPrice="50.0"/>' in written_xml
    assert '<Line sku="GADGET-B" qty="5" unitPrice="150.0"/>' in written_xml

    info_messages = [call.args[0] for call in info_mock.call_args_list]
    assert "Starting process JsonToXml_demo" in info_messages
    assert "Parsing JSON input" in info_messages
    assert "Mapping parsed JSON to XML structure" in info_messages
    assert "Printing XML output" in info_messages
    assert "Completed process JsonToXml_demo" in info_messages


def test_json_to_xml_demo_handles_missing_optional_fields_with_empty_values(module_under_test):
    """json_to_xml_demo should emit empty XML values when expected JSON fields are missing."""
    invoice_data = {}
    stdout_mock = MagicMock()

    with patch.object(module_under_test.json, "loads", return_value=invoice_data), \
         patch.object(module_under_test.sys, "stdout", stdout_mock):
        module_under_test.json_to_xml_demo()

    written_xml = stdout_mock.write.call_args_list[0].args[0]
    assert "<InvoiceId/>" in written_xml or "<InvoiceId></InvoiceId>" in written_xml
    assert "<Customer/>" in written_xml or "<Customer></Customer>" in written_xml
    assert '<Total currency=""/>' in written_xml or '<Total currency=""></Total>' in written_xml
    assert "<Lines/>" in written_xml or "<Lines></Lines>" in written_xml


def test_json_to_xml_demo_handles_empty_line_items_without_line_elements(module_under_test):
    """json_to_xml_demo should create a Lines container without Line children when lineItems is empty."""
    invoice_data = {
        "invoiceId": "INV-EMPTY",
        "customerName": "No Lines Inc",
        "invoiceTotal": 0,
        "currency": "USD",
        "lineItems": [],
    }
    stdout_mock = MagicMock()

    with patch.object(module_under_test.json, "loads", return_value=invoice_data), \
         patch.object(module_under_test.sys, "stdout", stdout_mock):
        module_under_test.json_to_xml_demo()

    written_xml = stdout_mock.write.call_args_list[0].args[0]
    assert "<Lines/>" in written_xml or "<Lines></Lines>" in written_xml
    assert "<Line " not in written_xml


def test_json_to_xml_demo_converts_non_string_values_to_strings_in_xml_attributes(module_under_test):
    """json_to_xml_demo should stringify numeric and None values when building XML content and attributes."""
    invoice_data = {
        "invoiceId": 123,
        "customerName": None,
        "invoiceTotal": 99.95,
        "currency": None,
        "lineItems": [
            {"sku": None, "qty": 7, "unitPrice": 12.5},
        ],
    }
    stdout_mock = MagicMock()

    with patch.object(module_under_test.json, "loads", return_value=invoice_data), \
         patch.object(module_under_test.sys, "stdout", stdout_mock):
        module_under_test.json_to_xml_demo()

    written_xml = stdout_mock.write.call_args_list[0].args[0]
    assert "<InvoiceId>123</InvoiceId>" in written_xml
    assert "<Customer>None</Customer>" in written_xml
    assert '<Total currency="None">99.95</Total>' in written_xml
    assert '<Line sku="None" qty="7" unitPrice="12.5"/>' in written_xml


def test_json_to_xml_demo_adds_newline_when_prettified_xml_lacks_one(module_under_test):
    """json_to_xml_demo should append a newline if the prettified XML does not already end with one."""
    stdout_mock = MagicMock()
    invoice_data = {"lineItems": []}

    with patch.object(module_under_test.json, "loads", return_value=invoice_data), \
         patch.object(module_under_test, "_prettify_xml", return_value="<Invoice></Invoice>"), \
         patch.object(module_under_test.sys, "stdout", stdout_mock):
        module_under_test.json_to_xml_demo()

    assert stdout_mock.write.call_count == 2
    assert stdout_mock.write.call_args_list[0].args[0] == "<Invoice></Invoice>"
    assert stdout_mock.write.call_args_list[1].args[0] == "\n"


def test_json_to_xml_demo_does_not_add_extra_newline_when_xml_already_has_one(module_under_test):
    """json_to_xml_demo should not write an extra newline when the XML output already ends with one."""
    stdout_mock = MagicMock()
    invoice_data = {"lineItems": []}

    with patch.object(module_under_test.json, "loads", return_value=invoice_data), \
         patch.object(module_under_test, "_prettify_xml", return_value="<Invoice></Invoice>\n"), \
         patch.object(module_under_test.sys, "stdout", stdout_mock):
        module_under_test.json_to_xml_demo()

    assert stdout_mock.write.call_count == 1
    assert stdout_mock.write.call_args_list[0].args[0] == "<Invoice></Invoice>\n"


def test_json_to_xml_demo_logs_and_reraises_when_json_parsing_fails(module_under_test):
    """json_to_xml_demo should log an error and re-raise when json.loads raises an exception."""
    exc = json.JSONDecodeError("bad json", "doc", 0)

    with patch.object(module_under_test.json, "loads", side_effect=exc), \
         patch.object(module_under_test.logger, "error") as error_mock:
        with pytest.raises(json.JSONDecodeError):
            module_under_test.json_to_xml_demo()

    error_mock.assert_called_once()
    assert error_mock.call_args.args[0] == "Process JsonToXml_demo failed"
    assert error_mock.call_args.kwargs["exc_info"] is exc


def test_json_to_xml_demo_logs_and_reraises_when_prettify_fails(module_under_test):
    """json_to_xml_demo should log an error and re-raise when XML prettification fails."""
    invoice_data = {"lineItems": []}
    exc = ValueError("prettify failed")

    with patch.object(module_under_test.json, "loads", return_value=invoice_data), \
         patch.object(module_under_test, "_prettify_xml", side_effect=exc), \
         patch.object(module_under_test.logger, "error") as error_mock:
        with pytest.raises(ValueError):
            module_under_test.json_to_xml_demo()

    error_mock.assert_called_once()
    assert error_mock.call_args.args[0] == "Process JsonToXml_demo failed"
    assert error_mock.call_args.kwargs["exc_info"] is exc


def test_json_to_xml_demo_logs_and_reraises_when_stdout_write_fails(module_under_test):
    """json_to_xml_demo should log an error and re-raise when writing XML to stdout fails."""
    invoice_data = {"lineItems": []}
    stdout_mock = MagicMock()
    stdout_mock.write.side_effect = OSError("stdout unavailable")

    with patch.object(module_under_test.json, "loads", return_value=invoice_data), \
         patch.object(module_under_test.sys, "stdout", stdout_mock), \
         patch.object(module_under_test.logger, "error") as error_mock:
        with pytest.raises(OSError):
            module_under_test.json_to_xml_demo()

    error_mock.assert_called_once()
    assert error_mock.call_args.args[0] == "Process JsonToXml_demo failed"
    assert isinstance(error_mock.call_args.kwargs["exc_info"], OSError)


def test_jsontoxml_demo_wrapper_delegates_to_json_to_xml_demo(module_under_test):
    """JsonToXml_demo should call the underlying json_to_xml_demo function exactly once."""
    with patch.object(module_under_test, "json_to_xml_demo") as wrapped_mock:
        module_under_test.JsonToXml_demo()

    wrapped_mock.assert_called_once_with()
