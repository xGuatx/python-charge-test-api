# Python API Load Testing Tool

Python script to perform load tests on APIs, with performance measurement and response validation.

## Description

Load testing tool that sends parallel HTTP requests to an API and measures:
- Response time
- HTTP codes
- JSON structure validation
- Performance statistics

Primarily used to test the **shoturl** API (screenshot capture) but adaptable to any API.

## Prerequisites

- Python 3.6+
- `curl` installed on the system

## Installation

```bash
# No external Python dependencies required
# Uses only the standard library
```

## Usage

### Configuration

Modify the variables in `requestsCharge.py`:

```python
# Data sent to the API
data = {"url": "https://google.com", "delay": 1}

# Expected keys in JSON response
EXPECTED_KEYS = {"request_id", "screenshot", "session_id"}

# API endpoint
"https://192.168.164.5/capture_screenshot"
```

### Run the test

```bash
python requestsCharge.py
```

## Features

### Parallel tests

Uses `ThreadPoolExecutor` to send multiple simultaneous requests:

```python
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(send_curl_request) for _ in range(100)]
```

### Collected metrics

For each request:
- **HTTP Status Code**: Response code (200, 500, etc.)
- **Total Time**: Total request time (according to curl)
- **Elapsed Time**: Time measured in Python
- **Response Validation**: Verification of expected JSON keys

### Statistics

Displays:
- Average response time
- Min/Max
- Success rate
- Validation errors

## Script structure

```python
def send_curl_request():
    """
    Sends a curl request with:
    - POST /capture_screenshot
    - Content-Type: application/json
    - Timeout: 90s
    """

# Response validation
js = json.loads(body)
keys = set(js)
if not EXPECTED_KEYS.issubset(keys):
    # Log validation error
```

## Test example

Testing a screenshot API:

```bash
python requestsCharge.py
```

Example output:
```
Sending 100 requests...
 95 success
 5 errors
Average time: 2.3s
Min time: 1.8s
Max time: 4.1s
```

## Configuration for other APIs

To test another API, modify:

1. **Endpoint URL**:
```python
"https://your-api.com/endpoint"
```

2. **POST data**:
```python
data = {"param1": "value1", "param2": "value2"}
```

3. **Response validation**:
```python
EXPECTED_KEYS = {"field1", "field2", "field3"}
```

4. **Number of workers and requests**:
```python
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(send_curl_request) for _ in range(500)]
```

## Security notes

 **IMPORTANT**:
- Uses `-k` (insecure) in curl to accept self-signed certificates
- Should be modified for production
- Do not use to test public APIs without permission
- Respect API rate limiting

## Limitations

- No automatic retry management
- Fixed timeout of 90 seconds
- Simple validation (presence of JSON keys)
- No graphics/advanced metrics

## Possible improvements

- [ ] Support for different HTTP methods (GET, PUT, DELETE)
- [ ] HTML report generation
- [ ] Performance graphs
- [ ] Authentication support (Bearer token, API key)
- [ ] Configuration via YAML file
- [ ] CSV result export

## Main Use Case

Originally created to test the **shoturl** API which generates website screenshots:
- Server load testing
- Response format validation
- Screenshot generation time measurement

## License

Personal project - Test use
