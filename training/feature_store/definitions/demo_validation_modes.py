from kitefs import EntityKey, EventTimestamp, Expect, Feature, FeatureGroup
from kitefs import FeatureType, Metadata, StorageTarget, ValidationMode


demo_filter_features = FeatureGroup(
    name="demo_filter_features",
    storage_target=StorageTarget.OFFLINE,
    entity_key=EntityKey(name="demo_id", dtype=FeatureType.INTEGER),
    event_timestamp=EventTimestamp(name="event_timestamp"),
    features=[
        Feature(name="score", dtype=FeatureType.FLOAT, expect=Expect().not_null().gt(0))
    ],
    ingestion_validation=ValidationMode.FILTER,
    offline_retrieval_validation=ValidationMode.NONE,
    metadata=Metadata(
        description="Demo-only group for FILTER validation mode",
        owner="data-science-team",
        tags={"purpose": "validation-demo"},
    ),
)


demo_none_features = FeatureGroup(
    name="demo_none_features",
    storage_target=StorageTarget.OFFLINE,
    entity_key=EntityKey(name="demo_id", dtype=FeatureType.INTEGER),
    event_timestamp=EventTimestamp(name="event_timestamp"),
    features=[
        Feature(name="score", dtype=FeatureType.FLOAT, expect=Expect().not_null().gt(0))
    ],
    ingestion_validation=ValidationMode.NONE,
    offline_retrieval_validation=ValidationMode.NONE,
    metadata=Metadata(
        description="Demo-only group for NONE validation mode",
        owner="data-science-team",
        tags={"purpose": "validation-demo"},
    ),
)