"""Process: JsonToXml_demo
Source: Boomi
Converts an invoice JSON payload into XML and prints it to stdout.
Inputs: embedded JSON string
Outputs: XML document on stdout

This module demonstrates a simple end-to-end transformation pipeline that:

1. Reads an embedded JSON invoice payload.
2. Parses the JSON into a Python dictionary.
3. Maps the parsed data into an XML element tree.
4. Pretty-prints the XML document.
5. Writes the final XML to standard output.

The module also configures logging from the ``LOG_LEVEL`` environment variable
and exposes both a snake_case implementation function and a legacy-compatible
wrapper named ``JsonToXml_demo``.
"""

import json
import logging
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Environment variables from placeholders
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


def _prettify_xml(element: ET.Element) -> str:
    """Convert an XML element into a human-readable XML string.

    This helper serializes the provided element tree to UTF-8 bytes, reparses it
    with ``xml.dom.minidom``, and returns a pretty-printed XML string using a
    two-space indentation level.

    Args:
        element: The root XML element to serialize and format.

    Returns:
        A pretty-printed XML document as a string.

    Raises:
        xml.parsers.expat.ExpatError: If the serialized XML cannot be reparsed by
            ``minidom.parseString``.
        TypeError: If ``element`` is not a valid ``xml.etree.ElementTree.Element``
            instance for serialization.
    """
    rough_xml = ET.tostring(element, encoding="utf-8")
    parsed = minidom.parseString(rough_xml)
    return parsed.toprettyxml(indent="  ")


def json_to_xml_demo() -> None:
    """Run the JSON-to-XML demonstration process.

    The function logs process start and completion, parses a hard-coded invoice
    JSON payload, maps the resulting dictionary into an XML structure, formats
    the XML for readability, and writes the final document to standard output.

    The generated XML has the following high-level structure:

    - ``Invoice`` as the root element
    - ``InvoiceId`` containing the invoice identifier
    - ``Customer`` containing the customer name
    - ``Total`` containing the invoice total and a ``currency`` attribute
    - ``Lines`` containing repeated ``Line`` elements for each line item

    Returns:
        None.

    Raises:
        Exception: Re-raises any exception encountered during parsing, mapping,
            formatting, or output after logging the failure.
    """
    try:
        logger.info("Starting process JsonToXml_demo")

        # Boomi shape: Start [start]
        input_json = """{
  "invoiceId": "INV-2024-0042",
  "customerName": "Acme Corp",
  "invoiceTotal": 1250.00,
  "currency": "USD",
  "lineItems": [
    {"sku": "WIDGET-A", "qty": 10, "unitPrice": 50.00},
    {"sku": "GADGET-B", "qty": 5, "unitPrice": 150.00}
  ]
}"""

        # Boomi shape: Parse JSON string to dict [dataProcess]
        logger.info("Parsing JSON input")
        invoice_data = json.loads(input_json)

        # Boomi shape: Convert dict to XML [map]
        logger.info("Mapping parsed JSON to XML structure")
        invoice_root = ET.Element("Invoice")

        invoice_id_element = ET.SubElement(invoice_root, "InvoiceId")
        invoice_id_element.text = str(invoice_data.get("invoiceId", ""))

        customer_element = ET.SubElement(invoice_root, "Customer")
        customer_element.text = str(invoice_data.get("customerName", ""))

        total_element = ET.SubElement(invoice_root, "Total")
        total_element.text = str(invoice_data.get("invoiceTotal", ""))
        total_element.set("currency", str(invoice_data.get("currency", "")))

        lines_element = ET.SubElement(invoice_root, "Lines")

        # Map each line item object into a repeated Line element with attributes.
        for line_item in invoice_data.get("lineItems", []):
            line_element = ET.SubElement(lines_element, "Line")
            line_element.set("sku", str(line_item.get("sku", "")))
            line_element.set("qty", str(line_item.get("qty", "")))
            line_element.set("unitPrice", str(line_item.get("unitPrice", "")))

        xml_output = _prettify_xml(invoice_root)

        # Boomi shape: Print XML to stdout [stop]
        logger.info("Printing XML output")
        sys.stdout.write(xml_output)
        if not xml_output.endswith("\n"):
            sys.stdout.write("\n")

        logger.info("Completed process JsonToXml_demo")
    except Exception as exc:
        logger.error("Process JsonToXml_demo failed", exc_info=exc)
        raise


def JsonToXml_demo() -> None:
    """Invoke the JSON-to-XML demo using the legacy process name.

    This wrapper preserves the original Boomi-style process naming convention
    while delegating execution to the PEP 8-compliant ``json_to_xml_demo``
    implementation.

    Returns:
        None.
    """
    json_to_xml_demo()


if __name__ == "__main__":
    json_to_xml_demo()