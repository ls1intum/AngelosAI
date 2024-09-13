class BaseModelClient:
    def complete(self, messages: []) -> (str, float):
        raise NotImplementedError("This method should be implemented by subclasses.")

    def embed(self, text: str) -> (str, float):
        raise NotImplementedError("This method should be implemented by subclasses.")
