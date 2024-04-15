from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServeClientArgs(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: str
    def __init__(self, request: _Optional[str] = ...) -> None: ...

class ServeClientReply(_message.Message):
    __slots__ = ("data", "leaderId", "success")
    DATA_FIELD_NUMBER: _ClassVar[int]
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    data: str
    leaderId: int
    success: bool
    def __init__(self, data: _Optional[str] = ..., leaderId: _Optional[int] = ..., success: bool = ...) -> None: ...

class VoteRequestReply(_message.Message):
    __slots__ = ("nodeId", "term", "success", "leaseDurationRemaining")
    NODEID_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    LEASEDURATIONREMAINING_FIELD_NUMBER: _ClassVar[int]
    nodeId: int
    term: int
    success: bool
    leaseDurationRemaining: float
    def __init__(self, nodeId: _Optional[int] = ..., term: _Optional[int] = ..., success: bool = ..., leaseDurationRemaining: _Optional[float] = ...) -> None: ...

class GetVoteRequest(_message.Message):
    __slots__ = ("term", "nodeId", "lastLogIndex", "lastLogTerm")
    TERM_FIELD_NUMBER: _ClassVar[int]
    NODEID_FIELD_NUMBER: _ClassVar[int]
    LASTLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    LASTLOGTERM_FIELD_NUMBER: _ClassVar[int]
    term: int
    nodeId: int
    lastLogIndex: int
    lastLogTerm: int
    def __init__(self, term: _Optional[int] = ..., nodeId: _Optional[int] = ..., lastLogIndex: _Optional[int] = ..., lastLogTerm: _Optional[int] = ...) -> None: ...

class AppendEntryReply(_message.Message):
    __slots__ = ("success", "term", "ack", "nodeId")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    ACK_FIELD_NUMBER: _ClassVar[int]
    NODEID_FIELD_NUMBER: _ClassVar[int]
    success: bool
    term: int
    ack: int
    nodeId: int
    def __init__(self, success: bool = ..., term: _Optional[int] = ..., ack: _Optional[int] = ..., nodeId: _Optional[int] = ...) -> None: ...

class LogRequestReply(_message.Message):
    __slots__ = ("nodeId", "currentTerm", "ack", "success")
    NODEID_FIELD_NUMBER: _ClassVar[int]
    CURRENTTERM_FIELD_NUMBER: _ClassVar[int]
    ACK_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    nodeId: int
    currentTerm: int
    ack: int
    success: bool
    def __init__(self, nodeId: _Optional[int] = ..., currentTerm: _Optional[int] = ..., ack: _Optional[int] = ..., success: bool = ...) -> None: ...

class Command(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ("term", "command")
    TERM_FIELD_NUMBER: _ClassVar[int]
    COMMAND_FIELD_NUMBER: _ClassVar[int]
    term: int
    command: Command
    def __init__(self, term: _Optional[int] = ..., command: _Optional[_Union[Command, _Mapping]] = ...) -> None: ...

class AppendEntriesRequest(_message.Message):
    __slots__ = ("term", "leaderId", "prevLogIndex", "prevLogTerm", "entries", "leaderCommitIndex", "leaseDuration")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LEADERID_FIELD_NUMBER: _ClassVar[int]
    PREVLOGINDEX_FIELD_NUMBER: _ClassVar[int]
    PREVLOGTERM_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    LEADERCOMMITINDEX_FIELD_NUMBER: _ClassVar[int]
    LEASEDURATION_FIELD_NUMBER: _ClassVar[int]
    term: int
    leaderId: int
    prevLogIndex: int
    prevLogTerm: int
    entries: _containers.RepeatedCompositeFieldContainer[LogEntry]
    leaderCommitIndex: int
    leaseDuration: int
    def __init__(self, term: _Optional[int] = ..., leaderId: _Optional[int] = ..., prevLogIndex: _Optional[int] = ..., prevLogTerm: _Optional[int] = ..., entries: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ..., leaderCommitIndex: _Optional[int] = ..., leaseDuration: _Optional[int] = ...) -> None: ...
