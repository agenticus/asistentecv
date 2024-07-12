#Definir las variables manuales
nombre_apellido = 'Nombre Apellido'
nombre = 'Nombre'
titulo = "Título de tu asistente: "
descripcion = 'Descripción'
pregunta_defult = 'pregunta default'

#Importar librerias
from langchain.vectorstores import Pinecone
from langchain.prompts import PromptTemplate 
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import gradio as gr
import os

#Definir variables programáticas
embeddin_model = OpenAIEmbeddings()
vectorstore = Pinecone.from_existing_index("asistentecv", embeddin_model)
template1 = """
        ###INSTRUCCIONES:
        Eres un asistente IA educado y profesional. Debes proveer al usuario información sobre {}

        En tu respuesta POR FAVOR SIEMPRE:
            (0) Se un lector detallista: lee la pregunta y contexto y entiendo ambos antes de responder.
            (1) Comienza tus respuestas con un tono amigable, y reitera la pregunta de manera que el usario está seguro de que la entendiste.
            (2) Si el contexto te permite responder la pregunta, escribe una respuesta detallada y útil con fuentes citadas. SI NO: Si no puedes encontrar la respuesta, indicale al usuario que no encontraste esa información sobre Fernando Rodríguez e invitale a entrevistarlo.
            (3) Debajo de tu respuesta, por favor lista todas las fuentes citadas (ejemplo: un párrafo donde se sustenta tu respuesta)

        Piensa paso a paso.
        ###.format(nombre_apellido)

        Responde la siguiente pregunta utilizando el contexto brindado.""".format(nombre_apellido)
        
template2 = """        
        ### Pregunta: {question} ###

        ### Contexto: {context} ###



        ### Respuesta con fuentes:
        """
template = template1 + template2

#Elementos de la cadena langchain
llm = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0, openai_api_key=os.getenv('OPENAI_API_KEY'))
#Instanciamos el retreaver que recuperará los documentos similares a la consulta del usuario
retriever = vectorstore.as_retriever()
prompt = PromptTemplate.from_template(template)
#Crear chain
chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

#Wraper function
def get_answer(question):
    answer = chain.invoke(question)
    return answer

#Desplegar interfaz de Gradio
iface = gr.Interface(fn=get_answer, inputs=gr.Textbox(
    value=pregunta_defult),
        outputs="markdown",
        title=titulo,
        description=descripcion,
        examples=[["Qué estudió {}?".format(nombre_apellido)],
                ["Cuáles son sus principales debilidades?"],
                ["{} sabe algo de cocina tailandesa?".format(nombre)]],
    theme=gr.themes.Soft(),
    allow_flagging="never",)

iface.launch()