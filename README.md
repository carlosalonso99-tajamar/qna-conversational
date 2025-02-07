# Funcionamiento de la Aplicación

## Azure Chat con Análisis de Intenciones y Entidades

La aplicación integra los servicios de análisis de lenguaje y QnA de Azure para ofrecer una experiencia de chat interactiva. Su funcionamiento se puede resumir en los siguientes pasos:

### 1. Ingreso y Selección de Preguntas
- El usuario puede ingresar manualmente una pregunta o seleccionar una de las preguntas de ejemplo disponibles en la barra lateral.
- Las preguntas de ejemplo están agrupadas por proyecto (**CrewAi** y **LangGraph**) y cada una incluye una referencia explícita (por ejemplo, "CrewAi agent" o "LangGraph") para facilitar la detección de la entidad correspondiente.

### 2. Análisis de Conversación
- Al enviar una pregunta, la aplicación utiliza el `ConversationAnalysisClient` de Azure para identificar la intención principal y extraer las entidades presentes en el texto.
- Con base en las entidades detectadas, se determina de forma dinámica el proyecto a utilizar (**CrewAi** o **LangGraph**). Este cambio se refleja inmediatamente en la interfaz.

### 3. Consulta al Servicio QnA
- Una vez seleccionado el proyecto, se utiliza el `QuestionAnsweringClient` de Azure para consultar una respuesta que se ajuste a la pregunta planteada.
- La respuesta obtenida se muestra en la interfaz en una sección expandible (con menor prominencia).

### 4. Visualización de Resultados
La UI muestra:
- **El análisis de intenciones y entidades**: Se despliega la intención detectada y una lista de entidades extraídas.
- **La respuesta del QnA**: Disponible dentro de un `expander`.
- **El historial de conversación**: Un registro de todas las preguntas y respuestas intercambiadas durante la sesión.

Este flujo permite que la aplicación adapte su comportamiento en tiempo real según el contenido de la pregunta, actualizando inmediatamente el proyecto de consulta (**CrewAi** o **LangGraph**) según la entidad detectada y proporcionando respuestas relevantes del servicio QnA de Azure.
