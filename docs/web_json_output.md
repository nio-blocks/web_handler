WebJSONOutput
=============
This block is a subclass of the `WebOutput` block and behaves very similarly. This block is mainly intended for use in conjunction with the `WebJSONHandler` block as the Handler block of the service. It can be configured to behave *exactly* the same as the `WebOutput` block but has some shortcuts and common configuration built in by default. Mainly, it will automatically add the `Content-Type: application/json` header to the response headers. This can be overridden by adding a different `Content-Type` header in the block config. The block also has a convenient default for the `Response Body` config which will write the non-hidden attributes of the signal to the response. This block, along with the `WebJSONHandler` block, should be used if you find yourself having to dive into the `$body` of the standard request signal more often that you would like. It is also useful for building a response object through DynamicFields or similar blocks.

Properties
----------
- **id_val**: The same ID that was returned with the signal notified from the WebHandler block
- **response_headers**: A list of key/value pairs representing header names and header values to return in the HTTP response headers.
- **response_out**: What the payload of the response should be. This should be a string or bytes, do any serialization in the expression or beforehand.
- **response_status**: An integer representing the HTTP status to return. Defaults to 200 (type:OK)

Inputs
------
- **default**: 

Outputs
-------
None

Commands
--------
None
