import logging
import os
from email import policy
from email.parser import BytesParser

import pandas as pd
from dotenv import load_dotenv

from app.common.logging_config import setup_logging
from app.email_responder.email_responder import EmailResponder

# Configuration
load_dotenv("./../development.env")
eml_folder_path = os.getenv("TEST_EML_PATH")


def process_eml_files():
    email_responder = EmailResponder()
    non_sensitive = []
    sensitive = []
    for i, filename in enumerate(os.listdir(eml_folder_path), start=1):
        if filename.endswith('.eml'):
            eml_file_path = os.path.join(eml_folder_path, filename)
            with open(eml_file_path, 'rb') as f:
                eml_data = f.read()

            # Parse the .eml file
            email_message = BytesParser(policy=policy.default).parsebytes(eml_data)
            raw_emails = [email_message.as_bytes()]
            emails = email_responder.email_processor.process_raw_emails(raw_emails)
            for email in emails:
                classification, language, study_program = email_responder.email_classifier.classify(email)
                # classification1, confidence1 = email_responder.study_program_classifier.classify(email)
                if classification.strip().lower() == "non-sensitive":
                    non_sensitive.append(email.subject)
                else:
                    sensitive.append(email.subject)

    logging.info(f"sensitive: {len(sensitive)} non-sensitive: {len(non_sensitive)}")
    df_non_sensitive = pd.DataFrame({
        'Array': ['non_sensitive'] * len(non_sensitive),
        'Element': non_sensitive
    })

    df_sensitive = pd.DataFrame({
        'Array': ['sensitive'] * len(sensitive),
        'Element': sensitive
    })

    # Concatenate the DataFrames to create the final table
    df_combined = pd.concat([df_non_sensitive, df_sensitive], ignore_index=True)

    # Display the combined DataFrame
    print(df_combined)


if __name__ == "__main__":
    setup_logging()
    logging.info("Application started")
    process_eml_files()
