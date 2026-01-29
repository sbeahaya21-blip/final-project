# Test design strategies

As a reminder, **test design** is the process of choosing the strategy and approach for testing our app.

#### End-to-end (manual) testing

In the previous project, you tested your endpoints **manually** using `curl` or Postman, while the app was running locally in the background.
This strategy is known as **end-to-end testing**, because you, as a tester, interact with the app just like a real user would do. And the app is fully running, as a whole, with all its components (database, external OCI service communication, etc...).

```mermaid 
sequenceDiagram
    participant TS as curl/Postman
    participant RA as Uvicorn
    participant FA as FastAPI App
    participant DB as SQLite Database (Real)

    TS->>RA: HTTP Request (GET/POST/PUT/DELETE)
    RA->>FA: Route Request to Endpoint
    FA->>DB: Execute SQL Query
    DB-->>FA: Return Query Results
    FA-->>RA: HTTP Response (JSON)
    RA-->>TS: Response Data
    TS->>TS: Assert Response Data
    
    Note over TS,DB: Full system test with real HTTP communication
    Note over DB: Real database with actual data
```

Let's explore another common strategy:

#### Integration test 

In this approach we test the API endpoint, while interacting with a real database. 
This is why it's called an **integration test** - we test the integration between the API layer and the database layer.

Note that we **don't** run a real app server (like Uvicorn) in this approach, alternatively, we use FastAPI's `TestClient` to simulate HTTP requests to the API endpoints. 
We also **mock the OCI Document AI service calls**, so we don't depend on external services during the test.

```mermaid
sequenceDiagram
    participant TC as Test Code
    participant FTC as FastAPI TestClient
    participant EP as API Endpoints
    participant DB as Real SQLite Database

    TC->>FTC: TestClient.get/post/
    FTC->>EP: Call Endpoint Function
    EP->>DB: Database Operation
    DB-->>EP: Query Results
    EP-->>FTC: Response Object
    FTC-->>TC: Test Response
    TC->>TC: Assert Response
    
    Note over TC,DB: Integration test using TestClient
    Note over DB: Real database operations
```


### API Unit testing + DB integration testing

This approach is divided into two parts:

#### Part I: Unit test - API endpoints only

We test the API endpoints in isolation using FastAPI's `TestClient`,
while mocking the database operations.

```mermaid
sequenceDiagram
    participant UT as Test Code
    participant FTC as FastAPI TestClient
    participant EP as API Endpoints
    participant Mock as Mocked DB Operations

    UT->>UT: Setup Mock Data
    UT->>FTC: client.get/post/put/delete()
    FTC->>EP: Call Endpoint
    EP->>Mock: Call DB Function (Mocked)
    Mock-->>EP: Return Mock Data
    EP-->>FTC: Response with Mock Data
    FTC-->>UT: Test Response
    UT->>UT: Assert Response Logic
    
    Note over UT,Mock: Testing API logic in isolation
    Note over Mock: No real database - mocked responses
```

#### Part I: DB Integration test

We test the database functions directly without going through the API layer.
This allows more flexibility in testing the database operations, as we don't need to pass through an API endpoint.

```mermaid
sequenceDiagram
    participant IT as Integration Tests
    participant DBF as Database Functions
    participant DB as SQLite Database (Real)

    IT->>IT: Setup Test Data
    IT->>DBF: Call DB Function Directly
    DBF->>DB: Execute SQL Query
    DB-->>DBF: Return Query Results
    DBF-->>IT: Function Return Value
    IT->>IT: Assert Data Operations
    IT->>IT: Cleanup Test Data
    
    Note over IT,DB: Testing database layer in isolation
    Note over DB: Real database operations without API layer
```

