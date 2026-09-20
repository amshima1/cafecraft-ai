"""Unit tests for the Documents foundation."""

import unittest

from core.exceptions import DocumentGenerationError, ValidationError
from documents import (
    DeterministicDocumentGenerator,
    DocumentGenerator,
    DocumentRequest,
    DocumentService,
    GeneratedDocument,
)


class RecordingGenerator:
    """Injected generator used to verify service delegation."""

    def __init__(self, result: GeneratedDocument | None = None) -> None:
        self.requests: list[DocumentRequest] = []
        self.result = result

    def generate(self, request: DocumentRequest) -> GeneratedDocument:
        self.requests.append(request)
        return self.result or GeneratedDocument(request.document_type, request.content)


class FailingGenerator:
    """Injected generator that raises a chosen exception."""

    def __init__(self, error: Exception) -> None:
        self.error = error

    def generate(self, request: DocumentRequest) -> GeneratedDocument:
        raise self.error


class DocumentsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.request = DocumentRequest("resume", "Ada built reliable systems.")
        self.generator = DeterministicDocumentGenerator()

    def test_valid_document_request(self) -> None:
        self.assertEqual(self.request.document_type, "resume")
        self.assertEqual(self.request.content, "Ada built reliable systems.")

    def test_valid_generated_document(self) -> None:
        document = GeneratedDocument("cover_letter", "Dear hiring team.")
        self.assertEqual(document.document_type, "cover_letter")
        self.assertEqual(document.content, "Dear hiring team.")

    def test_empty_document_type_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentRequest("", "content")

    def test_whitespace_document_type_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentRequest("   ", "content")

    def test_empty_content_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentRequest("resume", "")

    def test_whitespace_content_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentRequest("resume", "   ")

    def test_non_string_required_fields_are_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentRequest(123, "content")  # type: ignore[arg-type]
        with self.assertRaises(ValidationError):
            DocumentRequest("resume", 123)  # type: ignore[arg-type]
        with self.assertRaises(ValidationError):
            GeneratedDocument(123, "content")  # type: ignore[arg-type]
        with self.assertRaises(ValidationError):
            GeneratedDocument("resume", 123)  # type: ignore[arg-type]

    def test_models_are_immutable(self) -> None:
        with self.assertRaises((AttributeError, TypeError)):
            self.request.content = "changed"  # type: ignore[misc]
        document = GeneratedDocument("resume", "content")
        with self.assertRaises((AttributeError, TypeError)):
            document.content = "changed"  # type: ignore[misc]

    def test_generator_accepts_valid_request(self) -> None:
        self.assertIsInstance(self.generator.generate(self.request), GeneratedDocument)

    def test_generator_preserves_exact_document_type_and_content(self) -> None:
        request = DocumentRequest(" cover letter ", " Supplied content ")
        result = self.generator.generate(request)
        self.assertEqual(result.document_type, request.document_type)
        self.assertEqual(result.content, request.content)

    def test_generator_is_deterministic(self) -> None:
        self.assertEqual(self.generator.generate(self.request), self.generator.generate(self.request))

    def test_generator_adds_no_metadata(self) -> None:
        result = self.generator.generate(self.request)
        self.assertEqual(result, GeneratedDocument(self.request.document_type, self.request.content))
        self.assertEqual(set(result.__dataclass_fields__), {"document_type", "content"})

    def test_generator_does_not_mutate_request(self) -> None:
        before = self.request
        self.generator.generate(self.request)
        self.assertEqual(self.request, before)

    def test_generator_rejects_invalid_request_type(self) -> None:
        with self.assertRaises(ValidationError):
            self.generator.generate({"document_type": "resume", "content": "content"})  # type: ignore[arg-type]

    def test_generator_has_no_external_service_dependency(self) -> None:
        result = self.generator.generate(self.request)
        self.assertEqual(result.content, self.request.content)

    def test_default_service_generator(self) -> None:
        result = DocumentService().generate("resume", "content")
        self.assertEqual(result, GeneratedDocument("resume", "content"))

    def test_service_returns_generated_result(self) -> None:
        result = DocumentService().generate("resume", "content")
        self.assertIsInstance(result, GeneratedDocument)

    def test_service_rejects_invalid_document_type(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentService().generate("", "content")

    def test_service_rejects_whitespace_document_type(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentService().generate(" ", "content")

    def test_service_rejects_invalid_content(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentService().generate("resume", "")

    def test_service_rejects_whitespace_content(self) -> None:
        with self.assertRaises(ValidationError):
            DocumentService().generate("resume", " ")

    def test_service_delegates_to_injected_generator(self) -> None:
        generator = RecordingGenerator()
        service = DocumentService(generator)
        service.generate("resume", "content")
        self.assertEqual(len(generator.requests), 1)

    def test_service_passes_document_request_to_generator(self) -> None:
        generator = RecordingGenerator()
        DocumentService(generator).generate("resume", "content")
        self.assertIsInstance(generator.requests[0], DocumentRequest)
        self.assertEqual(generator.requests[0], DocumentRequest("resume", "content"))

    def test_service_returns_injected_result_unchanged(self) -> None:
        expected = GeneratedDocument("resume", "generated")
        service = DocumentService(RecordingGenerator(expected))
        self.assertIs(service.generate("resume", "source"), expected)

    def test_service_propagates_document_generation_error(self) -> None:
        error = DocumentGenerationError("generation failed")
        with self.assertRaisesRegex(DocumentGenerationError, "generation failed"):
            DocumentService(FailingGenerator(error)).generate("resume", "content")

    def test_service_propagates_unexpected_exception(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "unexpected"):
            DocumentService(FailingGenerator(RuntimeError("unexpected"))).generate("resume", "content")

    def test_public_protocol_can_type_injected_generator(self) -> None:
        generator: DocumentGenerator = RecordingGenerator()
        result = DocumentService(generator).generate("resume", "content")
        self.assertEqual(result.content, "content")

    def test_documents_have_no_mutable_global_state(self) -> None:
        first = DocumentService().generate("resume", "first")
        second = DocumentService().generate("resume", "second")
        self.assertNotEqual(first.content, second.content)
        self.assertEqual(first.content, "first")


if __name__ == "__main__":
    unittest.main()
