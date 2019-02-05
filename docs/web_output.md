WebOutput
=========
This block writes to the response for a given HTTP request made to a WebHandler block

Properties
----------
- **id_val**: The same ID that was returned with the signal notified from the WebHandler block
- **response_headers**: A list of key/value pairs representing header names and header values to return in the HTTP response headers.
- **response_out**: What the payload of the response should be. This should be a string or bytes, do any serialization in the expression or beforehand.
- **response_status**: An integer representing the HTTP status to return. Defaults to 200 (type:OK)

Inputs
------
- **default**: Any list of signals

Outputs
-------
None

Commands
--------
None
