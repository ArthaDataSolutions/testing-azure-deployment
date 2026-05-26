# XmlToJson_demo Module Reference

## Purpose

`XmlToJson_demo` is a small Python integration script that converts shipment notification XML into a JSON array printed to standard output. It mirrors a simple Boomi-style process flow:

- read XML input from configuration,
- parse and split by `Shipment` elements,
- map XML fields to JSON keys,
- emit formatted JSON.

This module is intended as a demo or lightweight transformation utility.

## Data Flow

1. **Input acquisition**
   - The module reads the `INPUT_XML` environment variable at import time.
   - If `INPUT_XML` is not set, a built-in sample XML payload is used.

2. **XML parsing**
   - `xml_to_json_demo()` encodes the XML string as UTF-8 bytes.
   - `lxml.etree.fromstring()` parses the XML into an element tree.

3. **Shipment extraction**
   - The code finds all `.//Shipment` elements beneath the root.

4. **Field mapping**
   - Each `Shipment` element is converted into a Python dictionary.
   - XML element names are mapped to camelCase JSON keys.

5. **Output generation**
   - The list of shipment dictionaries is serialized with `json.dumps(..., indent=2)`.
   - The JSON array is printed to stdout.

6. **Logging and error handling**
   - Informational log messages are emitted for each major stage.
   - Broad exceptions are logged and re-raised.

## Function Reference

| Name | Signature | Description |
|---|---|---|
| `xml_to_json_demo` | `xml_to_json_demo() -> None` | Runs the full XML-to-JSON transformation and prints the result. |
| `_get_child_text` | `_get_child_text(parent_element: etree._Element, child_tag: str) -> str` | Returns stripped text from a named child element, or an empty string if missing. |

## XML to JSON Mapping

The module maps each `Shipment` element as follows:

| XML Element | JSON Key |
|---|---|
| `ShipmentId` | `shipmentId` |
| `OrderId` | `orderId` |
| `CarrierCode` | `carrierCode` |
| `TrackingNumber` | `trackingNumber` |
| `Status` | `status` |
| `EstimatedDelivery` | `estimatedDelivery` |

## Configuration / Environment Variables

### `INPUT_XML`

- **Required:** No
- **Default:** Embedded sample shipment XML
- **Purpose:** Supplies the XML payload to parse and transform

Because `INPUT_XML` is read at module import time, changes to the environment after import will not affect the already-loaded module unless it is reloaded.

## Logging

The module uses the standard library `logging` package with a module-level logger:

- logger name: `__name__`
- startup and completion events are logged at `INFO`
- failures are logged at `ERROR` with exception information

When run as a script, logging is configured with:

```python
logging.basicConfig(level=logging.INFO)
```

## Usage Example

### Run with default embedded XML

```python
from xml_to_json_demo import xml_to_json_demo

xml_to_json_demo()
```

### Run with custom XML via environment variable

```python
import os
from xml_to_json_demo import xml_to_json_demo

os.environ["INPUT_XML"] = """
<ShipmentNotifications>
  <Shipment>
    <ShipmentId>SHP-10001</ShipmentId>
    <OrderId>ORD-50001</OrderId>
    <CarrierCode>DHL</CarrierCode>
    <TrackingNumber>TRACK123</TrackingNumber>
    <Status>SHIPPED</Status>
    <EstimatedDelivery>2025-01-15</EstimatedDelivery>
  </Shipment>
</ShipmentNotifications>
"""

# Note: if the module was already imported before setting INPUT_XML,
# reload the module or set the environment variable before import.
xml_to_json_demo()
```

### Example Output

```json
[
  {
    "shipmentId": "SHP-88901",
    "orderId": "ORD-2024-0042",
    "carrierCode": "FEDEX",
    "trackingNumber": "7489203847561",
    "status": "IN_TRANSIT",
    "estimatedDelivery": "2024-12-20"
  },
  {
    "shipmentId": "SHP-88902",
    "orderId": "ORD-2024-0043",
    "carrierCode": "UPS",
    "trackingNumber": "1Z999AA10123456784",
    "status": "DELIVERED",
    "estimatedDelivery": "2024-12-18"
  }
]
```

## Notes and Considerations

- The XML parser is used with default settings; for untrusted XML input, a hardened parser configuration should be considered.
- Exception handling is intentionally broad to preserve the current process behavior and logging pattern.
- The transformation logic is simple and deterministic, making it straightforward to test.
- Missing XML child elements are converted to empty strings rather than causing failures.
