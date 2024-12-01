# Hands-on: Message Brokers

The project demonstrates an event-driven system with use of RabbitMQ as a message broker.
The system processes users' messages, filtering for stop words, converting text to uppercase, and sending emails.
A Pipes-and-Filters version of the system is developed for performance comparison.

The system consists of four independent services, which communicates asynchronously via RabbitMQ:

- REST API Service receives user messages via POST requests.
- Filter Service filters messages containing specific stop words (bird-watching, ailurophobia, mango).
- SCREAMING Service converts messages to uppercase.
- Publish Service sends processed messages via email.

The Pipes-and-Filters implementation uses the same services, but connects them using in-memory pipes instead of a broker. Each service operates as a separate process.

**Testing report:**

| Metric |	Event-Driven System |	Pipes-and-Filters System |
|--------|----------------------|--------------------------|
|Average Latency|	0.08 seconds |	18.84 seconds |
|Average CPU Usage|	6.05%|	3.83% |
|Average Memory Usage|	88.41%	|86.61% |

**Observations:**
Event-Driven is faster and more scalable due to asynchronous processing, though slightly higher CPU usage.
Pipes-and-Filters simplified design with lower CPU overhead, but significantly higher latency due to sequential processing.

**Steps to Run:**
1. Start a RabbitMQ broker using Docker:
   
   `docker run -d --hostname rabbitmq --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management`
2. Create a .env file in the pipes and publish directories

3 (a). Run Event-Driven
   - Navigate to message_brokers/message_broker
   - Start each service in separate terminals
     
3 (b). Run Pipes-and-Filters
   - Navigate to message_brokers/pipes
   - Run main.py
