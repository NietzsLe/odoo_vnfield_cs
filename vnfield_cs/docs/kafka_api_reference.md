# 📚 KafkaUtil API Reference

## 📋 Class Overview

```python
from odoo import models, api

class KafkaUtil(models.TransientModel):
    _name = 'vnfield.kafka.util'
    _description = 'Kafka Utility for Producer and Consumer Operations'
```

---

## 🔧 Configuration Methods

### `get_bootstrap_servers()`

Lấy Kafka bootstrap servers từ system parameters.

**Returns**: `str` - Bootstrap server connection string

**Example**:

```python
kafka_util = self.env['vnfield.kafka.util']
servers = kafka_util.get_bootstrap_servers()
# Returns: "localhost:9092"
```

---

### `get_consumer_group_id()`

Tạo consumer group ID dựa trên external_id của default contractor.

**Returns**: `str` - Consumer group identifier

**Logic**:

1. Tìm default contractor với `is_default_contractor = True`
2. Nếu có external*id: `{base_group}*{external_id}`
3. Nếu không: fallback to system parameter

**Example**:

```python
group_id = kafka_util.get_consumer_group_id()
# Returns: "vnfield_cs_consumer_123" (nếu external_id = 123)
```

---

### `get_default_contractor_external_id()`

Lấy external_id của default contractor.

**Returns**: `int|None` - External ID hoặc None nếu không tìm thấy

**Example**:

```python
external_id = kafka_util.get_default_contractor_external_id()
# Returns: 123 hoặc None
```

---

### `get_consumer_timeout()`

Lấy consumer polling timeout từ system parameters.

**Returns**: `float` - Timeout in seconds

---

### `get_max_messages()`

Lấy maximum số messages per consumption.

**Returns**: `int` - Max messages count

---

### `get_producer_retries()`

Lấy số lần retry cho producer.

**Returns**: `int` - Retry count

---

### `get_topic_prefix()`

Lấy topic prefix từ system parameters.

**Returns**: `str` - Topic prefix

---

## 🏗️ Utility Methods

### `build_topic_name(base_name, include_contractor_id=False)`

Tạo topic name với prefix và optional contractor ID.

**Parameters**:

- `base_name` (str): Base topic name
- `include_contractor_id` (bool): Include contractor external_id trong topic name

**Returns**: `str` - Formatted topic name

**Examples**:

```python
# Basic topic
topic = kafka_util.build_topic_name('contractor_updates')
# Returns: "vnfield_cs.contractor_updates"

# Contractor-specific topic
topic = kafka_util.build_topic_name('contractor_updates', include_contractor_id=True)
# Returns: "vnfield_cs.123.contractor_updates"
```

---

### `validate_topics(topics)`

Validate và normalize topic names.

**Parameters**:

- `topics` (str|list): Topic name hoặc list of topic names

**Returns**: `list` - Validated list of topic names

**Raises**: `ValueError` - Nếu input không hợp lệ

**Examples**:

```python
# String input
topics = kafka_util.validate_topics('single_topic')
# Returns: ['single_topic']

# List input
topics = kafka_util.validate_topics(['topic1', 'topic2'])
# Returns: ['topic1', 'topic2']
```

---

## 📤 Producer Methods

### `produce(topic, message, headers=None)`

Produce message đến Kafka topic.

**Parameters**:

- `topic` (str): Kafka topic name
- `message` (dict): Message payload
- `headers` (dict, optional): Message headers

**Returns**: `bool` - True if successful, False if failed

**Configuration**:

```python
producer_config = {
    'bootstrap.servers': self.get_bootstrap_servers(),
    'client.id': f'{prefix}_{external_id}_producer',
    'acks': 'all',
    'retries': self.get_producer_retries(),
    'retry.backoff.ms': 100,
    'delivery.timeout.ms': 30000,
    'request.timeout.ms': 25000
}
```

**Message Processing**:

1. JSON serialize message với UTF-8 encoding
2. Convert headers to Kafka format
3. Send với delivery callback
4. Flush để ensure delivery

**Example**:

```python
success = kafka_util.produce(
    topic='contractor.updates',
    message={
        'action': 'create',
        'external_id': 123,
        'data': {'name': 'New Contractor'}
    },
    headers={
        'source': 'vnfield_cs',
        'entity': 'contractor'
    }
)

if success:
    print("Message sent successfully")
```

**Error Handling**:

- Connection errors → logged và return False
- Serialization errors → logged và return False
- Delivery failures → callback logging

---

## 📥 Consumer Methods

### `consume(topics, group_id=None, timeout=None, max_messages=None)`

Consume messages từ Kafka topics.

**Parameters**:

- `topics` (list): List of topic names to consume
- `group_id` (str, optional): Consumer group ID (defaults to contractor-specific)
- `timeout` (float, optional): Polling timeout (defaults to system parameter)
- `max_messages` (int, optional): Max messages to consume (defaults to system parameter)

**Returns**: `list` - List of consumed messages

**Configuration**:

```python
consumer_config = {
    'bootstrap.servers': self.get_bootstrap_servers(),
    'group.id': group_id,
    'client.id': f'{prefix}_{external_id}_consumer',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 1000,
    'session.timeout.ms': 30000,
    'heartbeat.interval.ms': 10000
}
```

**Message Structure**:

```python
{
    'topic': 'vnfield_cs.contractor_updates',
    'partition': 0,
    'offset': 1234,
    'timestamp': (1, 1721211000000),
    'headers': {'source': 'vnfield_cs'},
    'payload': {'action': 'create', 'data': {...}}
}
```

**Example**:

```python
messages = kafka_util.consume(
    topics=['contractor.updates', 'task.updates'],
    max_messages=50
)

for message in messages:
    print(f"Received from {message['topic']}: {message['payload']}")
```

**Processing Logic**:

1. Subscribe to topics
2. Poll messages với timeout
3. Handle partition EOF gracefully
4. Parse JSON payload
5. Extract headers
6. Return structured message data

**Error Handling**:

- Polling timeouts → graceful exit
- JSON decode errors → skip message, continue
- Consumer errors → logged và break loop
- Connection cleanup → always executed

---

## 🔍 Testing Methods

### `test_connection()`

Test Kafka server connectivity.

**Returns**: `dict` - Connection test results

**Return Structure**:

```python
{
    'success': bool,                    # Connection success status
    'message': str,                     # Human-readable message
    'bootstrap_servers': str,           # Server configuration
    'available_topics': list,           # List of available topics (if successful)
    'error_details': str|None          # Error details (if failed)
}
```

**Test Process**:

1. Create test producer với short timeouts
2. Request topic metadata
3. Validate response
4. Return detailed results

**Example**:

```python
result = kafka_util.test_connection()

if result['success']:
    print(f"✅ {result['message']}")
    print(f"📊 Available topics: {len(result['available_topics'])}")
else:
    print(f"❌ {result['message']}")
    print(f"🔍 Error: {result['error_details']}")
```

---

## 🎯 System Parameter Dependencies

| Parameter Key                     | Default Value         | Type   | Description              |
| --------------------------------- | --------------------- | ------ | ------------------------ |
| `vnfield.kafka.bootstrap_servers` | `localhost:9092`      | string | Kafka cluster connection |
| `vnfield.kafka.consumer_group_id` | `vnfield_cs_consumer` | string | Base consumer group ID   |
| `vnfield.kafka.consumer_timeout`  | `5.0`                 | float  | Consumer polling timeout |
| `vnfield.kafka.max_messages`      | `10`                  | int    | Max messages per batch   |
| `vnfield.kafka.producer_retries`  | `3`                   | int    | Producer retry count     |
| `vnfield.kafka.topic_prefix`      | `vnfield_cs`          | string | Topic naming prefix      |

---

## 🏢 Contractor Dependencies

### Required Fields

```python
# vnfield.contractor model cần có:
is_default_contractor = fields.Boolean()  # Identify default contractor
external_id = fields.Integer()            # External system mapping
```

### Search Logic

```python
default_contractor = self.env['vnfield.contractor'].search([
    ('is_default_contractor', '=', True)
], limit=1)
```

---

## 🚨 Exception Handling

### Common Exceptions

- `json.JSONDecodeError`: Invalid message format
- `confluent_kafka.KafkaError`: Kafka server errors
- `ValueError`: Invalid input parameters
- `ConnectionError`: Network connectivity issues

### Error Recovery

1. **Producer**: Retry với exponential backoff
2. **Consumer**: Skip invalid messages, continue processing
3. **Connection**: Fallback to system parameters
4. **Logging**: Comprehensive error details

---

## 🔄 Client ID Patterns

### Naming Convention

- **Producer**: `{prefix}_{external_id}_producer`
- **Consumer**: `{prefix}_{external_id}_consumer`
- **Test**: `{prefix}_{external_id}_test_producer`

### Examples

```
vnfield_cs_123_producer
vnfield_cs_123_consumer
vnfield_cs_123_test_producer
```

### Benefits

- **Tracking**: Easy identification trong Kafka tools
- **Isolation**: Separate connections per contractor
- **Debugging**: Clear connection ownership

---
