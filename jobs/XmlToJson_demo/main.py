"""Process: XmlToJson_demo

Source: Boomi
Converts embedded shipment XML into a JSON array.
Inputs: embedded XML payload
Outputs: JSON printed to stdout

This module reads shipment notification XML from the ``INPUT_XML`` environment
variable, parses each ``Shipment`` element, maps selected child elements to a
JSON-friendly dictionary structure, and prints the resulting JSON array to
standard output.
"""

import json
import logging
import os
from lxml import etree

logger = logging.getLogger(__name__)

# Environment variables derived from process placeholders/defaults
INPUT_XML: str = os.environ.get(
    "INPUT_XML",
    """<ShipmentNotifications>
  <Shipment>
    <ShipmentId>SHP-88901</ShipmentId>
    <OrderId>ORD-2024-0042</OrderId>
    <CarrierCode>FEDEX</CarrierCode>
    <TrackingNumber>7489203847561</TrackingNumber>
    <Status>IN_TRANSIT</Status>
    <EstimatedDelivery>2024-12-20</EstimatedDelivery>
  </Shipment>
  <Shipment>
    <ShipmentId>SHP-88902</ShipmentId>
    <OrderId>ORD-2024-0043</OrderId>
    <CarrierCode>UPS</CarrierCode>
    <TrackingNumber>1Z999AA10123456784</TrackingNumber>
    <Status>DELIVERED</Status>
    <EstimatedDelivery>2024-12-18</EstimatedDelivery>
  </Shipment>
</ShipmentNotifications>""",
)


def xml_to_json_demo() -> None:
    """Parse shipment XML and print a JSON array to standard output.

    The function performs the full process flow for the demo integration:

    1. Logs process startup.
    2. Parses the XML payload stored in ``INPUT_XML``.
    3. Finds all ``Shipment`` elements.
    4. Maps each shipment's child elements to a JSON-compatible dictionary
       using camelCase output keys.
    5. Prints the resulting JSON array to stdout.
    6. Logs process completion.

    The function uses broad exception handling around parsing, mapping, and
    output so that failures are logged before being re-raised.

    Raises:
        Exception: Re-raises any exception encountered during XML parsing,
            shipment mapping, or JSON output.
    """
    logger.info("Starting process XmlToJson_demo")

    try:
        logger.info("Parsing XML input and splitting by Shipment element")
        root = etree.fromstring(INPUT_XML.encode("utf-8"))
        shipment_elements = root.findall(".//Shipment")
    except Exception as exc:
        logger.error("Failed to parse XML input", exc_info=exc)
        raise

    try:
        logger.info("Mapping Shipment elements to JSON objects")
        shipments = []
        for shipment_element in shipment_elements:
            # Field-name mapping follows the Boomi map definition from XML element names to JSON camelCase keys.
            shipment_record = {
                "shipmentId": _get_child_text(shipment_element, "ShipmentId"),
                "orderId": _get_child_text(shipment_element, "OrderId"),
                "carrierCode": _get_child_text(shipment_element, "CarrierCode"),
                "trackingNumber": _get_child_text(shipment_element, "TrackingNumber"),
                "status": _get_child_text(shipment_element, "Status"),
                "estimatedDelivery": _get_child_text(shipment_element, "EstimatedDelivery"),
            }
            shipments.append(shipment_record)
    except Exception as exc:
        logger.error("Failed to map XML elements to JSON objects", exc_info=exc)
        raise

    try:
        logger.info("Printing JSON array to stdout")
        print(json.dumps(shipments, indent=2))
        logger.info("Completed process XmlToJson_demo")
    except Exception as exc:
        logger.error("Failed to print JSON output", exc_info=exc)
        raise


def _get_child_text(parent_element: etree._Element, child_tag: str) -> str:
    """Return stripped text content from a named child element.

    This helper looks up the first direct child element matching ``child_tag``
    under ``parent_element``. If the child element does not exist or contains
    no text, an empty string is returned.

    Args:
        parent_element: The XML element whose child should be inspected.
        child_tag: The tag name of the child element to find.

    Returns:
        The stripped text value of the child element, or an empty string if the
        child is missing or has no text content.
    """
    child = parent_element.find(child_tag)
    if child is None or child.text is None:
        return ""
    return child.text.strip()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    xml_to_json_demo()