# Connections

According to microservices philosophy, each microservice should have its own isolated databases. In our architecture, two microservices are using the same databases and the same messaging queue. Specifically, the service responsible for the [API](../backend/api/) and [Typechecking](../backend/typechecking/) share the following connections:

1. **Redis**: `Typechecking` uses Redis to constantly update the status of tasks. In the case of `API`, it is used to obtain the status of tasks and cache responses to user requests, thus making the server's response speed much more efficient.

2. **MongoDB**: Due to TTL (Time To Live) policies and in order not to overload Redis' capacity, MongoDB is being used to maintain persistence on the status of tasks tracked with Redis. So, if the API layer wanted to check the status of tasks, it would start with Redis, and if it wasn't there, it would check Mongo. In addition, Mongo is also used to store users' `Json Schemas`.

3. **RabbitMQ**: Part of our architecture is based on the Pub/Sub model, where the Publisher is in the `API` microservice, and the Subscriber or Consumer is in `Typechecking`.

In [database](./database/), there is a microservice entirely responsible for tasks related to Redis and MongoDB; and in [messaging](./messaging/), there is the microservice responsible for connecting to the messaging queue in RabbitMQ.
