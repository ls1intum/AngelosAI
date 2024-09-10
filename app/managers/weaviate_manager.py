import weaviate

class WeaviateManager:
    def __init__(self, url: str, model):
        self.client = weaviate.Client(url)
        self.model = model
        self.schema_initialized = False
        self._initialize_schema()

    def class_exists(self, class_name):
        schema = self.client.schema.get()
        existing_classes = [class_["class"] for class_ in schema["classes"]]
        return class_name in existing_classes

    def _initialize_schema(self):
        """Creates the schema in Weaviate for storing documents and embeddings."""
        if self.class_exists("Document"):
            print("Class 'Document' already exists, no need to create it.")
        else:
            schema = {
                "classes": [
                    {
                        "class": "Document",
                        "properties": [
                            {"name": "content", "dataType": ["text"]},
                            {"name": "embedding", "dataType": ["number[]"]},  # Vector embeddings
                            {"name": "classification", "dataType": ["text"]}
                        ]
                    }
                ]
            }
            self.client.schema.create(schema)
            self.schema_initialized = True

    def add_document(self, text: str, classification: str):
        """Add a document with embedding and classification to Weaviate."""
        embedding = self.model.embed(text)
        self.client.data_object.create({
            "content": text,
            "embedding": embedding,
            "classification": classification
        }, class_name="Document")

    def get_relevant_context(self, question: str, classification: str):
        """Retrieve documents based on the question embedding and classification."""
        question_embedding = self.model.embed(question)
        query_result = self.client.query.get("Document", ["content"]).with_near_vector({
            "vector": question_embedding
        }).with_where({
            "path": ["classification"],
            "operator": "Like",
            "valueString": classification
        }).with_limit(5).do()

        results = query_result.get("data", {}).get("Get", {}).get("Document", [])
        context = "\n\n".join(result["content"] for result in results)
        return context
