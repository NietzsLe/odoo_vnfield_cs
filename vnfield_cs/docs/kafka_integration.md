# 📡 VNField CS - Kafka Integration Documentation

## 📋 Overview

VNField Contractor System (CS) sử dụng Apache Kafka để tích hợp với Integration System (IS) và các contractor sites khác. Hệ thống sử dụng **confluent-kafka** library để đảm bảo high-performance và reliability.

## 🎯 Architecture

```
┌─────────────────┐    📤 Produce     ┌─────────────────┐    📥 Consume    ┌─────────────────┐
│   VNField CS    │ ──────────────→   │  Kafka Cluster  │ ──────────────→  │   VNField IS    │
│  (Contractor)   │                   │                 │                  │ (Integration)   │
└─────────────────┘                   └─────────────────┘                  └─────────────────┘
         ↑                                       │                                    ↓
         │                                       │                                    │
         └─────────────── 📨 Change Propagation ─┴────────────────────────────────────┘
```

## 🏗️ KafkaUtil Class

### Class Definition

```python
class KafkaUtil(models.TransientModel):
    _name = 'vnfield.kafka.util'
    _description = 'Kafka Utility for Producer and Consumer Operations'
```

### 🔧 Core Methods

#### 1. **Producer Method**

```python
kafka_util = self.env['vnfield.kafka.util']
success = kafka_util.produce(
    topic='contractor.updates',
    message={'action': 'create', 'contractor_id': 123},
    headers={'source': 'vnfield_cs', 'entity': 'contractor'}
)
```

#### 2. **Consumer Method**

```python
messages = kafka_util.consume(
    topics=['contractor.updates', 'task.updates'],
    group_id=None,  # Sử dụng contractor-specific group ID
    timeout=5.0,
    max_messages=10
)
```

#### 3. **Connection Test**

```python
result = kafka_util.test_connection()
print(result['message'])  # ✅ Kết nối thành công đến Kafka server
```

## 🏢 Contractor-based Consumer Groups

### Dynamic Group ID Generation

Consumer Group ID được tạo dynamically dựa trên **external_id** của default contractor:

```python
# Format: {base_group}_{external_id}
# Ví dụ: vnfield_cs_consumer_123
group_id = kafka_util.get_consumer_group_id()
```

### Benefits

- **Message Isolation**: Mỗi contractor chỉ consume message của riêng mình
- **Parallel Processing**: Nhiều contractor có thể hoạt động đồng thời
- **Debugging**: Dễ dàng track message theo contractor ID
- **Security**: Phân tách message access theo contractor

## ⚙️ Configuration

### System Parameters

Tất cả cấu hình được quản lý qua **ir.config_parameter**:

| Parameter                         | Default Value         | Description                  |
| --------------------------------- | --------------------- | ---------------------------- |
| `vnfield.kafka.bootstrap_servers` | `localhost:9092`      | Kafka cluster connection     |
| `vnfield.kafka.consumer_group_id` | `vnfield_cs_consumer` | Base consumer group ID       |
| `vnfield.kafka.consumer_timeout`  | `5.0`                 | Polling timeout (seconds)    |
| `vnfield.kafka.max_messages`      | `10`                  | Max messages per consumption |
| `vnfield.kafka.producer_retries`  | `3`                   | Producer retry attempts      |
| `vnfield.kafka.topic_prefix`      | `vnfield_cs`          | Topic naming prefix          |

### Loading Configuration

Parameters được load từ `data/kafka_config.xml` khi install module.

## 📡 Topic Management

### Topic Naming Convention

```python
# Basic topic: vnfield_cs.contractor_updates
topic = kafka_util.build_topic_name('contractor_updates')

# Contractor-specific topic: vnfield_cs.123.contractor_updates
topic = kafka_util.build_topic_name('contractor_updates', include_contractor_id=True)
```

### Recommended Topics

- `contractor.updates`: Contractor CRUD operations
- `task.updates`: Task assignments và status changes
- `project.updates`: Project lifecycle events
- `approval.updates`: Approval workflow events

## 🔄 Message Format

### Producer Message

```json
{
  "action": "create|update|delete",
  "entity": "contractor|task|project|approval",
  "external_id": 123,
  "data": {
    "field1": "value1",
    "field2": "value2"
  },
  "timestamp": "2025-07-17T10:30:00Z",
  "source": "vnfield_cs"
}
```

### Consumer Message Structure

```python
{
    'topic': 'vnfield_cs.contractor_updates',
    'partition': 0,
    'offset': 1234,
    'timestamp': (1, 1721211000000),  # (type, timestamp_ms)
    'headers': {
        'source': 'vnfield_cs',
        'entity': 'contractor',
        'action': 'create'
    },
    'payload': {
        'external_id': 123,
        'data': {...}
    }
}
```

## 🛡️ Error Handling

### Producer Errors

- **Connection failures**: Retry với exponential backoff
- **Delivery failures**: Logged với error details
- **Serialization errors**: Message rejected với error log

### Consumer Errors

- **Polling timeouts**: Graceful handling, không crash
- **JSON decode errors**: Skip message, continue processing
- **Connection errors**: Auto-reconnect với configuration

### Logging Examples

```
✅ Message delivered to contractor.updates [0]
❌ Message delivery failed: Local: Message timed out
🎯 Subscribed to topics: ['contractor.updates'] with group_id: vnfield_cs_consumer_123
⚠️ No default contractor with external_id found, using system parameter
```

## 🚀 Usage Examples

### 1. Producer Usage in Model

```python
class VnfieldContractor(models.Model):
    _inherit = 'vnfield.contractor'

    def write(self, vals):
        result = super().write(vals)

        # Produce change message
        kafka_util = self.env['vnfield.kafka.util']
        kafka_util.produce(
            topic='contractor.updates',
            message={
                'action': 'update',
                'external_id': self.external_id,
                'data': vals
            },
            headers={
                'entity': 'contractor',
                'source': 'vnfield_cs'
            }
        )

        return result
```

### 2. Consumer Usage in Cron Job

```python
@api.model
def _process_kafka_messages(self):
    """Cron job để process Kafka messages"""
    kafka_util = self.env['vnfield.kafka.util']

    topics = [
        'contractor.updates',
        'task.updates',
        'project.updates'
    ]

    messages = kafka_util.consume(topics, max_messages=50)

    for message in messages:
        self._process_message(message)
```

## 🔧 Installation & Setup

### 1. Install Dependencies

```bash
pip install confluent-kafka
```

### 2. Module Dependencies

Thêm vào `__manifest__.py`:

```python
"external_dependencies": {
    "python": ["confluent_kafka"],
}
```

### 3. Configure Default Contractor

Đảm bảo có contractor với `is_default_contractor = True` và `external_id` được set.

### 4. Update System Parameters

Cập nhật `vnfield.kafka.bootstrap_servers` để point đến Kafka cluster thực tế.

## 📊 Monitoring & Debugging

### Health Check

```python
result = self.env['vnfield.kafka.util'].test_connection()
if result['success']:
    print(f"Connected: {result['available_topics']} topics available")
else:
    print(f"Failed: {result['error_details']}")
```

### Log Monitoring

Kafka operations được log với emoji indicators:

- 🚀 Message sent successfully
- ✅ Message delivered
- ❌ Errors và failures
- 🎯 Connection events
- ⚠️ Warnings

### Performance Metrics

- **Producer**: Message delivery time, success rate
- **Consumer**: Message processing rate, lag monitoring
- **Connection**: Availability, topic metadata

## 🔮 Future Enhancements

1. **Message Schemas**: Implement Avro/JSON Schema validation
2. **Dead Letter Queue**: Handle failed messages
3. **Metrics Dashboard**: Real-time monitoring interface
4. **Auto-scaling**: Dynamic consumer scaling
5. **Message Replay**: Reprocess historical messages
6. **Encryption**: Message-level encryption cho sensitive data

---
