import importlib
import json
import os
import sys
from unittest.mock import MagicMock, patch

import pytest


MODULE_NAME = "xml_to_json_demo"


@pytest.fixture
def module_under_test():
    """Import the target module with a clean environment for each test."""
    if MODULE_NAME in sys.modules:
        del sys.modules[MODULE_NAME]
    with patch.dict(os.environ, {}, clear=True):
        module = importlib.import_module(MODULE_NAME)
    return module


@pytest.fixture
def sample_xml():
    """Provide a representative XML payload with two shipments."""
    return """<ShipmentNotifications>
  <Shipment>
    <ShipmentId>SHP-100</ShipmentId>
    <OrderId>ORD-100</OrderId>
    <CarrierCode>UPS</CarrierCode>
    <TrackingNumber>1Z123</TrackingNumber>
    <Status>IN_TRANSIT</Status>
    <EstimatedDelivery>2024-12-31</EstimatedDelivery>
  </Shipment>
  <Shipment>
    <ShipmentId>SHP-200</ShipmentId>
    <OrderId>ORD-200</OrderId>
    <CarrierCode>FEDEX</CarrierCode>
    <TrackingNumber>999999</TrackingNumber>
    <Status>DELIVERED</Status>
    <EstimatedDelivery>2025-01-01</EstimatedDelivery>
  </Shipment>
</ShipmentNotifications>"""


@pytest.fixture
def expected_shipments():
    """Provide the expected JSON-ready shipment records for the sample XML."""
    return [
        {
            "shipmentId": "SHP-100",
            "orderId": "ORD-100",
            "carrierCode": "UPS",
            "trackingNumber": "1Z123",
            "status": "IN_TRANSIT",
            "estimatedDelivery": "2024-12-31",
        },
        {
            "shipmentId": "SHP-200",
            "orderId": "ORD-200",
            "carrierCode": "FEDEX",
            "trackingNumber": "999999",
            "status": "DELIVERED",
            "estimatedDelivery": "2025-01-01",
        },
    ]


def test_xml_to_json_demo_happy_path_prints_expected_json(module_under_test, sample_xml, expected_shipments, capsys):
    """xml_to_json_demo should parse valid XML and print the expected JSON array."""
    module_under_test.INPUT_XML = sample_xml

    module_under_test.xml_to_json_demo()

    captured = capsys.readouterr()
    assert json.loads(captured.out) == expected_shipments


def test_xml_to_json_demo_with_no_shipment_elements_prints_empty_array(module_under_test, capsys):
    """xml_to_json_demo should print an empty JSON array when no Shipment elements exist."""
    module_under_test.INPUT_XML = "<ShipmentNotifications></ShipmentNotifications>"

    module_under_test.xml_to_json_demo()

    captured = capsys.readouterr()
    assert json.loads(captured.out) == []


def test_xml_to_json_demo_missing_fields_maps_to_empty_strings(module_under_test, capsys):
    """xml_to_json_demo should map missing child elements to empty strings in output records."""
    module_under_test.INPUT_XML = """<ShipmentNotifications>
    <Shipment>
        <ShipmentId>SHP-300</ShipmentId>
        <OrderId>ORD-300</OrderId>
    </Shipment>
</ShipmentNotifications>"""

    module_under_test.xml_to_json_demo()

    captured = capsys.readouterr()
    assert json.loads(captured.out) == [
        {
            "shipmentId": "SHP-300",
            "orderId": "ORD-300",
            "carrierCode": "",
            "trackingNumber": "",
            "status": "",
            "estimatedDelivery": "",
        }
    ]


def test_xml_to_json_demo_strips_whitespace_from_child_text(module_under_test, capsys):
    """xml_to_json_demo should strip surrounding whitespace from XML child text values."""
    module_under_test.INPUT_XML = """<ShipmentNotifications>
    <Shipment>
        <ShipmentId>  SHP-400  </ShipmentId>
        <OrderId>
            ORD-400
        </OrderId>
        <CarrierCode> UPS </CarrierCode>
        <TrackingNumber> 12345 </TrackingNumber>
        <Status> DELIVERED </Status>
        <EstimatedDelivery> 2025-02-02 </EstimatedDelivery>
    </Shipment>
</ShipmentNotifications>"""

    module_under_test.xml_to_json_demo()

    captured = capsys.readouterr()
    assert json.loads(captured.out) == [
        {
            "shipmentId": "SHP-400",
            "orderId": "ORD-400",
            "carrierCode": "UPS",
            "trackingNumber": "12345",
            "status": "DELIVERED",
            "estimatedDelivery": "2025-02-02",
        }
    ]


def test_xml_to_json_demo_invalid_xml_raises_and_logs_error(module_under_test):
    """xml_to_json_demo should raise an exception and log an error when XML parsing fails."""
    module_under_test.INPUT_XML = "<ShipmentNotifications><Shipment></ShipmentNotifications>"

    with patch.object(module_under_test.logger, "error") as mock_error:
        with pytest.raises(Exception):
            module_under_test.xml_to_json_demo()

    mock_error.assert_called_once()
    assert "Failed to parse XML input" in mock_error.call_args[0][0]


def test_xml_to_json_demo_mapping_error_raises_and_logs_error(module_under_test, sample_xml):
    """xml_to_json_demo should raise and log when mapping shipment elements fails."""
    module_under_test.INPUT_XML = sample_xml

    with patch.object(module_under_test, "_get_child_text", side_effect=RuntimeError("mapping failed")):
        with patch.object(module_under_test.logger, "error") as mock_error:
            with pytest.raises(RuntimeError, match="mapping failed"):
                module_under_test.xml_to_json_demo()

    mock_error.assert_called_once()
    assert "Failed to map XML elements to JSON objects" in mock_error.call_args[0][0]


def test_xml_to_json_demo_print_error_raises_and_logs_error(module_under_test, sample_xml):
    """xml_to_json_demo should raise and log when printing JSON output fails."""
    module_under_test.INPUT_XML = sample_xml

    with patch("builtins.print", side_effect=OSError("stdout unavailable")):
        with patch.object(module_under_test.logger, "error") as mock_error:
            with pytest.raises(OSError, match="stdout unavailable"):
                module_under_test.xml_to_json_demo()

    mock_error.assert_called_once()
    assert "Failed to print JSON output" in mock_error.call_args[0][0]


def test_xml_to_json_demo_logs_start_and_completion_messages(module_under_test, sample_xml):
    """xml_to_json_demo should emit informational log messages for start and completion."""
    module_under_test.INPUT_XML = sample_xml

    with patch.object(module_under_test.logger, "info") as mock_info:
        with patch("builtins.print"):
            module_under_test.xml_to_json_demo()

    info_messages = [call.args[0] for call in mock_info.call_args_list]
    assert "Starting process XmlToJson_demo" in info_messages
    assert "Parsing XML input and splitting by Shipment element" in info_messages
    assert "Mapping Shipment elements to JSON objects" in info_messages
    assert "Printing JSON array to stdout" in info_messages
    assert "Completed process XmlToJson_demo" in info_messages


def test_get_child_text_returns_stripped_text_for_existing_child(module_under_test):
    """_get_child_text should return stripped text when the child element exists with text."""
    parent = module_under_test.etree.fromstring("<Shipment><Status>  IN_TRANSIT  </Status></Shipment>")

    result = module_under_test._get_child_text(parent, "Status")

    assert result == "IN_TRANSIT"


def test_get_child_text_returns_empty_string_when_child_missing(module_under_test):
    """_get_child_text should return an empty string when the requested child element is absent."""
    parent = module_under_test.etree.fromstring("<Shipment><Status>DELIVERED</Status></Shipment>")

    result = module_under_test._get_child_text(parent, "TrackingNumber")

    assert result == ""


def test_get_child_text_returns_empty_string_when_child_text_is_none(module_under_test):
    """_get_child_text should return an empty string when the child exists but has no text."""
    parent = module_under_test.etree.fromstring("<Shipment><Status/></Shipment>")

    result = module_under_test._get_child_text(parent, "Status")

    assert result == ""
