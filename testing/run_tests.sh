#!/bin/bash

# Load environment variables from ./testing/testing.env
export $(grep -v '^#' ./testing/testing.env | xargs)

# Check if USE_AZURE is set to "true"
if [ "$USE_AZURE" = "true" ]; then
    echo "Configuring DeepEval to use Azure OpenAI..."

    # Step 1: Configure DeepEval to use Azure OpenAI
    deepeval set-azure-openai \
        --openai-endpoint="${AZURE_OPENAI_ENDPOINT}" \
        --openai-api-key="${AZURE_OPENAI_API_KEY}" \
        --deployment-name="${AZURE_OPENAI_DEPLOYMENT}" \
        --openai-api-version="${AZURE_OPENAI_VERSION}"
else
    echo "USE_AZURE is not set to 'true'. Skipping Azure OpenAI configuration."
fi

# Step 2: Run the tests in tests/test_rag.py with pytest
pytest ./testing/tests/test_rag.py --disable-warnings

# Uncomment the following to run tests with logging
#pytest -o log_cli=true --log-cli-level=INFO ./testing/tests/test_rag.py