def validate_modelkit_tag(modelkit_tag: str) -> bool:
    """Validate that ModelKit tag has correct format"""
    # Check if modelkit_tag is valid
    if not modelkit_tag or not isinstance(modelkit_tag, str):
        raise ValueError("ModelKit tag must be a non-empty string")

    # Validate ModelKit tag format: registry/namespace/repository:tag
    if modelkit_tag.count("/") < 2 or ":" not in modelkit_tag:
        raise ValueError(
            "ModelKit tag must have format: registry/namespace/repository:tag"
        )

    # Split the tag to check individual components
    path, tag_part = modelkit_tag.rsplit(":", 1)
    path_parts = path.split("/")

    # Ensure all parts are non-empty
    if "" in path_parts or not tag_part:
        raise ValueError(
            "All components of ModelKit tag (registry, namespace, repository, tag) must be non-empty"
        )

    return True
