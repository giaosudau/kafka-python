import inspect
import sys
from collections import namedtuple

###############
#   Structs   #
###############

# https://cwiki.apache.org/confluence/display/KAFKA/A+Guide+To+The+Kafka+Protocol#AGuideToTheKafkaProtocol-MetadataAPI
MetadataRequest = namedtuple("MetadataRequest",
    ["topics"])

MetadataResponse = namedtuple("MetadataResponse",
    ["brokers", "topics"])

# https://cwiki.apache.org/confluence/display/KAFKA/A+Guide+To+The+Kafka+Protocol#AGuideToTheKafkaProtocol-ConsumerMetadataRequest
ConsumerMetadataRequest = namedtuple("ConsumerMetadataRequest",
    ["groups"])

ConsumerMetadataResponse = namedtuple("ConsumerMetadataResponse",
    ["error", "nodeId", "host", "port"])

# https://cwiki.apache.org/confluence/display/KAFKA/A+Guide+To+The+Kafka+Protocol#AGuideToTheKafkaProtocol-ProduceAPI
ProduceRequestPayload = namedtuple("ProduceRequestPayload",
    ["topic", "partition", "messages"])

ProduceResponsePayload = namedtuple("ProduceResponsePayload",
    ["topic", "partition", "error", "offset"])

# https://cwiki.apache.org/confluence/display/KAFKA/A+Guide+To+The+Kafka+Protocol#AGuideToTheKafkaProtocol-FetchAPI
FetchRequestPayload = namedtuple("FetchRequestPayload",
    ["topic", "partition", "offset", "max_bytes"])

FetchResponsePayload = namedtuple("FetchResponsePayload",
    ["topic", "partition", "error", "highwaterMark", "messages"])

# https://cwiki.apache.org/confluence/display/KAFKA/A+Guide+To+The+Kafka+Protocol#AGuideToTheKafkaProtocol-OffsetAPI
OffsetRequestPayload = namedtuple("OffsetRequestPayload",
    ["topic", "partition", "time", "max_offsets"])

OffsetResponsePayload = namedtuple("OffsetResponsePayload",
    ["topic", "partition", "error", "offsets"])

# https://cwiki.apache.org/confluence/display/KAFKA/A+Guide+To+The+Kafka+Protocol#AGuideToTheKafkaProtocol-OffsetCommit/FetchAPI
OffsetCommitRequestPayload = namedtuple("OffsetCommitRequestPayload",
    ["topic", "partition", "offset", "metadata"])

OffsetCommitResponsePayload = namedtuple("OffsetCommitResponsePayload",
    ["topic", "partition", "error"])

OffsetFetchRequestPayload = namedtuple("OffsetFetchRequestPayload",
    ["topic", "partition"])

OffsetFetchResponsePayload = namedtuple("OffsetFetchResponsePayload",
    ["topic", "partition", "offset", "metadata", "error"])



# Other useful structs
BrokerMetadata = namedtuple("BrokerMetadata",
    ["nodeId", "host", "port"])

TopicMetadata = namedtuple("TopicMetadata",
    ["topic", "error", "partitions"])

PartitionMetadata = namedtuple("PartitionMetadata",
    ["topic", "partition", "leader", "replicas", "isr", "error"])

OffsetAndMessage = namedtuple("OffsetAndMessage",
    ["offset", "message"])

Message = namedtuple("Message",
    ["magic", "attributes", "key", "value"])

TopicPartition = namedtuple("TopicPartition",
    ["topic", "partition"])

KafkaMessage = namedtuple("KafkaMessage",
    ["topic", "partition", "offset", "key", "value"])

OffsetAndMetadata = namedtuple("OffsetAndMetadata",
    ["offset", "metadata"])

# Define retry policy for async producer
# Limit value: int >= 0, 0 means no retries
RetryOptions = namedtuple("RetryOptions",
    ["limit", "backoff_ms", "retry_on_timeouts"])


#################
#   Exceptions  #
#################


class KafkaError(RuntimeError):
    retriable = False
    # whether metadata should be refreshed on error
    invalid_metadata = False


class IllegalStateError(KafkaError):
    pass


class IllegalArgumentError(KafkaError):
    pass


class NoBrokersAvailable(KafkaError):
    retriable = True
    invalid_metadata = True


class NodeNotReadyError(KafkaError):
    retriable = True


class CorrelationIdError(KafkaError):
    retriable = True


class Cancelled(KafkaError):
    retriable = True


class TooManyInFlightRequests(KafkaError):
    retriable = True


class StaleMetadata(KafkaError):
    retriable = True
    invalid_metadata = True


class BrokerResponseError(KafkaError):
    errno = None
    message = None
    description = None

    def __str__(self):
        return '%s - %s - %s' % (self.__class__.__name__, self.errno, self.description)


class NoError(BrokerResponseError):
    errno = 0
    message = 'NO_ERROR'
    description = 'No error--it worked!'


class UnknownError(BrokerResponseError):
    errno = -1
    message = 'UNKNOWN'
    description = 'An unexpected server error.'


class OffsetOutOfRangeError(BrokerResponseError):
    errno = 1
    message = 'OFFSET_OUT_OF_RANGE'
    description = ('The requested offset is outside the range of offsets'
                   ' maintained by the server for the given topic/partition.')


class InvalidMessageError(BrokerResponseError):
    errno = 2
    message = 'INVALID_MESSAGE'
    description = ('This indicates that a message contents does not match its'
                   ' CRC.')


class UnknownTopicOrPartitionError(BrokerResponseError):
    errno = 3
    message = 'UNKNOWN_TOPIC_OR_PARTITON'
    description = ('This request is for a topic or partition that does not'
                   ' exist on this broker.')
    invalid_metadata = True


class InvalidFetchRequestError(BrokerResponseError):
    errno = 4
    message = 'INVALID_FETCH_SIZE'
    description = 'The message has a negative size.'


class LeaderNotAvailableError(BrokerResponseError):
    errno = 5
    message = 'LEADER_NOT_AVAILABLE'
    description = ('This error is thrown if we are in the middle of a'
                   ' leadership election and there is currently no leader for'
                   ' this partition and hence it is unavailable for writes.')
    retriable = True
    invalid_metadata = True


class NotLeaderForPartitionError(BrokerResponseError):
    errno = 6
    message = 'NOT_LEADER_FOR_PARTITION'
    description = ('This error is thrown if the client attempts to send'
                   ' messages to a replica that is not the leader for some'
                   ' partition. It indicates that the clients metadata is out'
                   ' of date.')
    retriable = True
    invalid_metadata = True


class RequestTimedOutError(BrokerResponseError):
    errno = 7
    message = 'REQUEST_TIMED_OUT'
    description = ('This error is thrown if the request exceeds the'
                   ' user-specified time limit in the request.')
    retriable = True


class BrokerNotAvailableError(BrokerResponseError):
    errno = 8
    message = 'BROKER_NOT_AVAILABLE'
    description = ('This is not a client facing error and is used mostly by'
                   ' tools when a broker is not alive.')

class ReplicaNotAvailableError(BrokerResponseError):
    errno = 9
    message = 'REPLICA_NOT_AVAILABLE'
    description = ('If replica is expected on a broker, but is not (this can be'
                   ' safely ignored).')


class MessageSizeTooLargeError(BrokerResponseError):
    errno = 10
    message = 'MESSAGE_SIZE_TOO_LARGE'
    description = ('The server has a configurable maximum message size to avoid'
                   ' unbounded memory allocation. This error is thrown if the'
                   ' client attempt to produce a message larger than this'
                   ' maximum.')


class StaleControllerEpochError(BrokerResponseError):
    errno = 11
    message = 'STALE_CONTROLLER_EPOCH'
    description = 'Internal error code for broker-to-broker communication.'


class OffsetMetadataTooLargeError(BrokerResponseError):
    errno = 12
    message = 'OFFSET_METADATA_TOO_LARGE'
    description = ('If you specify a string larger than configured maximum for'
                   ' offset metadata.')


# TODO is this deprecated? https://cwiki.apache.org/confluence/display/KAFKA/A+Guide+To+The+Kafka+Protocol#AGuideToTheKafkaProtocol-ErrorCodes
class StaleLeaderEpochCodeError(BrokerResponseError):
    errno = 13
    message = 'STALE_LEADER_EPOCH_CODE'


class GroupLoadInProgressError(BrokerResponseError):
    errno = 14
    message = 'OFFSETS_LOAD_IN_PROGRESS'
    description = ('The broker returns this error code for an offset fetch'
                   ' request if it is still loading offsets (after a leader'
                   ' change for that offsets topic partition), or in response'
                   ' to group membership requests (such as heartbeats) when'
                   ' group metadata is being loaded by the coordinator.')
    retriable = True


class GroupCoordinatorNotAvailableError(BrokerResponseError):
    errno = 15
    message = 'CONSUMER_COORDINATOR_NOT_AVAILABLE'
    description = ('The broker returns this error code for group coordinator'
                   ' requests, offset commits, and most group management'
                   ' requests if the offsets topic has not yet been created, or'
                   ' if the group coordinator is not active.')
    retriable = True


class NotCoordinatorForGroupError(BrokerResponseError):
    errno = 16
    message = 'NOT_COORDINATOR_FOR_CONSUMER'
    description = ('The broker returns this error code if it receives an offset'
                   ' fetch or commit request for a group that it is not a'
                   ' coordinator for.')
    retriable = True


class InvalidTopicError(BrokerResponseError):
    errno = 17
    message = 'INVALID_TOPIC'
    description = ('For a request which attempts to access an invalid topic'
                   ' (e.g. one which has an illegal name), or if an attempt'
                   ' is made to write to an internal topic (such as the'
                   ' consumer offsets topic).')


class RecordListTooLargeError(BrokerResponseError):
    errno = 18
    message = 'RECORD_LIST_TOO_LARGE'
    description = ('If a message batch in a produce request exceeds the maximum'
                   ' configured segment size.')


class NotEnoughReplicasError(BrokerResponseError):
    errno = 19
    message = 'NOT_ENOUGH_REPLICAS'
    description = ('Returned from a produce request when the number of in-sync'
                   ' replicas is lower than the configured minimum and'
                   ' requiredAcks is -1.')


class NotEnoughReplicasAfterAppendError(BrokerResponseError):
    errno = 20
    message = 'NOT_ENOUGH_REPLICAS_AFTER_APPEND'
    description = ('Returned from a produce request when the message was'
                   ' written to the log, but with fewer in-sync replicas than'
                   ' required.')


class InvalidRequiredAcksError(BrokerResponseError):
    errno = 21
    message = 'INVALID_REQUIRED_ACKS'
    description = ('Returned from a produce request if the requested'
                   ' requiredAcks is invalid (anything other than -1, 1, or 0).')


class IllegalGenerationError(BrokerResponseError):
    errno = 22
    message = 'ILLEGAL_GENERATION'
    description = ('Returned from group membership requests (such as heartbeats)'
                   ' when the generation id provided in the request is not the'
                   ' current generation.')


class InconsistentGroupProtocolError(BrokerResponseError):
    errno = 23
    message = 'INCONSISTENT_GROUP_PROTOCOL'
    description = ('Returned in join group when the member provides a protocol'
                   ' type or set of protocols which is not compatible with the current group.')


class InvalidGroupIdError(BrokerResponseError):
    errno = 24
    message = 'INVALID_GROUP_ID'
    description = 'Returned in join group when the groupId is empty or null.'


class UnknownMemberIdError(BrokerResponseError):
    errno = 25
    message = 'UNKNOWN_MEMBER_ID'
    description = ('Returned from group requests (offset commits/fetches,'
                   ' heartbeats, etc) when the memberId is not in the current'
                   ' generation.')


class InvalidSessionTimeoutError(BrokerResponseError):
    errno = 26
    message = 'INVALID_SESSION_TIMEOUT'
    description = ('Return in join group when the requested session timeout is'
                   ' outside of the allowed range on the broker')


class RebalanceInProgressError(BrokerResponseError):
    errno = 27
    message = 'REBALANCE_IN_PROGRESS'
    description = ('Returned in heartbeat requests when the coordinator has'
                   ' begun rebalancing the group. This indicates to the client'
                   ' that it should rejoin the group.')


class InvalidCommitOffsetSizeError(BrokerResponseError):
    errno = 28
    message = 'INVALID_COMMIT_OFFSET_SIZE'
    description = ('This error indicates that an offset commit was rejected'
                   ' because of oversize metadata.')


class TopicAuthorizationFailedError(BrokerResponseError):
    errno = 29
    message = 'TOPIC_AUTHORIZATION_FAILED'
    description = ('Returned by the broker when the client is not authorized to'
                   ' access the requested topic.')


class GroupAuthorizationFailedError(BrokerResponseError):
    errno = 30
    message = 'GROUP_AUTHORIZATION_FAILED'
    description = ('Returned by the broker when the client is not authorized to'
                   ' access a particular groupId.')


class ClusterAuthorizationFailedError(BrokerResponseError):
    errno = 31
    message = 'CLUSTER_AUTHORIZATION_FAILED'
    description = ('Returned by the broker when the client is not authorized to'
                   ' use an inter-broker or administrative API.')


class KafkaUnavailableError(KafkaError):
    pass


class KafkaTimeoutError(KafkaError):
    pass


class FailedPayloadsError(KafkaError):
    def __init__(self, payload, *args):
        super(FailedPayloadsError, self).__init__(*args)
        self.payload = payload


class ConnectionError(KafkaError):
    retriable = True
    invalid_metadata = True


class BufferUnderflowError(KafkaError):
    pass


class ChecksumError(KafkaError):
    pass


class ConsumerFetchSizeTooSmall(KafkaError):
    pass


class ConsumerNoMoreData(KafkaError):
    pass


class ConsumerTimeout(KafkaError):
    pass


class ProtocolError(KafkaError):
    pass


class UnsupportedCodecError(KafkaError):
    pass


class KafkaConfigurationError(KafkaError):
    pass


class AsyncProducerQueueFull(KafkaError):
    def __init__(self, failed_msgs, *args):
        super(AsyncProducerQueueFull, self).__init__(*args)
        self.failed_msgs = failed_msgs


def _iter_broker_errors():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj) and issubclass(obj, BrokerResponseError) and obj != BrokerResponseError:
            yield obj


kafka_errors = dict([(x.errno, x) for x in _iter_broker_errors()])


def for_code(error_code):
    return kafka_errors.get(error_code, UnknownError)


def check_error(response):
    if isinstance(response, Exception):
        raise response
    if response.error:
        error_class = kafka_errors.get(response.error, UnknownError)
        raise error_class(response)


RETRY_BACKOFF_ERROR_TYPES = (
    KafkaUnavailableError, LeaderNotAvailableError,
    ConnectionError, FailedPayloadsError
)


RETRY_REFRESH_ERROR_TYPES = (
    NotLeaderForPartitionError, UnknownTopicOrPartitionError,
    LeaderNotAvailableError, ConnectionError
)


RETRY_ERROR_TYPES = RETRY_BACKOFF_ERROR_TYPES + RETRY_REFRESH_ERROR_TYPES
