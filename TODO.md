# TODOs

## Both

### Unit Testing

Pruebas unitarias a todos los microservicios jejeje

## Typechecking

### Database Connection

Cuando se trabaja con arquitectura de microservicios y varios microservicios comparten la misma base de datos, hay problemas respecto a la arquitectura de microservicios, puesto que, en teoría cada microservicio debería tener su propia base de datos (en caso que la haya). En el caso de los servicios para la capa de la API y typechecking, se comparten la base de datos en Redis y Mongo.

¿Para qué se usa en cada microservicio?

* Typechecking: Utiliza Redis para rastrear el estado de las tareas en RabbitMQ, esto se hace por la rapidez de respuesta de Redis, pero, al mismo tiempo, para no sobrecargar el almacenamiento de Redis, se utiliza Mongo para la permanencia de las tareas anteriormente obtenidas en Mongo.

* API: El uso de Redis aquí es únicamente para cachear las respuestas, de manera general. Pero, puede darse el caso que, un usuario quiera obtener el estado de una tarea, en ese caso, primero se consulta la base de datos en Redis, preguntando por el estado de la tarea, y si no se encuentra, se va a Mongo. En caso de ir a Mongo, nuevamente se cachearía la respuesta en redis, por rapidez.

Por todo lo mencionado, es necesario buscar una manera en la cual se puedan compartir estas bases de datos sin romper la filosofía de los microservicios, teniendo en cuenta también que los microservicios pueden estar en diferentes lenguajes de programación.

Para ellos, he pensado en crear otro servicio (app) que sirva para centralizar las bases de datos, y **comunicarlas entre los servicios API y Typechecking con gRPC**, así no se perdería la filosofía de los microservicios y no habría problemas con los multilenguajes. Así que, como **TODO**, se debe crear ese microservicio y utilizarlo en Typechecking y API.

El servicio de API utiliza otra base de datos, diferente a las antes mencionadas: Postgres. Esta como es únicamente utilizada en una sola capa, se podría dejar así, pero en todo caso, se podría también colocar dentro del nuevo servicio de base de datos. Sea como sea, no es la prioridad.

#### Estado Actual

Ahora mismo ya está implementado las funciones que proveerá este nuevo microservicio, con sus respectivas pruebas unitarias. Un detalle a comentar para que no se pase por alto, es que MongoDB ya guarda el estado de las tareas de Redis, por tanto, también falta implementar unas buenas políticas de TTLs para Redis, y así liberar su carga. Ya con las funciones bien hechas, y probadas con las pruebas unitarias, entonces solo queda crear el servidor gRPC para dejar por terminado este microservicio y la respectiva documentación.

El servidor también está hecho, y parece funcionar de maravillas, solamente queda realizar sus pruebas para comprobar que todo funcione como es debido.

### Messaging Connection

Relacionado al primer punto, algo así pasa con RabbitMQ. Pues, en este software también se hace uso del modelo Pub/Sub (Publisher/Subscriber), en este caso, la capa de la API es la encargada de publicar las tareas en RabbitMQ, y el subscriber o consumer (el servicio typechecking) es el encargado de escuchar constantemente la cola de mensajes y actuar cada que se publiquen tareas a la cola. ¿Cómo se manejaría en este caso?

Se haría lo mismo, un servicio de mensajería, pero deberían ser diferentes por buenas prácticas de programación. Así que sí, se debe implementar gRPC aquí también, para comunicar RabbitMQ a la capa de la API y el servicio de Typechecking.

### API Layer Errors

Después de empezar con el desarrollo de la capa de la API, con el código duplicado que toca solucionar, aparentemente los controladores para los usuarios no están funcionando como deberían, por lo que, la autenticación tampoco lo está haciendo, así que, hay errores que es necesario verificar. En realidad, esto no es prioridad todavía, es primordial lo mencionado en [Database Connection](#database-connection) y [Messaging Connection](#messaging-connection).
