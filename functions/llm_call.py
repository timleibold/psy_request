from pydantic import BaseModel, Field
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)
from langchain.output_parsers import PydanticOutputParser
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
import os

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


    # 2) Erzeuge den Parser aus Deinem Model
    parser = PydanticOutputParser(pydantic_object=PsychotherapieAntrag)
    format_instructions = parser.get_format_instructions()

    # 3) Baue Dein Prompt
    system = SystemMessagePromptTemplate.from_template(
        "Du bist ein Assistent, der aus dem gegebenen Transkript einen vollständigen Psychotherapie-Antrag "
        "(7-Abschnitte plus Anrede und Signatur) **ausschließlich als JSON** gemäß dem Pydantic-Schema erstellt. "
        "Sprache: Deutsch. Förmlich, keine zusätzlichen Informationen."
    )

    human = HumanMessagePromptTemplate.from_template("""
    Hier das Transkript der Audio-Memo (auf Deutsch):
    \"\"\"{transkript}\"\"\"

    {format_instructions}
    """)

    prompt = ChatPromptTemplate.from_messages([system, human])

    # 4) LLM und Chain initialisieren
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.0,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    chain = LLMChain(
        llm=llm,
        prompt=prompt,
        output_parser=parser
    )

    # 5) Transkript (in einer anderen Zelle definiert)
    # z.B.:
    # transkript_text = """Frau Meier, 38 Jahre, ..."""

    # 6) Aufruf und direktes Parsen
    antrag_obj: PsychotherapieAntrag = chain.predict_and_parse(
        transkript=transkript_text,
        format_instructions=format_instructions
    )
    data = antrag_obj.model_dump()
    return data