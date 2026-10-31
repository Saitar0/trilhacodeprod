"""Isolated curriculum domain contracts.

This package is not imported by the active application flows.
"""

from .editorial_revision_protocol import (
    EditorialRevisionProtocol,
    FenceAuthorityCredential,
    FencingRejected,
    IdempotencyConflict,
    InMemoryEditorialRevisionProtocol,
    InvalidProposal,
    OperationAborted,
    OperationState,
    PreparedRevision,
    ProposalValidationError,
    RevisionConflict,
    RevisionProtocolError,
    RevisionRecord,
    RevisionReceipt,
    WriterAuthorizationError,
    WriterCredential,
)

__all__ = [
    "EditorialRevisionProtocol",
    "FenceAuthorityCredential",
    "FencingRejected",
    "IdempotencyConflict",
    "InMemoryEditorialRevisionProtocol",
    "InvalidProposal",
    "OperationAborted",
    "OperationState",
    "PreparedRevision",
    "ProposalValidationError",
    "RevisionConflict",
    "RevisionProtocolError",
    "RevisionRecord",
    "RevisionReceipt",
    "WriterAuthorizationError",
    "WriterCredential",
]
