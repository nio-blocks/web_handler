WebJSONHandler
==============
This block is a subclass of the `WebHandler` block and behaves very similarly. The main difference is that it will JSON parse the incoming request body (on a `POST` or `PUT` call) and put the result on the main part of the signal, rather than nested in the `$body` of the signal. As a result, the attributes on the output signal are somewhat different than on the parent block.

Properties
----------
- **auth**: If checked (true) incoming requests must include an Authorization header.
- **endpoint**: An optional endpoint to launch the server on. The URL that requests should be made to will follow the form `http://<HOST>:<PORT>/<ENDPOINT>`
- **host**: Host to launch the server on.
- **port**: The port to launch the server on. Be sure the port is not already in use.
- **request_timeout**: How long to give the service to respond to the request. If a corresponding WebOutput block does not write to the response for the incoming request in the specified time, a 504 Gateway Timed Out error will be returned to the caller. This is important to include in case an error in the service occurs.
- **ssl_cert**: Location of the SSL certificate file to apply to the web server
- **ssl_enable**: Enables the optional SSL security for the web handler endpoint
- **ssl_key**: Location of the SSL private key file to apply to the web server

Advanced Properties
-------------------
- **cors**: Allows overriding for CORS headers on all HTTP reponses for this **endpoint**.
    - **allow_credentials**: Set/override the `Access-Control-Allow-Credentials` reponse header.
    - **allow_headers**: Set/override the `Access-Control-Allow-Headers` reponse header.
    - **allow_methods**: Set/override the `Access-Control-Allow-Methods` reponse header.
    - **allow_origin**: Set/override the `Access-Control-Allow-Origin` reponse header.
    - **expose_headers**: Set/override the `Access-Control-Expose-Headers` reponse header.
    - **max_age**: Set/override the `Access-Control-Max-Age` reponse header.

Inputs
------
None

Outputs
-------
- **default**: One signal per request, the main (non-hidden) attributes on the notified signal will be the contents of the body of the HTTP request made. The following (hidden) attributes will also be included on the output signal.
  * **_id**: The unique request ID for this request. This value must carry along with the signal to the WebOutput block.
  * **_method**: The HTTP method (i.e. `GET`, `POST`, etc) that the request was made with.
  * **_params**: A dictionary containing any URL parameters passed to the request.
  * **_headers**: A dictionary containing any request headers included in the request.
  * **_user**: The User (nio.modules.security.user.User) object of the user who made the HTTP request. This is determined based on the `Authorization` header. If no authorization information is provided, the Guest user will probably be returned.

Commands
--------
None
