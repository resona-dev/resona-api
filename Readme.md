# Resona API

Resona allows you to register jobs that will call your API with the given parameters at a specified time.

## Capabilities

- Register a job for a specific time
- Register a job to be triggered after some delay
- Register recurring jobs (cron)

## Usage of the API

### Register a Job

To register a job, send a POST request to the `/jobs` endpoint with the job details.

#### Request

`POST /jobs`
`Content-Type: application/json`

```json
{
  "name": "My Job",
  "request": {
    "url": "http://example.com/endpoint",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer token"
    },
    "body": {
      "key": "value"
    }
  },
  "trigger": {
    "delay": 5
  }
}
```

Trigger can be one of:

```json
{
    "delay": number
}
```

```json
{
    "date": datetime iso string
}
```

```json
{
    "cron": cron expression
}
```

#### Response

`HTTP/1.1 201 Created`
`Content-Type: application/json`

```json
{
  "id": "job_id",
  "name": "My Job",
  "created_at": "2023-09-01T10:00:00Z",
  "next_run_time": "2023-10-01T10:00:00Z",
  "status": "active",
  "trigger": {
    "type": "one-time",
    "fields": {
      "date": "2023-10-01T10:00:00Z"
    }
  },
  "request": {
    "url": "http://example.com/endpoint",
    "method": "POST",
    "headers": {
      "Authorization": "Bearer token"
    },
    "body": {
      "key": "value"
    }
  },
  "result": null
}
```

### Update a Job

To update a job, send a POST request to the /jobs/{job_id} endpoint with the updated job details.

#### Request

```json
POST /jobs/{job_id}
Content-Type: application/json

{
  "name": "My Job",
  "request": {
    "url": "http://example.com/updated-endpoint",
    "method": "PUT",
    "headers": {
      "Authorization": "Bearer updated_token"
    },
    "body": {
      "key": "updated_value"
    }
  },
  "trigger": {
    "delay": 5
  }
}
```

#### Response

```json
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "job_id",
  "name": "Updated Job",
  "created_at": "2023-09-01T10:00:00Z",
  "next_run_time": "2023-10-01T10:00:00Z",
  "status": "active",
  "trigger": {
    "type": "cron",
    "fields": {
      "cron": "0 0 * * *"
    }
  },
  "request": {
    "url": "http://example.com/updated-endpoint",
    "method": "PUT",
    "headers": {
      "Authorization": "Bearer updated_token"
    },
    "body": {
      "key": "updated_value"
    }
  },
  "result": null
}
```

### Get All Jobs

To retrieve all jobs, send a GET request to the /jobs endpoint.

#### Request

```json
GET /jobs/{job_id}
```

#### Response

```json
HTTP/1.1 200 OK
Content-Type: application/json
[
  {
    "id": "job_id",
    "name": "My Job",
    "created_at": "2023-09-01T10:00:00Z",
    "next_run_time": "2023-10-01T10:00:00Z",
    "status": "active",
    "trigger": {
      "type": "one-time",
      "fields": {
        "date": "2023-10-01T10:00:00Z"
      }
    },
    "request": {
      "url": "http://example.com/endpoint",
      "method": "POST",
      "headers": {
        "Authorization": "Bearer token"
      },
      "body": {
        "key": "value"
      }
    },
    "result": null
  }
]
```

There are also endpoints for pausing, resuming and deleting jobs.
