# HTTP Protocol

## Overview

The **Hypertext Transfer Protocol (HTTP)** is an application-level protocol that is being widely used over the Web.
HTTP is a **request/response** protocol, which means, the client sends a request to the server (request method, URI, protocol version, followed by headers, and possible body content). 
The server responds (status code line, a success or error code, followed by server headers information, and possible entity-body content).

![][http-req-res]

Under the hood, HTTP requests and responses are sent over a TCP socket with default port 80 (on the server side).
Servers should be able to handle thousands of simultaneous TCP connections.

## Launch your InvParser app

Before exploring HTTP requests and responses, let's add a simple health check endpoint to your InvParser app.

Open your `app.py` file and add the following endpoint:

```python
@app.get('/health')
def health():
    return {'status': 'ok'}
```

This endpoint returns a simple JSON response indicating that the server is running. 
Start your application and verify it works:

```bash
python app.py
```

In another terminal, test the endpoint:

```bash
curl http://localhost:8080/health
```

You should see: `{"status":"ok"}`

## HTTP Request and Response

We can learn a lot by taking a closer look on a raw HTTP request and response that sent over the network:

```text
curl -v http://localhost:8080/health
```

Below is the actual raw HTTP request sent by `curl` to the server:

```text
GET /health HTTP/1.1
Host: localhost:8080
User-Agent: curl/7.68.0
Accept: */
```

The server response is:

```text
HTTP/1.1 200 OK
date: Sun, 04 May 2025 12:52:02 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}
```

The MDN web docs [specify the core components of request and response objects](https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview#http_flow), review this resource.

## Status code

HTTP response status codes indicate how a specific HTTP request was completed.

Responses are grouped in five classes:

- Informational (100–199)
- Successful (200–299)
- Redirection (300–399)
- Client error (400–499)
- Server error (500–599)

## Cookies

We mentioned that an HTTP server is stateless.
However, it is often desirable for a website to remember stateful information of users. For this purpose, HTTP uses **cookies**.

An HTTP cookie is a small piece of data that a server sends to a user's web browser. The browser may store the cookie and send it back to the same server with later requests. Most major commercial websites use cookies today.

![][networking_cookies]

As shown in the figure above, a cookie has four components:

1. `Set-Cookie` header line in the HTTP **response** message, usually in the form of `key=value`.
2. `Cookie` header line in the HTTP **request** message.
3. A cookie file kept on the user's end system and managed by the user's browser.
4. A back-end database at the website.

Suppose Berta contacts Amazon.com for the first time. When the request comes into the Amazon server, the server creates a unique id and creates an entry in its back-end database that is indexed by the id. Amazon  server then responds to Berta's browser, including in the HTTP response a `Set-cookie` header, which contains the id value. For example, the header line might be:

```text
Set-cookie: ITEM=12345
```

When Berta's browser receives the HTTP response message, it sees the `Set-cookie` header, and appends a line to the special cookie file that it manages locally.

As Berta continues to browse the Amazon site, each time she requests a web page, her browser consults her cookie file, extracts her id value for this site, and puts a cookie header line that includes the id value in the HTTP request. Specifically, each of her HTTP requests to the Amazon server includes the header line:

```text
Cookie: ITEM=12345
```

In this manner, Amazon server is able to track Berta's activity, it knows exactly which pages she visited, in which order, and at what times!

> [!WARNING]
> #### The dark side of cookies
>
> Although cookies often simplify and improve user experience, they are controversial because they can also be considered as an invasion of privacy.
> As we just saw, using a combination of cookies and user-supplied account information, a website can learn a lot about a user and potentially sell this information to a third party. The [GDPR](https://gdpr.eu/cookies/) website includes extensive information on cookies compliance requirements.


## APIs

An **API (Application Programming Interface)** can be thought of as a collection of all server **endpoints** that together define the functionality that is exposed to the client.
Each endpoint typically accepts input parameters in a specific format and returns output data in a standard format such as JSON or XML.

For example, a web API for a social media platform might include endpoints for retrieving a user's profile information, posting a new status update, or searching for other users.
Each endpoint would have a unique URL and a specific set of input parameters and output data.

Many platforms expose both API, and GUI. Like Spotify, OpenAI, GitHub, and, our Yolo service.

## Introducing Postman

Postman is a powerful and user-friendly tool for testing, debugging, and documenting APIs.    

1. Download from: https://learning.postman.com/docs/getting-started/first-steps/get-postman/.
2. Create a Postman account to unlock some important features.

# Exercises

### :pencil2: Practicing the HTTP protocol 

#### The `Accept` header

1. Use `curl` to perform an HTTP `GET` request to `http://httpbin.org/image`.
   Add an `Accept` header to your requests with the `image/png` value to indicate that you anticipate a `png` image.
2. Read carefully the Warning message written by `curl` at the end of the server response, follow the instructions to save the image on the file system.
3. Execute another `curl` to save the image in the file system.

Which animal appears in the served image?

#### Status code

1. Perform an HTTP `GET` request to `google.com`
2. What does the server response status code mean? Follow the response headers and body to get the real Google's home page.
3. Which HTTP version does the server use in the above response?

#### Connection close

The server of httpbin.org uses `keep-alive` connection by default, indicating that the server would like to keep the TCP connection open, so further requests to the server will use the same underlying TCP socket.

Perform an HTTP `POST` request to the `http://httpbin.org/anything` endpoint and tell the server that the client (you) would like to close the connection immediately after the server has responded.

Make sure the server's response contains the `Connection: close` header which means that the TCP connection used to serve the request was closed.

### :pencil2: Return informational errors  

In this exercise you'll modify your InvParser app to better handle unsuccessful requests.

When a user performs an unsuccessful request to your API, you'll raise an `HTTPException` with informational `status_code` and `detail`:

```python
from fastapi import HTTPException

raise HTTPException(status_code=400, detail="Only PDF files are supported")
```

Modify your `/extract` endpoint to validate that the uploaded file is a PDF:

1. Check that the file's content type is `application/pdf` or that the filename ends with `.pdf`.
2. If the file is not a PDF, raise an `HTTPException` with status code `400` and an appropriate error message.
3. Test your changes using `curl`:

```bash
# This should fail with 400 Bad Request
curl -i -X POST -F "file=@some_image.jpg" http://localhost:8080/extract

# This should work
curl -i -X POST -F "file=@invoice.pdf" http://localhost:8080/extract
```

Expected error response:

```json
{
  "detail": "Only PDF files are supported"
}
```

### :pencil2: Postman collections and simple API testing

- Run your InvParser app in the background
- Open Postman and select **+** in the workspace page to open a new tab.
- Enter `localhost:8080/health` for the request URL
- Select **Send**.

Postman displays the response data sent from the server in the lower pane.

Every request you send in Postman appears under the History tab of the sidebar. 
On a small scale, reusing requests through the history section is convenient.
As your Postman usage grows, it can be time-consuming to find a particular request in your history.
Instead of scrolling through your history section, you can use **Collections**. 

A Postman collection is a set of saved requests used to interact and test APIs. 
Collections allow you to group, organize, and execute multiple API calls easily.

- In your request builder, select **Save**.
- Create a new collection by selecting **New Collection**. Enter a collection name (e.g., "InvParser API"), and then select **Create**.
- Select **Save** to save the request in the new collection.
- Add to the created collection the following requests:
  - `GET /health` - Should return 200 OK
  - `POST /extract` with a PDF file - Should return 200 OK
  - `POST /extract` with a non-PDF file - Should return 400 Bad Request

**API tests** are a way to ensure that your API is behaving as you expect it to. 
For example, you might write a test to validate your API's error handling by sending a request with incomplete data or wrong parameters.

You can create and configure API tests using Postman and JavaScript. 

- Go to your `/health` request tab.
- In the request, go to the **Scripts** tab, then select the **Post-response** tab.
- In the snippet section to the right, select the snippet **Status code: Code is 200**. This will enter the following test code:

   ```javascript
   pm.test("Status code is 200", function () {
     pm.response.to.have.status(200);
   });
   ```

- Create a test for the `/extract` endpoint with a non-PDF file that validates the status code is 400 and the error message is correct:

   ```javascript
   pm.test("Status code is 400", function () {
     pm.response.to.have.status(400);
   });
   
   pm.test("Error message is correct", function () {
     var jsonData = pm.response.json();
     pm.expect(jsonData.detail).to.include("PDF");
   });
   ```

- You can utilize a built-in AI agent by clicking on the button in the top right corner of the code textbox.  

[http-req-res]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/networking_http-req-res.png
[networking_cookies]: https://exit-zero-academy.github.io/DevOpsTheHardWayAssets/img/networking_cookies.png

