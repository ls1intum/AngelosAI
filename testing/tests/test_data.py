from testing.test_data_models.qu_data import QAData

qa_objects = [
    QAData(
        question = "Ich studiere Wirtschaftsinformatik im Masterstudiengang. Ich möchte nächste Semester meine Masterarbeit schreiben, damit ich bevor Februar 2024 meine Masterarbeit abgeben kann. Ich habe schon seit zwei Monaten versucht, auf der Website jedes Lehrstuhls nach Themen zu suchen, aber es gab nicht viele Themen. Meiner E-Mails erhalten meistens keine Antwort oder nur Ablehnung. Selbst wenn ich eine Antwort erhalte, ist das Thema nicht für mich geeignet. Wie kann ich einen Antrag für Themasuchen beim Prüfungsausschuss stellen?",
        answer = "Manchmal gestaltet sich die Suche nach einer Abschlussarbeit etwas schwierig. Deshalb bieten wir auch jedes Semester eine Veranstaltung zu diesem Thema an. Eine Aufzeichnung finden Sie in unserem Moodlekurs, Link dazu hier: cit.tum.de/cit/studienfachberatung-informatik. Und noch ein paar Tipps zur Suche: Bitte überprüfen Sie nochmal die Art und Weise Ihrer Bewerbung. Fügen Sie Ihren Anfragen Lebenslauf, Übersicht über die zum Themenbereich passenden, belegten Module sowie ein kurzes Motivationsschreiben an. Setzen Sie den Professor des Lehrstuhls und vielleicht auch Sekretariat in cc. Fragen Sie nach ein paar Tagen nach, wenn Sie keine Antwort bekommen! Wenn Sie sich bewerben, so fixieren Sie sich auch nicht auf ein spezielles Thema, sondern geben Sie den Bereich an, der Sie interessiert und dazu passende Kenntnisse. Vielleicht passen diese ja auch in den Forschungsbereichs des Lehrstuhls, bei dem Sie sich bewerben. Browsen Sie bitte auf den Lehrstuhlseiten nach ausgeschriebenen Themen, da finden Sie auch offene Themen. Manchmal hilft es auch, persönlich vorbeizugehen oder um einen kurzen persönlichen Termin zu bitten. Es passiert  nur äußerst selten, dass jemand, der Informatik studiert, kein passendes Thema findet. Zwar könnten wir in so einem Fall ein Thema zuweisen, aber Sie hätten dann keinen Einfluss darauf und müssten evtl. an einem für Sie nur mäßig interessanten Thema arbeiten, das nicht unbedingt in dem von Ihnen gewünschten Bereich liegt. Auch wäre diese Zuweisung ein aufwendiger Prozess, der ein paar Wochen dauert.",
        classification = "master-information-systems",
        key_facts = [
            "Überprüfen Sie die Art und Weise Ihrer Bewerbung.",
            "Fügen Sie Lebenslauf, belegte Module und Motivationsschreiben an.",
            "Setzen Sie den Professor und das Sekretariat in cc.",
            "Fixieren Sie sich nicht auf ein spezielles Thema, sondern einen Bereich.",
            "Persönlich vorbeigehen oder einen kurzen Termin anfragen.",
            "Die Zuweisung eines Themas ist ein aufwendiger Prozess."
        ],
        expected_sources = [
            "cit.tum.de/cit/studienfachberatung-informatik"
        ],
        label = "THESIS1"
    ),
    QAData(
        question = "Ich wollte mal nachfragen wo genau man die Bachelorarbeit abgeben soll. Auf der Webseite steht nur wo man es abgibt wenn man vor dem 15.01. angefangen hat, jedoch ist das bei mir nicht der Fall. Außerdem wollte ich fragen. Da bei mir steht, dass mein Abgabedatum der 11.07 ist. Kann ich dann bis zum 11.07.24 23:59 abgeben oder muss das VOR dem 11.07 abgegeben sein.",
        answer = "ich nehme an, dass Ihre Arbeit über das CIT-Portal angemeldet wurde. Die Abgabe erfolgt im Portal. Sie laden dort eine digitale Version Ihrer Bachelorarbeit hoch. Späteste Abgabe ist am 11.07. 23:59. Allerdings empfehle ich Ihnen dringend, dass Sie schon etwas früher abgeben, um auf der sicheren Seite zu sein, dass technisch alles klappt.",
        key_facts = [
            "Die Abgabe erfolgt im CIT-Portal.",
            "Späteste Abgabe ist am 11.07. um 23:59.",
            "Es wird empfohlen, die Arbeit früher abzugeben, um technische Probleme zu vermeiden."
        ],
        classification = "general",
        expected_sources = [
            "CIT-Portal"
        ],
        label = "THESIS2"
    ),
    QAData(
        question = "My thesis submission deadline is on the 15th of July. When submitting my thesis on Koinon, do I need to and how do I attach further documents such as transcripts?",
        answer = "There is no need to upload transcripts or the like. Your thesis is sufficient. Just as it would have been, had you printed it and handed it in.",
        key_facts = [
            "No need to upload transcripts or further documents.",
            "The thesis is sufficient for submission."
        ],
        classification = "general",
        expected_sources = [],
        label = "THESIS3"
    ),
    QAData(
        question = "I recently did my masters in informatics thesis at the chair of media technology at TUM. I wanted to inquire where do I have to submit the thesis apart from the CIT portal. Should I print out physical copies at submit them at the informatics desk as well?",
        answer = "Unless you made other arrangements with the chair, it is sufficient to upload the document to the CIT portal. There is no need to print it and hand it in physically.",
        key_facts = [
            "Upload the thesis to the CIT portal is sufficient.",
            "No need to submit physical copies unless arrangements with the chair have been made."
        ],
        classification = "Master Informatik",
        expected_sources = [],
        label = "THESIS4"
    ),
    QAData(
        question = "Ich wollte fragen ob ich mir für meinen Master Informatik theoretisch die zwei einzelnen Sprachkurse Französisch A1.1 und A1.2 (je 3 Ects) oder den Blockkurs (6 Ects) (nicht meine Muttersprache) für überfachliche Grundlagen anrechnen lassen kann?",
        answer = "ja, das ist möglich. Siehe auch: https://www.cit.tum.de/cit/studium/studierende/ueberfachliche-grundlagen/#c451",
        key_facts = [
            "Es ist möglich, sich die Sprachkurse anrechnen zu lassen.",
            "Der Blockkurs oder die beiden einzelnen Kurse können angerechnet werden."
        ],
        classification = "Master Informatik",
        expected_sources = [
            "https://www.cit.tum.de/cit/studium/studierende/ueberfachliche-grundlagen/#c451"
        ],
        label = "COURSE1"
    ),
    QAData(
        question =  "Ich bin Student im B.Sc. Informatik, im zweiten Semester. Ich habe im ersten Semester das Modul Spanisch A1 als Wahlmodul überfachliche Grundlagen ausgewählt und habe es erfolgreich bestanden. In meinem Leistungsnachweis zählen diese ECTS Credits jedoch nicht als Wahlmodule überfachliche Grundlagen, sondern als Zusatzleistungen. Warum ist das so? und was könnte ich tun, damit meine Credits als überfachliche Grundlagen zählen?",
        answer = "Die Sprachkurse des Sprachzentrums müssen Ihrem Studiengang häufig zugeordnet werden. Bitte gehen Sie wie hier (https://www.cit.tum.de/cit/studium/studierende/ueberfachliche-grundlagen/ --> Informatik  --> Sprachkurse  --> Einbringung von Sprachkursen) beschrieben vor.",
        key_facts = [
            "Sprachkurse müssen Ihrem Studiengang zugeordnet werden.",
            "Der Prozess zur Einbringung von Sprachkursen ist auf der Webseite beschrieben."
        ],
        classification = "Bachelor Informatik",
        expected_sources = [
            "https://www.cit.tum.de/cit/studium/studierende/ueberfachliche-grundlagen/"
        ],
        label = "COURSE2"
    ),
    QAData(
        question = "Ich werde im nächsten Semester ein freiwilliges Praktikum absolvieren und plane, ein Erholungssemester zu beantragen.Ich würde gerne erfahren, welche Schritte ich unternehmen muss, um ein Erholungssemester zu beantragen und welche Unterlagen hierfür erforderlich sind. Zudem möchte ich wissen, ob es bestimmte Fristen gibt, die ich einhalten muss.",
        answer = "Alle Informationen zu einem Urlaubssemester finden Sie auf folgender Webseite: https://www.tum.de/studium/im-studium/das-studium-organisieren/beurlaubung. Sie benötigen eine Stellungnahme der Studienfachberatung, senden Sie uns dazu bitte die unter cit.tum.de/cit/tipps-informatik -> Industriepraktika genannten Dokumente zu. Die Frist zum Beantragen einer Beurlabung für das Wintersemester 2024/25 ist der erste Vorlesungstag, also der 14. Oktober 2024.",
        key_facts = [
            "Alle Informationen zum Urlaubssemester sind auf der Webseite.",
            "Stellungnahme der Studienfachberatung wird benötigt.",
            "Die Frist zum Beantragen eines Urlaubssemesters ist der erste Vorlesungstag."
        ],
        classification = "general",
        expected_sources = [
            "https://www.tum.de/studium/im-studium/das-studium-organisieren/beurlaubung",
            "cit.tum.de/cit/tipps-informatik"
        ],
        label = "LEAVE1"
    ),
    QAData(
        question = "Ich plane im vom 11. November - 10. März meine Bachelorarbeit zu schreiben. Idealerweise will ich zum SS/25 meinen Master hier an der TUM anfangen, aber das wird wahrscheinlich zu knapp, da die letzte Note des Bachelors 4 Wochen nach Vorlesungsbeginn in TUMonline sein muss (soweit ich weiß). Wann darf die Note frühstens kommen, damit ich noch ein weiteres Semester im Bachelor studieren darf? Geht der Antrag auf Anerkennung zwischen Bachelor und Master auch über die Credittransfer INTUM Seite oder gibt es hier eine einfachere Möglichkeit?",
        answer = "Sie werden zum Ende des Semesters exmatrikuliert in dem Ihre Abschlussdokumente fertiggestellt werden. Das bedeutet für Sie konkret, dass Sie sich am besten bereits für den Master bewerben und falls Sie dann die Note doch nicht rechtzeitig für den Übergang bekommen, bleiben Sie im Bachelor immatrikuliert und verschieben Ihren Studienbeginn ins nächste Wintersemester. Zwei Dinge müssen Sie in diesem Fall beachten: zum Einen dürfen Sie nicht vergessen, sich für das WS wieder zu bewerben und wenn Sie dann im Master immatrikuliert sind, müssen Sie einen Anerkennungsantrag stellen, damit die Leistungen, die Sie im Bachelor für den Master erbracht haben, auch mit Ihnen in den Master 'wandern'. Alle Infos zum Anerkennungsprozess finden Sie hier: cit.tum.de/cit/anerkennung-informatik. Wenn es wider Erwartens doch rechtzeitig mit der Benotung klappen sollte und Sie Ihr Zeugnis vor Immatrikulationsfrist (5 Wochen nach Vorlesungsbeginn, also vor dem 27.05.25) beantragen, dann hat das Service Büro in der Vergangenheit Ihren Abschluss direkt gemeldet und Sie können den Masterstudiengang bereits im SoSe anfangen. Das würde ich jetzt mal nicht ausschließen wollen, wenn Sie am 10.03. Ihre Arbeit abgeben.",
        key_facts = [
            "Sie werden am Ende des Semesters exmatrikuliert, in dem die Abschlussdokumente fertiggestellt werden.",
            "Bewerben Sie sich schon für den Master und bleiben Sie im Bachelor, falls die Note nicht rechtzeitig kommt.",
            "Sie können den Studienbeginn ins nächste Wintersemester verschieben, wenn die Note zu spät kommt.",
            "Sie müssen sich für das WS neu bewerben und einen Anerkennungsantrag stellen.",
            "Falls die Note rechtzeitig kommt und das Abschlusszeugnis vor dem 27.05.25 beantragt wird, können Sie das Masterstudium im Sommersemester beginnen."
        ],
        classification = "general",
        expected_sources = [
            "cit.tum.de/cit/anerkennung-informatik"
        ],
        label = "THESIS5"
    ),
    QAData(
        question="Ich habe mich für Informatik beworben, erfülle aber die Voraussetzungen nicht. Ich bin vor einigen Jahren nach Deutschland gezogen und meine Noten haben unter der Sprache gelitten. Ich plane, Elektrotechnik und Informationstechnik zu studieren und später auf Informatik umsteigen. Wäre das möglich? Gibt es eine andere Möglichkeit, zugelassen zu werden?",
        answer="Die Zulassungsvoraussetzungen werden sich wahrscheinlich nicht wesentlich verändern, so dass nicht garantiert ist, dass Sie zu einem späteren Zeitpunkt eine Zulassung erhalten. Wenn Sie meinen, Sie möchten sich später für einen Masterstudiengang bewerben, dann können Sie die Zulassungsvoraussetzungen hier (https://www.cit.tum.de/cit/studium/studiengaenge/master-informatik/) nachlesen. Wenn Sie Informatik studieren möchten, können sich aber auch an anderen Unis und Hochschulen bewerben. Vielleicht klappt's da ja eher?",
        key_facts=[
            "Die Zulassungsvoraussetzungen werden sich wahrscheinlich nicht ändern.",
            "Es gibt keine Garantie, dass Sie später zugelassen werden.",
            "Sie können sich an anderen Universitäten und Hochschulen bewerben."
        ],
        classification="Bachelor Informatik",
        expected_sources=[
            "https://www.cit.tum.de/cit/studium/studiengaenge/master-informatik/"
        ],
        label = "ADMISSION1"
    ),
    QAData(
        question="Wenn ich in den Informatikkurse teilnehme und in dem Sommersemester als Quereinsteiger wechsele, werden meine Zulassungschancen dadurch beeinflusst? Und sind die Zulassungsvoraussetzungen in der zweiten Semester genauso gleich?",
        answer="Nein, ein - in dem Fall abgebrochenes - Vorstudium beeinflusst Ihre Chancen auf eine Zulassung weder positiv noch negativ. Sie würden ja auch nicht quereinsteigen, sondern später einsteigen. Was Einfluss auf die Zulassung hat, ist ausführlich auf unseren Internetseiten erklärt (https://www.cit.tum.de/cit/studium/studiengaenge/bachelor-informatik/  -->Zulassung  -->Stufe 1: Prüfung Ihrer Unterlagen). Wenn Sie in einem höheren Fachsemester einsteigen möchten, dann sind die Bedingungen die gleichen und zusätzlich müssen Sie noch eine gewisse Anzahl an Credits mitbringen. Auch dies können Sie unter oben referenzierter URL nachlesen.",
        key_facts=[
            "Ein abgebrochenes Vorstudium beeinflusst die Zulassungschancen nicht.",
            "Die Zulassungsvoraussetzungen bleiben in höheren Fachsemestern gleich.",
            "Zusätzliche Credits sind erforderlich für höhere Fachsemester."
        ],
        classification="Bachelor Informatik",
        expected_sources=[
            "https://www.cit.tum.de/cit/studium/studiengaenge/bachelor-informatik/"
        ],
        label = "ADMISSION2"
    ),
    QAData(
        question="Ich befinde mich im zweiten Semester und ziehe in Erwägung, mein Studienfach auf Wirtschaftsinformatik zu wechseln. Um eine fundierte Entscheidung über diesen möglichen Wechsel treffen zu können, möchte ich die Möglichkeit erkunden, einige Wirtschaftsinformatik-Module in meinen aktuellen Studienplan aufzunehmen, ohne zu diesem Zeitpunkt offiziell den Studiengang zu wechseln. Mein Ziel ist es, mein Interesse und meine Eignung für das Fach zu bewerten und einen reibungsloseren Übergang zu ermöglichen, falls ich mich für einen Wechsel entscheide und um die Übertragung der Credits zu erleichtern. Könnten Sie mir bitte zu den folgenden Punkten Auskunft geben: Die Machbarkeit der Einschreibung in Wirtschaftsinformatik-Module, während ich im BWL-Studiengang bleibe. Spezifische Module, die Sie empfehlen würden und die gut sowohl zu TUM-BWL als auch zu Wirtschaftsinformatik passen. Der Prozess, um sicherzustellen, dass die erworbenen Credits aus diesen Wirtschaftsinformatik-Modulen nahtlos übertragen werden können, falls ich mich für einen Studiengangswechsel entscheide. Mögliche Auswirkungen auf meinen Studienplan und meinen Studienfortschritt.",
        answer="Sie können die meisten Wirtschaftsinformatik Module als Freifach in Ihrem aktuellen Studiengang belegen und auch an Prüfungen teilnehmen. Sobald Sie sich entschlossen haben, den Studiengang zu wechseln, müssen Sie sich entsprechend bewerben und wenn Sie eine Zulassung bekommen und immatrikuliert sind, können Sie einen Anerkennungsantrag für die Module, die auch in Ihrem dann aktuellen Studiengang verankert sind, stellen. Alle Infos dazu finden Sie hier: cit.tum.de/cit/anerkennung-informatik. Da ich die TUM-BWL Studiengänge nicht kenne, kann ich Ihnen auch keine Module empfehlen. Lesen Sie sich am besten die Modulbeschreibungen sorgfältig durch und entscheiden selbst, was Sie interessiert und was gut passt. Der Prozess ist unter oben genanntem Link beschrieben.",
        key_facts=[
            "Wirtschaftsinformatik-Module können als Freifach belegt werden.",
            "Nach der Zulassung können Module in den neuen Studiengang integriert werden.",
            "Der Anerkennungsprozess ist auf der Webseite beschrieben."
        ],
        classification="Bachelor Wirtschaftsinformatik",
        expected_sources=[
            "cit.tum.de/cit/anerkennung-informatik"
        ],
        label = "COURSE3"
    ),
    QAData(
        question="Ich habe alle meine Noten für den Bachelorabschluss beisammen und möchte einige zusätzliche Leistungen in den Master übertragen. Ich studiere gerade noch den Informatik Bachelor und werde den Informatik Master nächstes Semester starten. Muss ich bei der Beantragung der Abschlussdokumente etwas beachten, damit ich die Leistungen übertragen kann? Außerdem wollte ich fragen, wie ich die Übertragung der Leistungen dann beantragen muss.",
        answer="Am besten kontaktieren Sie die für Ihren Studiengang verantwortliche Schriftführung und besprechen mit ihr, welche Module in Ihren Bachelor einfließen sollen und welche Sie für den Master 'aufsparen'. Sobald Sie im Master immatrikuliert sind, können Sie einen Anerkennungsantrag stellen. Alle Infos hierzu finden Sie hier: cit.tum.de/cit/anerkennung-informatik",
        key_facts=[
            "Kontaktieren Sie die Schriftführung für die Aufteilung der Module zwischen Bachelor und Master.",
            "Nach der Immatrikulation in den Master können Sie einen Anerkennungsantrag stellen."
        ],
        classification="Master Informatik",
        expected_sources=[
            "cit.tum.de/cit/anerkennung-informatik"
        ],
        label = "TRANSFER1"
    ),
    QAData(
        question="When/How should I start with the process of transferring credit hours from my previous program to better plan my studies?",
        answer="As soon as possible. You must apply for recognition within the first year of your studies and please be aware that it might take up to 6 months until your application has been processed. All relevant information can be found here: https://www.cit.tum.de/en/cit/recognition-informatics/",
        key_facts=[
            "You must apply for recognition within the first year of your studies.",
            "The application process can take up to 6 months."
        ],
        classification="general",
        expected_sources=[
            "https://www.cit.tum.de/en/cit/recognition-informatics/"
        ],
        label = "TRANSFER2"
    ),
    QAData(
        question="I am not able to register for the seminar yet through the matching platform, should I wait till next semester starts? Also can I take a practical lab course from another program other than informatics in case what I wanted is not offered?",
        answer="Seminars are a bit different than other modules. Please refer to the info site (https://www.cit.tum.de/en/cit/studies/students/examination-matters-modules/informatics/practical-courses-seminar-courses/) and follow the links there. If you want the practical course to count towards your program it must be a practical course that is part of your curriculum and most practical courses from other schools do not meet that requirement.",
        key_facts=[
            "Seminars have different rules than other modules.",
            "Practical courses must be part of your curriculum to count towards your program."
        ],
        classification="Bachelor Informatik",
        expected_sources=[
            "https://www.cit.tum.de/en/cit/studies/students/examination-matters-modules/informatics/practical-courses-seminar-courses/"
        ],
        label = "COURSE4"
    ),
    QAData(
        question="I'm a informatics master student in 4 semester. I have 52 credits passed, and I think I can get at least 15 credits in this semester. My original plan was to do the IDP in my 5th semester, and master thesis in 6th semester. I'm considering the possibility of working back to China, and the best way to evaluate this option is to do an internship back to China. When taking this into account, since my original plan did not permit an internship in China, I think it would be easier to arrange my time if I could leave for absence for one semester, either in next semester or between my 5th and 6th semester. It would be helpful if you have any suggestions :)",
        answer="Check our website for information on the criteria an internship has to meet in order to qualify for a leave of absence cit.tum.de/en/cit/tips-informatics -->Internships. I am sure you are aware that you need to have 60 ECTS by the end of your 4th semester. If you only pass 15 credits, you will have 67, which is close to the bare minimum, and it might make more sense to focus on your studies and make sure you obtain your Master's degree. Once you have worked through the information on the website mentioned above, make sure you join one of the academic advisors' consultation hours.",
        key_facts=[
            "You need 60 ECTS by the end of your 4th semester.",
            "It might make more sense to focus on your studies instead of taking a leave of absence.",
            "Consult the academic advisors for further assistance."
        ],
        classification="Master Informatik",
        expected_sources=[
            "cit.tum.de/en/cit/tips-informatics"
        ],
        label = "LEAVE2"
    )
]