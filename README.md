Web Handlers
===========

A suite of blocks that lets you build HTTP APIs using n.io services. In general, your service will have at least one of the following blocks, a Handler block and an Output block. 

The Handler block will launch an HTTP server on the specified port and will notify signals when requests are made to that server. 

The Output block is intended to respond to the requests made to the Handler block. These two blocks are "linked" by a request ID that will be notified on the signal by the Handler block and must be specified to the Output block.

### Handler Blocks
 * [WebHandler](#webhandler) - Basic HTTP request handling
 * [WebJSONHandler](#webjsonhandler) - Expects JSON in the body of a request that will be converted to a signal
 
### Output Blocks
 * [WebOutput](#weboutput) - Basic HTTP response writing
 * [WebJSONOutput](#webjsonoutput) - Automatically sets the `Content-Type: application/json` header and dumps the incoming signal to the response body by default
 
WebHandler
==========

Properties
----------
 * **Port** (type:int): The port to launch the server on. Be sure the port is not already in use
 * **Endpoint** (type:string): An optional endpoint to launch the server on. The URL that requests should be made to will follow the form `http://<HOST>:<PORT>/<ENDPOINT>`
 * **Max Request Timeout** (type:timedelta): How long to give the service to respond to the request. If a corresponding WebOutput block does not write to the response for the incoming request in the specified time, a 504 Gateway Timed Out error will be returned to the caller. This is important to include in case an error in the service occurs.

Dependencies
------------

Commands
--------
None

Input
-----
None

Output
------
One signal per request, each with the following attributes

 * **id**: The unique request ID for this request. This value must carry along with the signal to the WebOutput block.
 * **method**: The HTTP method (i.e. `GET`, `POST`, etc) that the request was made with.
 * **params**: A dictionary containing any URL parameters passed to the request.
 * **headers**: A dictionary containing any request headers included in the request.
 * **body**: For some requests, the payload of the HTTP request
 * **user**: The User (nio.modules.security.user.User) object of the user who made the HTTP request. This is determined based on the `Authorization` header. If no authorization information is provided, the Guest user will probably be returned.

***

WebJSONHandler
==============

This block is a subclass of the `WebHandler` block and behaves very similarly. The main difference is that it will JSON parse the incoming request body (on a `POST` or `PUT` call) and put the result on the main part of the signal, rather than nested in the `$body` of the signal. As a result, the attributes on the output signal are somewhat different than on the parent block.

Output
------
One signal per request, the main (non-hidden) attributes on the notified signal will be the contents of the body of the HTTP request made. The following (hidden) attributes will also be included on the output signal.

 * **_id**: The unique request ID for this request. This value must carry along with the signal to the WebOutput block.
 * **_method**: The HTTP method (i.e. `GET`, `POST`, etc) that the request was made with.
 * **_params**: A dictionary containing any URL parameters passed to the request.
 * **_headers**: A dictionary containing any request headers included in the request.
 * **_user**: The User (nio.modules.security.user.User) object of the user who made the HTTP request. This is determined based on the `Authorization` header. If no authorization information is provided, the Guest user will probably be returned.

***

WebOutput
=========

This block writes to the response for a given HTTP request made to a WebHandler block

Properties
----------
 * **Request ID** (type:expression): The same ID that was returned with the signal notified from the WebHandler block
 * **Response Body** (type:expression): What the payload of the response should be. This should be a string or bytes, do any serialization in the expression or beforehand.
 * **Response Status** (type:expression): An integer representing the HTTP status to return. Defaults to 200 (type:OK)
 * **Response Headers** (type:list of expressions): A list of key/value pairs representing header names and header values to return in the HTTP response headers.

Dependencies
------------
None

Commands
--------
None

Input
-----
Any list of signals

Output
------
None

***

WebJSONOutput
=============

This block is a subclass of the `WebOutput` block and behaves very similarly. This block is mainly intended for use in conjunction with the `WebJSONHandler` block as the Handler block of the service. It can be configured to behave *exactly* the same as the `WebOutput` block but has some shortcuts and common configuration built in by default.

Mainly, it will automatically add the `Content-Type: application/json` header to the response headers. This can be overridden by adding a different `Content-Type` header in the block config. 

The block also has a convenient default for the `Response Body` config which will write the non-hidden attributes of the signal to the response.

This block, along with the `WebJSONHandler` block, should be used if you find yourself having to dive into the `$body` of the standard request signal more often that you would like. It is also useful for building a response object through DynamicFields or similar blocks.
