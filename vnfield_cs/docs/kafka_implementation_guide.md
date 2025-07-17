# 🚀 VNField CS - Kafka Implementation Guide

## 📋 Overview

Hướng dẫn này cung cấp step-by-step instructions để implement và sử dụng Kafka integration trong VNField Contractor System.

---

## 🛠️ Setup & Installation

### 1. Dependencies Installation

#### Python Package

```bash
# Install confluent-kafka package
pip install confluent-kafka==2.3.0
```

#### Odoo Module Configuration

Trong `__manifest__.py`:

```python
{
    "external_dependencies": {
        "python": ["confluent_kafka"],
    },
}
```

### 2. Kafka Server Setup

#### Local Development (Docker)

```bash
# Start Kafka với Docker Compose
docker-compose up -d

# Tạo topics
docker exec kafka kafka-topics --create --topic contractor.updates --bootstrap-server localhost:9092
docker exec kafka kafka-topics --create --topic task.updates --bootstrap-server localhost:9092
```

#### Production Setup

- Configure Kafka cluster với multiple brokers
- Set up proper security (SASL/SSL)
- Configure retention policies
- Monitor cluster health

### 3. VNField Configuration

#### System Parameters

Cập nhật via Odoo interface hoặc data files:

```xml
<record id="kafka_bootstrap_servers" model="ir.config_parameter">
    <field name="key">vnfield.kafka.bootstrap_servers</field>
    <field name="value">your-kafka-server:9092</field>
</record>
```

#### Default Contractor

Đảm bảo có contractor được set như default:

```python
contractor = self.env['vnfield.contractor'].create({
    'name': 'Default Site Contractor',
    'is_default_contractor': True,
    'external_id': 123  # Important: phải có external_id
})
```

---

## 🔧 Implementation Patterns

### 1. Producer Implementation trong Models

#### Basic Producer Pattern

```python
class VnfieldContractor(models.Model):
    _inherit = 'vnfield.contractor'

    def _send_kafka_message(self, action, data=None):
        """Helper method để send Kafka messages"""
        kafka_util = self.env['vnfield.kafka.util']

        message = {
            'action': action,  # create, update, delete
            'entity': 'contractor',
            'external_id': self.external_id,
            'data': data or {},
            'timestamp': fields.Datetime.now().isoformat(),
            'source': 'vnfield_cs'
        }

        headers = {
            'entity': 'contractor',
            'action': action,
            'source': 'vnfield_cs',
            'external_id': str(self.external_id or '')
        }

        return kafka_util.produce(
            topic='contractor.updates',
            message=message,
            headers=headers
        )

    @api.model
    def create(self, vals):
        contractor = super().create(vals)

        # Send create message
        contractor._send_kafka_message('create', vals)

        return contractor

    def write(self, vals):
        result = super().write(vals)

        # Send update message cho mỗi contractor
        for contractor in self:
            contractor._send_kafka_message('update', vals)

        return result

    def unlink(self):
        # Send delete messages trước khi delete
        for contractor in self:
            contractor._send_kafka_message('delete')

        return super().unlink()
```

#### Advanced Producer với Error Handling

```python
def _send_kafka_message_with_retry(self, action, data=None, max_retries=3):
    """Send Kafka message với retry logic"""
    for attempt in range(max_retries):
        try:
            success = self._send_kafka_message(action, data)
            if success:
                _logger.info(f'✅ Kafka message sent successfully on attempt {attempt + 1}')
                return True
            else:
                _logger.warning(f'⚠️ Kafka message failed on attempt {attempt + 1}')
        except Exception as e:
            _logger.error(f'❌ Kafka message error on attempt {attempt + 1}: {str(e)}')

        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff

    _logger.error(f'❌ Failed to send Kafka message after {max_retries} attempts')
    return False
```

### 2. Consumer Implementation

#### Cron Job Consumer

```python
class KafkaConsumerCron(models.Model):
    _name = 'vnfield.kafka.consumer'
    _description = 'Kafka Message Consumer'

    @api.model
    def process_kafka_messages(self):
        """
        Cron job để consume Kafka messages
        Schedule: Chạy mỗi 30 giây
        """
        kafka_util = self.env['vnfield.kafka.util']

        topics = [
            'contractor.updates',
            'task.updates',
            'project.updates',
            'approval.updates'
        ]

        try:
            messages = kafka_util.consume(
                topics=topics,
                timeout=10.0,
                max_messages=100
            )

            _logger.info(f'📥 Processing {len(messages)} Kafka messages')

            for message in messages:
                self._process_single_message(message)

        except Exception as e:
            _logger.error(f'❌ Kafka consumer error: {str(e)}')

    def _process_single_message(self, message):
        """Process single Kafka message"""
        try:
            payload = message['payload']
            headers = message['headers']

            entity = headers.get('entity')
            action = headers.get('action')

            if entity == 'contractor':
                self._process_contractor_message(payload, action)
            elif entity == 'task':
                self._process_task_message(payload, action)
            elif entity == 'project':
                self._process_project_message(payload, action)
            else:
                _logger.warning(f'⚠️ Unknown entity type: {entity}')

        except Exception as e:
            _logger.error(f'❌ Error processing message: {str(e)}')

    def _process_contractor_message(self, payload, action):
        """Process contractor-specific message"""
        external_id = payload.get('external_id')
        data = payload.get('data', {})

        if action == 'create':
            # Create local contractor record
            pass
        elif action == 'update':
            # Update existing contractor
            pass
        elif action == 'delete':
            # Soft delete contractor
            pass
```

#### Real-time Consumer với Threading

```python
import threading
from queue import Queue

class RealtimeKafkaConsumer(models.Model):
    _name = 'vnfield.kafka.realtime'

    def __init__(self):
        super().__init__()
        self.message_queue = Queue()
        self.consumer_thread = None
        self.running = False

    def start_consumer(self):
        """Start background consumer thread"""
        if not self.running:
            self.running = True
            self.consumer_thread = threading.Thread(target=self._consume_loop)
            self.consumer_thread.daemon = True
            self.consumer_thread.start()

    def _consume_loop(self):
        """Background consumer loop"""
        kafka_util = self.env['vnfield.kafka.util']

        while self.running:
            try:
                messages = kafka_util.consume(
                    topics=['high_priority.updates'],
                    timeout=1.0,
                    max_messages=10
                )

                for message in messages:
                    self.message_queue.put(message)

            except Exception as e:
                _logger.error(f'❌ Realtime consumer error: {str(e)}')
                time.sleep(5)
```

---

## 🎯 Message Patterns

### 1. Standard Message Format

#### CRUD Operations

```python
# CREATE message
{
    "action": "create",
    "entity": "contractor",
    "external_id": 123,
    "data": {
        "name": "New Contractor",
        "email": "contractor@example.com"
    },
    "timestamp": "2025-07-17T10:30:00Z",
    "source": "vnfield_cs"
}

# UPDATE message
{
    "action": "update",
    "entity": "contractor",
    "external_id": 123,
    "data": {
        "email": "new-email@example.com"  # Only changed fields
    },
    "timestamp": "2025-07-17T10:35:00Z",
    "source": "vnfield_cs"
}

# DELETE message
{
    "action": "delete",
    "entity": "contractor",
    "external_id": 123,
    "timestamp": "2025-07-17T10:40:00Z",
    "source": "vnfield_cs"
}
```

#### Workflow Events

```python
# Task assignment
{
    "action": "assign",
    "entity": "task",
    "external_id": 456,
    "data": {
        "assignee_id": 789,
        "deadline": "2025-07-20T23:59:59Z"
    },
    "workflow_state": "assigned",
    "timestamp": "2025-07-17T10:30:00Z",
    "source": "vnfield_cs"
}

# Approval request
{
    "action": "request_approval",
    "entity": "approval",
    "external_id": 101,
    "data": {
        "approver_ids": [111, 222],
        "description": "Budget approval required"
    },
    "workflow_state": "pending",
    "timestamp": "2025-07-17T10:30:00Z",
    "source": "vnfield_cs"
}
```

### 2. Message Headers

#### Standard Headers

```python
headers = {
    'entity': 'contractor|task|project|approval',
    'action': 'create|update|delete|assign|approve|reject',
    'source': 'vnfield_cs',
    'external_id': '123',
    'priority': 'high|medium|low',
    'correlation_id': 'unique-request-id'
}
```

#### Routing Headers

```python
headers = {
    'destination': 'contractor_123,contractor_456',  # Target contractors
    'routing_key': 'vnfield.cs.contractor.updates',
    'message_type': 'command|event|query'
}
```

---

## 🔄 Error Handling Strategies

### 1. Producer Error Handling

#### Delivery Guarantee

```python
def produce_with_guarantee(self, topic, message, headers=None):
    """Produce message với delivery guarantee"""
    kafka_util = self.env['vnfield.kafka.util']

    # Add message ID cho tracking
    message['message_id'] = str(uuid.uuid4())

    success = kafka_util.produce(topic, message, headers)

    if not success:
        # Store failed message cho retry
        self.env['vnfield.failed.message'].create({
            'topic': topic,
            'message': json.dumps(message),
            'headers': json.dumps(headers or {}),
            'retry_count': 0,
            'created_at': fields.Datetime.now()
        })

    return success
```

#### Retry Mechanism

```python
@api.model
def retry_failed_messages(self):
    """Cron job để retry failed messages"""
    failed_messages = self.env['vnfield.failed.message'].search([
        ('retry_count', '<', 5),
        ('next_retry', '<=', fields.Datetime.now())
    ])

    for failed_msg in failed_messages:
        success = self._retry_message(failed_msg)

        if success:
            failed_msg.unlink()
        else:
            failed_msg.write({
                'retry_count': failed_msg.retry_count + 1,
                'next_retry': fields.Datetime.now() + timedelta(
                    minutes=2 ** failed_msg.retry_count
                )
            })
```

### 2. Consumer Error Handling

#### Message Validation

```python
def _validate_message(self, message):
    """Validate consumed message"""
    payload = message.get('payload', {})

    required_fields = ['action', 'entity', 'timestamp']

    for field in required_fields:
        if field not in payload:
            raise ValueError(f'Missing required field: {field}')

    # Validate external_id
    if payload.get('external_id') and not isinstance(payload['external_id'], int):
        raise ValueError('external_id must be integer')

    return True
```

#### Dead Letter Queue

```python
def _handle_poison_message(self, message, error):
    """Handle messages that cannot be processed"""
    self.env['vnfield.dead.letter'].create({
        'topic': message['topic'],
        'partition': message['partition'],
        'offset': message['offset'],
        'message': json.dumps(message),
        'error': str(error),
        'created_at': fields.Datetime.now()
    })

    _logger.error(f'💀 Message moved to dead letter queue: {error}')
```

---

## 📊 Monitoring & Logging

### 1. Performance Monitoring

#### Message Metrics

```python
class KafkaMetrics(models.Model):
    _name = 'vnfield.kafka.metrics'

    def track_message_sent(self, topic, success=True):
        """Track sent message metrics"""
        self.env['vnfield.kafka.stats'].create({
            'type': 'producer',
            'topic': topic,
            'success': success,
            'timestamp': fields.Datetime.now()
        })

    def track_message_consumed(self, topic, processing_time):
        """Track consumed message metrics"""
        self.env['vnfield.kafka.stats'].create({
            'type': 'consumer',
            'topic': topic,
            'processing_time': processing_time,
            'timestamp': fields.Datetime.now()
        })
```

#### Health Checks

```python
@api.model
def kafka_health_check(self):
    """Scheduled health check"""
    kafka_util = self.env['vnfield.kafka.util']

    result = kafka_util.test_connection()

    if not result['success']:
        # Send alert
        self.env['vnfield.alert'].create({
            'type': 'kafka_connection_failed',
            'message': result['message'],
            'severity': 'critical'
        })
```

### 2. Structured Logging

#### Log Format

```python
import logging
import json

kafka_logger = logging.getLogger('vnfield.kafka')

def log_kafka_event(event_type, data):
    """Structured Kafka event logging"""
    log_entry = {
        'timestamp': fields.Datetime.now().isoformat(),
        'event_type': event_type,
        'contractor_id': data.get('contractor_id'),
        'external_id': data.get('external_id'),
        'topic': data.get('topic'),
        'success': data.get('success', True),
        'error': data.get('error'),
        'processing_time': data.get('processing_time')
    }

    if log_entry['success']:
        kafka_logger.info(json.dumps(log_entry))
    else:
        kafka_logger.error(json.dumps(log_entry))
```

---

## 🚀 Deployment Checklist

### Pre-deployment

- [ ] Kafka cluster setup và accessible
- [ ] Network connectivity test
- [ ] Security configuration (SASL/SSL)
- [ ] Topic creation và retention policies
- [ ] System parameters configuration
- [ ] Default contractor setup với external_id

### Deployment

- [ ] Install confluent-kafka package
- [ ] Update module dependencies
- [ ] Run database upgrade
- [ ] Verify system parameters loaded
- [ ] Test Kafka connection
- [ ] Enable cron jobs

### Post-deployment

- [ ] Monitor message flow
- [ ] Check error logs
- [ ] Verify consumer group creation
- [ ] Test failover scenarios
- [ ] Performance baseline measurement

### Production Monitoring

- [ ] Set up alerting cho connection failures
- [ ] Monitor consumer lag
- [ ] Track message throughput
- [ ] Monitor error rates
- [ ] Regular health checks

---
