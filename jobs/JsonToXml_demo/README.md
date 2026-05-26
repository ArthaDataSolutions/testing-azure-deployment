# JsonToXml_demo Module Reference

## Purpose

`JsonToXml_demo` is a small Python demonstration module that converts a hard-coded invoice JSON payload into a formatted XML document and writes the result to standard output. It mirrors a simple Boomi-style integration flow with explicit logging around each major transformation step.

This module is useful as:

- a reference implementation for JSON-to-XML mapping,
- a lightweight integration demo,
- a test target for stdout and XML-generation behavior,
- an example of environment-driven logging configuration.

## Data Flow

The module performs the following sequence:

1. **Initialize logging**
   - Reads `LOG_LEVEL` from the environment.
   - Configures the root logging system with a standard timestamped format.

2. **Start process execution**
   - `json_to_xml_demo()` logs the beginning of the process.

3. **Load embedded JSON**
   - Uses a static invoice JSON string embedded directly in the function.

4. **Parse JSON**
   - Converts the JSON string into a Python dictionary using `json.loads()`.

5. **Map dictionary to XML**
   - Builds an `Invoice` XML tree using `xml.etree.ElementTree`.
   - Maps invoice fields to child elements and line items to repeated `Line` elements.

6. **Pretty-print XML**
   - `_prettify_xml()` serializes the XML and reformats it with `xml.dom.minidom`.

7. **Write output**
   - Prints the XML to `stdout`.
   - Ensures the output ends with a newline.

8. **Log completion or failure**
   - Logs success on completion.
   - Logs exception details and re-raises on failure.

## XML Output Structure

The generated XML follows this shape:

```xml
<?xml version="1.0" ?>
<Invoice>
  <InvoiceId>INV-2024-0042</InvoiceId>
  <Customer>Acme Corp</Customer>
  <Total currency="USD">1250.0</Total>
  <Lines>
    <Line sku="WIDGET-A" qty="10" unitPrice="50.0"/>
    <Line sku="GADGET-B" qty="5" unitPrice="150.0"/>
  </Lines>
</Invoice>
```

## Function Reference

| Name | Signature | Description |
|---|---|---|
| `_prettify_xml` | `(element: ET.Element) -> str` | Serializes and pretty-prints an XML element tree using `minidom`. |
| `json_to_xml_demo` | `() -> None` | Main process function that parses embedded JSON, builds XML, and writes it to stdout. |
| `JsonToXml_demo` | `() -> None` | Legacy-named wrapper that delegates to `json_to_xml_demo()`. |

## Configuration and Environment Variables

### `LOG_LEVEL`

Controls the configured logging level.

- **Environment variable:** `LOG_LEVEL`
- **Default:** `INFO`
- **Examples:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

Behavior notes:

- The value is uppercased before lookup.
- If the value does not match a valid `logging` level name, the module falls back to `logging.INFO`.

## Logging Behavior

The module configures logging with this format:

- timestamp
- log level
- logger name
- message

Typical log messages include:

- process start,
- JSON parsing,
- XML mapping,
- XML output,
- process completion,
- exception details on failure.

## Error Handling

The main process function wraps execution in a `try/except` block.

If an exception occurs:

1. the error is logged with stack trace information via `exc_info`,
2. the original exception is re-raised.

Potential failure points include:

- malformed JSON,
- invalid XML serialization/parsing,
- stdout write failures.

## Usage Example

### Run as a script

```python
from json_to_xml_demo import json_to_xml_demo

json_to_xml_demo()
```

### Use the legacy wrapper

```python
from json_to_xml_demo import JsonToXml_demo

JsonToXml_demo()
```

### Example shell execution

```bash
LOG_LEVEL=DEBUG python json_to_xml_demo.py
```

## Notes for Maintainers

- The input payload is embedded directly in the function, so the module is not currently parameterized for external input.
- The wrapper `JsonToXml_demo()` intentionally preserves a non-PEP 8 name for compatibility with the original process naming.
- XML line items are represented as repeated `Line` elements with attributes rather than nested child elements.
- The implementation favors simplicity and demonstration clarity over extensibility.

## Dependencies

This module uses only Python standard library components:

- `json`
- `logging`
- `os`
- `sys`
- `xml.etree.ElementTree`
- `xml.dom.minidom`
