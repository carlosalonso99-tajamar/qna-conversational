import streamlit as st
from dotenv import load_dotenv
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from azure.ai.language.conversations import ConversationAnalysisClient

# Cargar variables de entorno
load_dotenv()
service_endpoint = os.getenv('LS_CONVERSATIONS_ENDPOINT')
service_key = os.getenv('LS_CONVERSATIONS_KEY')
qa_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')

# Definir nombres de proyecto QnA y ejemplos de preguntas por proyecto
project_names = ["CrewAi", "LangGraph"]
example_questions = {
    "CrewAi": [
        "How does the CrewAi agent work?",
        "What are the advantages of the CrewAi agent?",
        "How does the CrewAi system integrate with other systems?",
        "What are the core functionalities of the CrewAi platform?",
        "I'm curious about the Reporting tool used by the system.",
        "Can you explain the deployment process of the CrewAi solution?",
        "How does the CrewAi system enhance operational efficiency?",
        "What security measures does the CrewAi platform implement?",
        "How can the CrewAi solution be customized for enterprise needs?",
        "What support options are available for CrewAi?"
    ],
    "LangGraph": [
        "How is a graph structured in LangGraph?",
        "What are the use cases of LangGraph?",
        "How does LangGraph process complex queries?",
        "What are the main functions of the Reporting tool?",
        "What are the main components of LangGraph's architecture?",
        "How scalable is LangGraph for large datasets?",
        "Could you list the features of the Security tool?",
        "Can you explain the data model behind LangGraph?",
        "How does LangGraph integrate with other systems?",
        "What performance optimizations are built into LangGraph?"
    ]
}

# Inicializar variables en session_state si aún no existen
if "selected_project" not in st.session_state:
    st.session_state.selected_project = project_names[0]
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "intent_data" not in st.session_state:
    st.session_state.intent_data = {"intent": "Esperando entrada...", "entities": []}
if "qna_reply" not in st.session_state:
    st.session_state.qna_reply = ""

def process_question(question):
    try:
        # Análisis de conversación para intenciones y entidades
        credential_lu = AzureKeyCredential(service_key)
        conv_client = ConversationAnalysisClient(
            endpoint=service_endpoint, credential=credential_lu
        )
        lu_project = "Clock"
        lu_deployment = "production"
        with conv_client:
            lu_result = conv_client.analyze_conversation(
                task={
                    "kind": "Conversation",
                    "analysisInput": {
                        "conversationItem": {
                            "participantId": "1",
                            "id": "1",
                            "modality": "text",
                            "language": "en-us",
                            "text": question
                        },
                        "isLoggingEnabled": False
                    },
                    "parameters": {
                        "projectName": lu_project,
                        "deploymentName": lu_deployment,
                        "verbose": True
                    }
                }
            )
        top_intent = lu_result["result"]["prediction"]["topIntent"]
        entities = lu_result["result"]["prediction"].get("entities", [])
        st.session_state.intent_data = {"intent": top_intent, "entities": entities}

        # Determinar el proyecto QnA a usar según las entidades detectadas
        target_model = st.session_state.selected_project
        for entity in entities:
            # Se espera que la entidad tenga un campo "text" extraído (si no, se usa una cadena vacía)
            txt = entity.get("text", "").lower()
            if entity["category"].lower() in ["agent", "framework", "tool"]:
                if "crewai" in txt:
                    target_model = "CrewAi"
                    break
                elif "langgraph" in txt:
                    target_model = "LangGraph"
                    break
        st.session_state.selected_project = target_model

        # Consulta al servicio QnA (respuesta de menor prominencia)
        credential_qna = AzureKeyCredential(service_key)
        qna_client = QuestionAnsweringClient(
            endpoint=service_endpoint, credential=credential_qna
        )
        response = qna_client.get_answers(
            question=question,
            project_name=st.session_state.selected_project,
            deployment_name=qa_deployment_name
        )
        reply = response.answers[0].answer if response.answers else "No se encontró una respuesta relevante."
        st.session_state.qna_reply = reply

        # Guardar el historial de mensajes
        st.session_state.conversation_history.append({"role": "Usuario", "content": question})
        st.session_state.conversation_history.append({"role": "Asistente", "content": reply})
    except Exception as e:
        st.error(f"Error: {e}")

# Título principal
st.title("Azure Chat con Análisis de Intenciones y Entidades")

# Mostrar todos los ejemplos en la barra lateral, agrupados por proyecto
st.sidebar.header("Ejemplos de Preguntas")
for project, questions in example_questions.items():
    st.sidebar.subheader(project)
    for question in questions:
        if st.sidebar.button(question, key=f"{project}_{question}"):
            st.session_state.selected_project = project
            process_question(question)

# Formulario para ingresar la pregunta manualmente
with st.form("chat_form", clear_on_submit=True):
    user_question = st.text_input("Ingresa tu pregunta:")
    submit_button = st.form_submit_button("Enviar")

if submit_button and user_question:
    process_question(user_question)

# Ahora, después de procesar la pregunta, se muestra el proyecto actual actualizado
st.markdown(f"### Hay dos proyectos de QnA\nProyecto actual(Decidico a partir de la intención): **{st.session_state.selected_project}**")

# Mostrar el análisis actualizado después de procesar la pregunta
st.header("Análisis de Intenciones y Entidades")
st.markdown(f"**Intención detectada:** {st.session_state.intent_data['intent']}")
if st.session_state.intent_data["entities"]:
    st.markdown("**Entidades detectadas:**")
    for entity in st.session_state.intent_data["entities"]:
        st.markdown(f"- {entity.get('text', 'N/A')}  _(Categoría: {entity['category']})_")
else:
    st.markdown("No se han detectado entidades.")

# Sección secundaria: Respuesta QnA (Menor importancia)
st.header("Respuesta del QnA")
with st.expander("Mostrar/Ocultar respuesta QnA"):
    st.write(st.session_state.qna_reply)

# (Opcional) Mostrar el historial de mensajes
if st.session_state.conversation_history:
    st.markdown("## Historial de Conversación")
    for msg in st.session_state.conversation_history:
        if msg["role"] == "Usuario":
            st.markdown(f"**Usuario:** {msg['content']}")
        else:
            st.markdown(f"**Asistente:** {msg['content']}")
