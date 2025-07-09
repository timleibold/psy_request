# Install (once) in your venv:
# pip install langchain langchain-ollama streamlit python-dotenv pydantic

from pydantic import BaseModel, Field
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from langchain_ollama.chat_models import ChatOllama  # local chat LLM :contentReference[oaicite:0]{index=0}
import streamlit as st


def LLMCall(transkript_text: str) -> dict:
    # 1) Dein Pydantic-Schema
    class PsychotherapieAntrag(BaseModel):
        anrede: str = Field(..., description="Anrede, z.B. 'Sehr geehrte Frau Dr. Müller,'")
        relevante_soziodemographische_daten: str = Field(
            ..., description="1. Relevante soziodemographische Daten: aktuell ausgeübter Beruf, Familienstand, Zahl der Kinder, Lebenssituation, Geschwister und ähnliches"
        )
        symptomatik_psychischer_befund: str = Field(
            ..., description="2. Symptomatik und psychischer Befund: Von Patientin geschilderte Symptomatik, Angaben zu Schwere und Verlauf; Auffälligkeiten bei Kontaktaufnahme, Interaktion, Erscheinungsbild; psychischer Befund; Krankheitsverständnis"
        )
        somatischer_befund: str = Field(
            ..., description="3. Somatischer Befund / Konsiliarbericht: Somatische Befunde, aktuelle psychopharmakologische Medikation, Vorbehandlungen"
        )
        lebensgeschichtliche_angaben: str = Field(
            ..., description="4. Behandlungsrelevante Angaben zur Lebensgeschichte / Psychosomatik / Systemisches Erklärungsmodell"
        )
        diagnose_zeitpunkt: str = Field(
            ..., description="5. Diagnose zum Zeitpunkt der Antragstellung"
        )
        behandlungsplan_prognose: str = Field(
            ..., description="6. Behandlungsplan und Prognose: Therapieziele, Behandlungsplan, Setting-Begründung, Kooperation"
        )
        signatur: str = Field(
            ..., description="Unterschrift / Signaturblock"
        )

    # 2) Parser
    parser = PydanticOutputParser(pydantic_object=PsychotherapieAntrag)
    format_instructions = parser.get_format_instructions()

    # 3) Prompt-Templates
    system = SystemMessagePromptTemplate.from_template(
        """Du bist ein Assistent, der aus dem gegebenen Transkript einen vollständigen, **ausführlichen und detaillierten** Psychotherapie-Antrag erstellt. 
        Der Antrag besteht aus 6 Abschnitten plus Anrede und Signatur und wird **ausschließlich als JSON** gemäß dem Pydantic-Schema erstellt.
        Stelle sicher, dass alle relevanten Informationen aus dem Transkript **umfassend und gut begründet** in den entsprechenden Abschnitten des Antrags wiedergegeben werden.
        Erfinde keine Daten, sondern nutze ausschließlich die Informationen aus dem Transkript, aber **formuliere sie so detailliert wie möglich** innerhalb der vorgegebenen Struktur.
        """
    )
    human = HumanMessagePromptTemplate.from_template(
        """
        Hier das Transkript der Audio-Memo (auf Deutsch):
        \"\"\"{transkript}\"\"\"

        {format_instructions}
        """
    )
    prompt = ChatPromptTemplate.from_messages([system, human])

    # 4) Lokal: Gemma 3 27B via Ollama
    llm = ChatOllama(
        model="gemma3:27b",        # local model name :contentReference[oaicite:1]{index=1}
        temperature=0.0,
        num_predict=10000
    )

    # 5) Chain
    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=parser
    )

    # 6) Ausführen & Parsen
    antrag_obj = chain.predict_and_parse(
        transkript=transkript_text,
        format_instructions=format_instructions
    )
    return antrag_obj.model_dump()
