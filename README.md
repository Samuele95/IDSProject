# IDSProject

Project for "Ingegneria del Software" exam, bachelor degree in Computer Science, Università degli Studi di Camerino.
The client application is shipped as a Streamlit application. Server application is intended to be used as a service within a machine. 

## Software architecture
Traditional web application architecture with a REST approach which includes:

* Data tier: Data persistence service on relational databases;
* Logic tier: CRUD functionality on data according to a language-agnostic REST-API interface, validation of data entered into the system (pre-conditions), computation of data independent of the information provided at client level post-conditions);
* Presentation tier: Interaction service with the API provided at server level, with stateless mode or without context storage between client and server, in order to facilitate decoupling between the two components which must enjoy operational autonomy.

Data tier and logic tier are the components of the Server-side of the application.
Presentation tier, together with a specific API client, are the components of the Client-side of the application.

## Technologies used

Python programming language has been chosen as the main programming language of this project due to its dynamic typing and code readability features. In order to speed-up development processes, several ready-to-use frameworks have been used for both server and client side of the project:

* Server side: Django web framework; Django REST Framework for API building; Drf-spectacular for Swagger-UI API documentation.
* Client side: Streamlit app
