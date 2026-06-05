from kitefs import (
    EntityKey,
    EventTimestamp,
    Expect,
    Feature,
    FeatureGroup,
    FeatureType,
    JoinKey,
    Metadata,
    StorageTarget,
    ValidationMode,
)


listing_features = FeatureGroup(
    name="listing_features",
    storage_target=StorageTarget.OFFLINE,
    entity_key=EntityKey(name="listing_id", dtype=FeatureType.INTEGER),
    event_timestamp=EventTimestamp(name="sold_at"),
    features=[
        Feature(
            name="net_area", dtype=FeatureType.INTEGER, expect=Expect().not_null().gt(0)
        ),
        Feature(
            name="number_of_rooms",
            dtype=FeatureType.INTEGER,
            expect=Expect().not_null().gt(0),
        ),
        Feature(
            name="build_year",
            dtype=FeatureType.INTEGER,
            expect=Expect().not_null().gte(1900).lte(2030),
        ),
        Feature(
            name="sold_price", dtype=FeatureType.FLOAT, expect=Expect().not_null().gt(0)
        ),
    ],
    join_keys=[
        JoinKey(
            name="town_id",
            dtype=FeatureType.INTEGER,
            referenced_group="town_market_features",
        )
    ],
    ingestion_validation=ValidationMode.ERROR,
    offline_retrieval_validation=ValidationMode.NONE,
    metadata=Metadata(
        description="Historical sold listing attributes and prices",
        owner="data-science-team",
        tags={"domain": "real-estate", "cadence": "monthly"},
    ),
)
