def generate_classification_prompt(subject, body, study_programs):
    classification_prompt = [
        {
            "role": "system",
            "content": (
                "You are a classifier for the study counseling service at the Technical University of Munich (TUM). "
                "Your task is to classify emails into three categories: \n"
                "1. 'Sensitive' or 'non-sensitive' based on the content.\n"
                "2. The language of the email. Either 'german' or 'english'. If it is a different language, default to 'english'.\n"
                "3. Whether the email mentions any of the following study programs: "
                f"{study_programs}.\nIdentify the study program from the given information. If the specific program of the student is mentioned, provide its name; if none is specified, respond with ‘general’. In cases where the email concerns switching study programs or transferring from a Bachelor’s to a Master’s program, provide the name of the program the student intends to switch to."
                "Output strictly as a JSON object in the following format, without any additional text.:\n"
                "{\n"
                '  "classification": "<sensitive or non-sensitive>",\n'
                '  "language": "<german or english>",\n'
                '  "study_program": "<specific program name or general>"\n'
                "}"
            )
        },
        {
            "role": "user",
            "content": (
                "Classify the email using the following guidelines:\n\n"
                "1. **Non-sensitive topics**: These are routine, straightforward, or administrative questions as well "
                "as the following topics:"
                "- Exam registration or missed exam registration\n"
                "- Finding a thesis topic\n"
                "- General administrative questions\n"
                "- Thesis submission\n"
                "- Recognition of credits from previous studies\n"
                "- Assignment of grades as free subjects (Freifach)\n"
                "- Approval of final certificate\n"
                "- Graduation ceremony inquiries and missing invitations\n"
                "- Questions about \"Überfachliche Grundlagen\" (support electives)\n"
                "If the email contains one of these topics, or it is clear and easily resolved without direct counselor involvement, classify it as 'non-sensitive'.\n\n"
                "2. **Sensitive topics**: These involve complex problems concerning the course of studies and topics such as:\n"
                "- Exmatriculation (deregistration)\n"
                "- Physical or psychological health concerns\n"
                "- Termination or switching a thesis, seminar, or practical course\n"
                "- Missing credit requirements or hurdles\n"
                "- Study interruptions or delays\n"
                "- Requests for very specific or critical academic guidance\n"
                "If the email involves one of these topics or you are uncertain, classify it as 'sensitive'."
                "Return the classification, the language and the study_program."
            )
        },
        {
            "role": "user",
            "content": f"Email Subject: {subject}\n\nEmail Body:\n{body}"
        }
    ]
    return classification_prompt
