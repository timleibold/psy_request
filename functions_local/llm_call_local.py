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
        Es ist sehr wichtig, dass du sehr ausführlich bleibst. Verwerte **alle** gegebenen Informationen aus dem Transkript. 
        Gib jede einzelne Information aus dem Transkript wieder—auch vermeintlich kleine Details (z. B. ADHS der Tochter, Reha-Maßnahme, Nahrungsmittelunverträglichkeiten des Ehemanns usw.).
        Gib mindestens 3.000 Token aus, um sicherzustellen, dass der Antrag sehr ausführlich ist!
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

    # 4) Lokal: DeepSeek R1 32B via Ollama
    llm = ChatOllama(
        model="deepseek-r1:32B",        # local model name :contentReference[oaicite:1]{index=1}
        temperature=0.0,
        num_predict=7000
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

if __name__ == '__main__':
    # Beispiel-Transkript
    beispiel_transkript = """
Hallo, mein Name ist Hans Müller. Ich berichte über eine Patientin mit dem anonymisierten Code von Z290361. Die Patientin ist verheiratet, hat einen Sohn, minus 22 Jahre, Beruf Architekt und eine Tochter, plus 24 Jahre, Beruf Studentin. Ihr Mann ist berentet. Sie arbeitet aktuell 40 Stunden als Betreuungsassistentin in Teilzeit. Gemeinsam mit ihrem Sohn und ihrer Tochter und ihrem Ehemann bewohnt sie ein Einfamilienhaus. Finanzielle Sorgen bestehen nicht. Zur Symptomatik, die Patientin berichtet seit mehreren Jahren unter Schlafstörungen, innerer Unruhe, gereizter Stimmung, Versagensgefühlen, Schuldgefühlen, verminderten Selbstwort, emotionaler Instabilität, Energieverlust, Konzentrationsstörungen, Verlust der Lebensfreude und Zukunftsängsten zu leiden. Sie selbst gibt an, in einem Pflegeheim zu arbeiten und täglich die Arbeit kranker Kollegen oder der Arbeit von unbesetzten Stellen mitarbeiten zu müssen. Ihr Mann leidet seit vielen Jahren unter chronischen Kopfschmerzen, unter Rheuma und sei aus diesem Grund auch schon teilberendet. Er habe mehrere Nahrungsmittelunverträglichkeiten und sie erwarte von ihr, dass sie darauf achte, dass seine Ernährung den Erkrankungen angepasst werde. Er selbst würde sich wenig um seine Gesundheit kümmern und sie hätte das als zusätzliche Aufgabe. Durch eine Therapie erhofft sie sich, die Belastungsgrenzen besser zu erkennen, rechtzeitig zu erkennen, ihre eigenen Bedürfnisse in den Vordergrund zu stellen und dadurch mehr eigene Werte zu finden und diese auch zu leben und insgesamt ihre Lebenskraft und Lebensfreude wiederzufinden. Psychischer Befund, es erscheint eine wache, bewusstseinsklare, zu allen Qualitäten adäquat orientierte Patientin. Im Kontakt ist sie ja unsicher und schüchtern, freundlich aber zugewandt. Im formalen Gedankengang besteht Grübeln. Inhaltlich zeigen sich Befürchtungen, den alltäglichen beruflichen Anforderungen nicht mehr gewachsen zu sein. Die Gedächtnis- und Aufmerksamkeitsfunktionen sind unauffällig. Es bestehen keine Hinweise auf Wahrnehmungs- oder Ich-Störungen. Sie rauchen nicht und trinken keinen Alkohol. Von Suizidalität distanziert sie sich glaubhaft. Zum somatischen Befund, siehe beiliegender ärztlicher Konsiliarbericht, die behandlungsrelevanten Angaben zur Lebensgeschichte und Krankheitsgeschichte. Die Patientin gibt an, zwei Geschwister zu haben, einmal minus drei Jahre Beruf Ärztin, einmal minus vier Jahre Krankenpfleger. Zu beiden Geschwistern bestehe kaum Kontakt. Sie seien in der Jugend von ihren Eltern deutlich bevorzugt worden, weil sie die besseren Noten in der Schule hatte und deutlich leistungsorientierter waren. Sie habe auf ihre Geschwister öfter aufpassen müssen. Sie haben auch im Haushalt viele Aktivitäten der Mutter abnehmen müssen. Seit vielen Jahren bestehe zu den Geschwistern kaum Kontakt, zu ihrer Mutter mäßiger Kontakt. Ihre Mutter, plus 29 Jahre berentet, beschreibt sie als sehr dominant und fordernd. Sie habe sich wenig um die Kinder und deren Bedürfnisse gekümmert. Sie habe sich in allen ihren Bedürfnissen ihrem Ehemann untergeordnet. Der Vater, plus 31 Jahre, Beruf Maurer, sei sehr dominant und egozentrisch gewesen. Er sei häufig impulsiv und unberechenbar gewesen. Er habe seine Frau geschlagen und auch grundlos seine Kinder. Er habe regelmäßig Alkohol getrunken, sei betrunken von der Arbeit nach Hause gekommen. Und die Mutter habe von den Kindern erwartet, dass sie wortlos dieses Verhalten hinnehmen sollten und das auch innerhalb der Familie bleibt und nicht nach außen getragen wird. Beide Eltern sind mittlerweile alt und sie müsse sich um ihre Eltern kümmern. Sie fühle sich deutlich überlastet, denn es kommt zusätzlich zu der Arbeitstätigkeit noch dazu. Ihr Mann ist nur eingeschränkt in der Lage, sich um den Garten zu kümmern. Auch dieser bleibt ihr übrig in der Versorgung. Genau, ihre Kinder kämen regelmäßig nach Hause, sie hätten eine sehr gute Beziehung. Keines der Kinder sei verheiratet, Enkelkinder gibt es keine. Damals habe sie ein immer braves Kind sein müssen, ihre Eltern unterstützen müssen und ihre Geschwister versorgen sollen. Ihre Bedürfnisse und Wünsche hätten die Eltern in keinster Weise interessiert. Sie habe sich komplett dem Leben ihrer Mutter und ihres Vaters angeschlossen. Bis heute würden die Eltern immer wieder ihre Hilfe einfordern und sie traue sich kaum, diese abzulehnen. Sie selbst hat zunächst die Grundschule im Anschluss der Realschule besucht und hat dann eine Ausbildung zum technischen Zeichner gemacht. Der Beruf hat ihr nie Spaß gemacht, den hatten die Eltern für sie ausgesucht. Vor einigen Jahren hat sie eine Ausbildung zum Betreuungsassistenten gemacht, seit der Arbeit sie in diesem Beruf. Im Krankenhaus wie im Pflegeheim sind immer weniger, sind die Stellen unterbesetzt. Also der Stellenschlüssel kann nicht ausgefüllt werden. Sie muss jeden Tag Überstunden machen. Sie kann die Überstunden nicht abfeiern, sondern sie müssen ausbezahlt werden. Dazu kommt, dass auch ihre Eltern nachts sie immer wieder stören, anrufen und sagen, sie müsse vorbeikommen, der Vater sei gestürzt und sie müsse den Notarzt rufen und sich um sie kümmern. Sie machen ihr konstant Vorwürfe, da sie glauben, dass sie insgesamt zu wenig für sie da ist. Ihr Mann macht ihr Vorwürfe, weil sie sich nicht adäquat um ihn kümmert. Ihre Kinder fordern natürlich ihre Aufgabe als Mutter auch ein. Sie fühlt sich immer weiter hilflos im Umgang mit den Problemen. Urlaub und Unternehmung könnte sie sich nicht leisten aus finanziellen Gründen. Die Tochter leidet zusätzlich unter ADHS und ist natürlich sehr anstrengend dadurch. Sie ist sehr sprunghaft in ihren Gedanken und auch in ihrem Verhalten und in keinster Weise ruhig und ausgeglichen. Von März bis Mai letztes Jahr hat sie an einer Reha-Maßnahme teilgenommen. Im Jahr zuvor war sie in einer psychosomatischen Klinik für sechs Wochen und möchte jetzt nach der Kurzzeittherapie mit einer Langzeittherapie diese fortführen. Die Makroanalyse, sie hat gelernt in früher Kindheit, dass sie sich anderen Menschen unterordnen muss, deren Bedürfnissen und Erwartungen und Lebensweisen und Wünschen, dass sie sie nicht nur annehmen, sondern auch erfüllen muss. Die Relevanz der Belastungsgrenze und Abgrenzungsfähigkeit wurde nicht vermittelt. Sie lernte eigene Bedürfnisse an Dritte zurückzustellen, andere zu unterstützen und für sie ein unproblematisches Kind, später eine immer angepasste und leistungsorientierte Ehefrau und auch leistungsorientierte und stets hilfsbereite und nach außen orientierte Mitarbeiterin zu sein. Dies alles ist der Entwicklung eines gesunden Selbstwertes und einer adäquaten Abgrenzungsfähigkeit nicht zuträglich. Daraus entwickelte sich das Selbstbild. Ich bin nur dann wertvoll, wenn ich die Werte anderer übernehme und deren Erwartungen erfülle und folgendes Weltbild, die anderen sehen nicht mich, sondern nur meine Anpassungsfähigkeit und Leistungsbereitschaft. Denn daran wird mein Wert gemessen. Ihre zeitüberdauernde situationsunabhängige hohe Leistungsorientierung angelehnt an die Bedürfnisse ihrer Umgebung beruflich wie privat bei gleichzeitiger Vernachlässigung eigener Interessen und Wertvorstellungen führte zu einer Hilflosigkeit und Überforderung. Dazu kam der Rückzug aus sozialen Kontakten und Freundschaften, der zu einer immer größer werdenden sozialen Isolation und einen Verlust an positiven Verstärkern führte weiterhin zu erneuten depressiven Symptomen. In der Aktualgenese stellt sich die Problematik folgendermaßen vor. Der Vorgesetzte bittet sie, am Wochenende einen Dienst ihrer Kollegen zu übernehmen, da sie einen leistungsabhängigen Selbstwert und hohe Harmoniebedürftigkeit, sehr einen instabilen Selbstwert, hat Angst vor Ablehnung in zwischenmenschlichen Beziehungen, sind ihre Gedanken, ich muss die bitte erfüllen, ich nehme mich und meine Bedürfnisse zurück und stelle die meiner Vorgesetzten in den Vordergrund, denn ich bin nur dann für andere wertvoll, wenn ich ihre Bedürfnisse erfülle. Emotional zeigt sich daraus Traurigkeit, Ärger, Wut auf sich selbst und den Vorgesetzten. Auf Verhaltensebene zeigt sie das Verhalten, dass sie den anderen den Wunsch erfüllt. Was natürlich rückwirkend dann zu einer Spannungsreduktion kurzfristig führt, zu einer Vermeidung der Konfrontation mit anderen Kollegen oder Vorgesetzten. Langfristig werden die Schuldgefühle wieder stark, der Selbstwert sinkt, die depressive Symptomatik nimmt zu und die dysfunktionalen Kognitionsmuster bestätigen sich. Die Diagnose zum Zeitpunkt der Antragstellung liegt bei F33.1. Die Therapieziele in der Therapie sind einmal ein gutes therapeutisches Bündnis, im Rahmen einer vertrauensvollen, tragfähigen, therapeutischen Beziehung durch komplementäre Beziehungsgestaltung und Transparenz, Strukturierung und Ressourcenaktivierung. Sie soll lernen, die eigene Stimmung funktional zu beeinflussen und zu stabilisieren. Ein plausibendes Erklärungsmodell vor dem Hintergrund der Bedingungs- und Funktionsanalyse soll erarbeitet werden. Die angenehmen Aktivitäten sollen geplant und gesteigert werden und ebenfalls über einen Aktivitätenplan körperliche Aktivitäten. Der Selbstwert soll ebenfalls gesteigert werden. Im sokratischen Dialog sollen die dysfunktionalen Kognitionen identifiziert und auch verändert werden, durch kognitive Umstrukturierung mit Neubewertung, wie zum Beispiel, Ich muss den Erwartungen meiner Vorgesetzten entsprechen, denen meines Mannes, meiner Tochter und meiner Eltern, mich deren Wünschen und Forderungen unterordnen. Dagegen steht, ich darf meine Belastungsgrenze wahrnehmen, bitten ablehnen, ich darf lernen, Nein zu sagen, ich muss mich und meine Bedürfnisse in den Vordergrund stellen und ich muss nicht der Leistungserwartung der anderen entsprechen. Ich bin ein wertvoller Mensch, auch ohne die Bewertung meiner Leistung von außen. Ein nächster Punkt ist die Aufbau und Erweiterung und Training sozialer Fertigkeiten durch therapeutische Rollenspiele und Teilen des Assertiveness-Trainingsprogramms, zum Beispiel Angst vor Ablehnung oder Verlust von Bindung beim Äußern oder der Befriedigung eigener Bedürfnisse thematisieren. Stellen sollen thematisiert werden, hier Stellen von Forderungen wie eine angemessene Arbeitszeit im Pflegeheim, keine Extradienste, nicht immer für alle an mich herangetragenen Aufgaben zur Verfügung stehen und nicht alle Krankheitsfälle ausgleichen müssen. Kritik an Arbeitskollegen und Vorgesetzten, sich trauen zu äußern, eigene Gefühle mitteilen, eigene Werte kreieren und danach leben, soziale Kontakte herstellen, aufarbeiten. Am Ende noch eine Erarbeitung und Entwicklung positiver, kurz- und mittelfristiger Zukunftsperspektiven in Verbindung mit der Reflexion der eigenen Bedürfnisse, Werte und Lebensziele, Erarbeitung eines Lebensplans für rückfallkritische Situationen. Die Prognose ist natürlich sehr gut, da die Patientin pünktlich zu den Terminen kommt, sie regelmäßig und verlässlich ihre Hausaufgaben erledigt, hochmotiviert mitarbeitet, sehr reflektiert ist, einen hohen Leidensdruck hat und ein deutlicher Wunsch zu erkennen ist, dass sie ihre depressiven Symptome verbessern will, ihr Selbstwertgefühl erhöhen und ihre Abräsungsfähigkeit besser wahrnehmen möchte. Sie will ein funktionierendes Umfeld aufbauen und Vorgesetzten gegenüber ihre Wünsche kundtun, um wieder mehr Lebenskraft, mehr Lebensfreude und Lebensmut zu erfahren. Also insgesamt kann man sagen, als prognostisch günstig sind ihre hohe Motivation, Zuverlässigkeit zu sehen, die Prognose ist als ausreichend günstig anzusehen. Zusammenfassung des bisherigen Therapieverlaufs, die therapeutische Beziehung gestaltet sich sehr gut, mit Hilfe von einem Wochenplan konnten positive Aktivitäten aufgebaut werden, wie sie geht regelmäßig zum Sport, geht mit Freundinnen spazieren und lernt so auf die eigene Stimmung Einfluss zu nehmen. Durch die Disputation dysfunktionaler Gedanken, wie ich muss die erwartete Leistung erfüllen, konnten nach und nach funktionale Kognitionsmuster und Beziehungsmuster erarbeitet und auch eingesetzt werden. Beruflich hat sie es geschafft, öfter Nein zu sagen, ihre freien Tage auch so zu nutzen, dass sie gar nicht zur Verfügung steht, dass sie auf Kurzurlaube geht. Besonders schwierig ist die Beziehung zu ihren Eltern. Wenn da ein Notruf abgegeben wird, fühlt sie sich natürlich verpflichtet, da hinzugehen, aber immer öfter kann sie auch mal ihren Bruder anrufen oder aber ihre Kinder bitten, da hinzugehen und muss das nicht alleine machen. Allerdings fällt es ihr da noch schwer, sich abzugrenzen und die Erwartung, die an sie gesetzt wird, abzulehnen. Bis heute spielt die internalisierte Erwartung, du musst deine Rolle als Tochter, Ehefrau, Mutter und Betreuungsassistentin perfekt erledigen, egal in welchem Setting, eine große Rolle. Ansonsten besucht sie die Eltern nur noch gelegentlich, bietet ihnen nur gelegentlich Unterstützung an oder wenn sie explizit eingefordert wird. Im folgenden Therapieabschnitt sollen bereits erzielte Therapiefolge ausgebaut werden und die weitere Entwicklung bezüglich Fokussierung, Durchsetzung eigener Wünsche, Bedürfnisse und Grenzen gefördert werden. Es sollen soziale Kompetenzen erweitert werden, Abgrenzungen im sozialen Kontext eingeübt werden. Ein weiteres Ziel ist die Rückfallprophylaxe. Hier sollte ein individueller Krisenplan erstellt werden. Die Sitzungen sollen im wöchentlichen Turnus stattfinden. Es wird eine Langzeittherapie mit 36 Stunden beantragt.
    """
    # Aufruf
    antrag_dict = LLMCall(beispiel_transkript)
    print(antrag_dict)
    # Optional: DOCX erstellen
    from functions_local.create_docx import create_docx
    create_docx(antrag_dict)

