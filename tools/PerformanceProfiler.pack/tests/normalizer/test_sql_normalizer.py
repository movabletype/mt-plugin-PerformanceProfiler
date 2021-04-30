import pytest

from performance_profiler.normalizer.sql_normalizer import SQLNormalizer

normalizer = SQLNormalizer()


@pytest.mark.parametrize(
    "identical_queries",
    [
        [
            # SELECT
            # Generally, results from this queries are not identical, but they are identical results in Data::ObjectDriver.
            """
        SELECT entry_meta_entry_id, entry_meta_type, entry_meta_vchar
        FROM mt_entry_meta
        WHERE (entry_meta_type NOT IN (?)) AND (entry_meta_entry_id = ?)
        ORDER BY entry_meta_entry_id ASC, entry_meta_type ASC
        """,
            """
        SELECT entry_meta_vchar, entry_meta_entry_id, entry_meta_type
        FROM mt_entry_meta
        WHERE (entry_meta_type NOT IN (?)) AND (entry_meta_entry_id = ?)
        ORDER BY entry_meta_entry_id ASC, entry_meta_type ASC
        """,
            """
        SELECT entry_meta_type, entry_meta_vchar, entry_meta_entry_id
        FROM mt_entry_meta
        WHERE (entry_meta_type NOT IN (?)) AND (entry_meta_entry_id = ?)
        ORDER BY entry_meta_entry_id ASC, entry_meta_type ASC
        """,
        ],
        [
            # WHERE
            """
        SELECT entry_meta_entry_id, entry_meta_type, entry_meta_vchar
        FROM mt_entry_meta
        WHERE (entry_meta_type NOT IN (?)) AND (entry_meta_entry_id = ?)
        ORDER BY entry_meta_entry_id ASC, entry_meta_type ASC
        """,
            """
        SELECT entry_meta_entry_id, entry_meta_type, entry_meta_vchar
        FROM mt_entry_meta
        WHERE (entry_meta_entry_id = ?) AND (entry_meta_type NOT IN (?))
        ORDER BY entry_meta_entry_id ASC, entry_meta_type ASC
        """,
        ],
        [
            # complex WHERE
            """
        SELECT entry_id
        FROM mt_entry
        WHERE ((((entry_authored_on < ?)) AND ((entry_status = ?)) AND ((entry_blog_id = ?)) AND ((entry_class = ?))) OR (((entry_authored_on = ?)) AND ((entry_status = ?)) AND ((entry_blog_id = ?)) AND ((entry_id < ?)) AND ((entry_class = ?))))
        ORDER BY entry_authored_on DESC, entry_id DESC
        LIMIT 1
        """,
            """
        SELECT entry_id
        FROM mt_entry
        WHERE ((((entry_authored_on = ?)) AND ((entry_status = ?)) AND ((entry_blog_id = ?)) AND ((entry_id < ?)) AND ((entry_class = ?))) OR (((entry_authored_on < ?)) AND ((entry_status = ?)) AND ((entry_blog_id = ?)) AND ((entry_class = ?))))
        ORDER BY entry_authored_on DESC, entry_id DESC
        LIMIT 1
        """,
            """
        SELECT entry_id
        FROM mt_entry
        WHERE ((((entry_status = ?)) AND ((entry_blog_id = ?)) AND ((entry_class = ?)) AND ((entry_authored_on < ?))) OR (((entry_authored_on = ?)) AND ((entry_status = ?)) AND ((entry_blog_id = ?)) AND ((entry_id < ?)) AND ((entry_class = ?))))
        ORDER BY entry_authored_on DESC, entry_id DESC
        LIMIT 1
        """,
        ],
        [
            # JOIN
            """
        SELECT COUNT(*) AS cnt, objecttag_tag_id
        FROM mt_entry, mt_objecttag
        WHERE (entry_class = ?) AND (entry_status = ?) AND (entry_blog_id IN (?)) AND (objecttag_object_datasource = ?) AND (objecttag_blog_id IN (?)) AND (entry_id = objecttag_object_id)
        GROUP BY objecttag_tag_id
        """,
            """
        SELECT COUNT(*) AS cnt, objecttag_tag_id
        FROM mt_objecttag, mt_entry
        WHERE (entry_class = ?) AND (entry_status = ?) AND (entry_blog_id IN (?)) AND (objecttag_object_datasource = ?) AND (objecttag_blog_id IN (?)) AND (entry_id = objecttag_object_id)
        GROUP BY objecttag_tag_id
        """,
        ],
        [
            # DISTINCT
            """
        SELECT DISTINCT entry_id, entry_authored_on
        FROM mt_entry, mt_objecttag
        WHERE (entry_status = ?) AND (entry_class = ?) AND (entry_blog_id = ?) AND (objecttag_blog_id = ?) AND (objecttag_tag_id IN (?,?)) AND (objecttag_object_datasource = ?) AND (entry_id = objecttag_object_id)
        ORDER BY entry_authored_on DESC, entry_id ASC
        """,
            """
        SELECT DISTINCT entry_authored_on, entry_id
        FROM mt_entry, mt_objecttag
        WHERE (entry_status = ?) AND (entry_class = ?) AND (entry_blog_id = ?) AND (objecttag_blog_id = ?) AND (objecttag_tag_id IN (?,?)) AND (objecttag_object_datasource = ?) AND (entry_id = objecttag_object_id)
        ORDER BY entry_authored_on DESC, entry_id ASC
        """,
        ],
        [
            # find by id
            """
        SELECT asset_id, asset_blog_id, asset_class, asset_created_by, asset_created_on, asset_description, asset_file_ext, asset_file_name, asset_file_path, asset_label, asset_mime_type, asset_modified_by, asset_modified_on, asset_parent, asset_url
        FROM mt_asset
        WHERE (asset_id IN (?))
        ORDER BY asset_id ASC
        """,
            """
        SELECT asset_id, asset_blog_id, asset_class, asset_created_by, asset_created_on, asset_description, asset_file_ext, asset_file_name, asset_file_path, asset_label, asset_mime_type, asset_modified_by, asset_modified_on, asset_parent, asset_url
        FROM mt_asset
        WHERE (asset_id IN (?,?))
        ORDER BY asset_id ASC
        """,
            """
        SELECT asset_id, asset_blog_id, asset_class, asset_created_by, asset_created_on, asset_description, asset_file_ext, asset_file_name, asset_file_path, asset_label, asset_mime_type, asset_modified_by, asset_modified_on, asset_parent, asset_url
        FROM mt_asset
        WHERE (asset_id IN (?,?,?))
        ORDER BY asset_id ASC
        """,
        ],
    ],
)
def test_normalize_identical(identical_queries):
    normalized_queries = map(normalizer.normalize, identical_queries)
    assert len(set(normalized_queries)) == 1


@pytest.mark.parametrize(
    "different_queries",
    [
        [
            # different order
            """
        SELECT entry_meta_entry_id, entry_meta_type, entry_meta_vchar
        FROM mt_entry_meta
        WHERE (entry_meta_type NOT IN (?)) AND (entry_meta_entry_id = ?)
        ORDER BY entry_meta_entry_id ASC, entry_meta_type ASC
        """,
            """
        SELECT entry_meta_entry_id, entry_meta_type, entry_meta_vchar
        FROM mt_entry_meta
        WHERE (entry_meta_type NOT IN (?)) AND (entry_meta_entry_id = ?)
        ORDER BY entry_meta_type ASC, entry_meta_entry_id ASC
        """,
        ],
    ],
)
def test_normalize_different(different_queries):
    normalized_queries = map(normalizer.normalize, different_queries)
    assert len(set(normalized_queries)) > 1
