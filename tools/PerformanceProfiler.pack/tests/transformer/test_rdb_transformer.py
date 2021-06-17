import pytest

from performance_profiler.transformer.rdb_transformer import RDBTransformer

transformer = RDBTransformer()


def test_transform():
    data = transformer.transform(
        {
            "build": {
                "file": "1db8f6cf7923be9c5694945eda20ce50719e19b1",
                "version": "6.7",
                "product_version": "6.7.8",
                "runtime": 0.35336,
                "timestamp": "2021-04-26T00:16:36Z",
                "instance_id": "32b57e3dc152",
                "archive_type": "index",
                "id": "7b28a232f123584b26d2caa4ef53adf4a9823975",
            },
            "logs": [
                {
                    "runtime": 0.405,
                    "package": "MT::Template",
                    "line": 408,
                    "query": "SELECT template_meta_template_id, template_meta_type, template_meta_vchar, template_meta_vchar_idx, template_meta_vdatetime, template_meta_vdatetime_idx, template_meta_vinteger, template_meta_vinteger_idx, template_meta_vfloat, template_meta_vfloat_idx, template_meta_vblob, template_meta_vclob\nFROM mt_template_meta\nWHERE (template_meta_template_id = ?)\nORDER BY template_meta_template_id ASC, template_meta_type ASC\n",
                }
            ],
        }
    )

    assert data == {
        "builds": [
            {
                "id": "7b28a232f123584b26d2caa4ef53adf4a9823975",
                "file": "1db8f6cf7923be9c5694945eda20ce50719e19b1",
                "version": "6.7",
                "product_version": "6.7.8",
                "runtime": 0.35336,
                "timestamp": "2021-04-26T00:16:36Z",
                "instance_id": "32b57e3dc152",
                "archive_type": "index",
                "logs": [
                    {
                        "runtime": 0.405,
                        "package": "MT::Template",
                        "line": 408,
                        "query_id": "rVCfQbiq5Q36E9AD6M22mXsb19o=",
                    }
                ],
            }
        ],
        "queries": [
            {
                "query": "SELECT template_meta_template_id, template_meta_type, template_meta_vchar, template_meta_vchar_idx, template_meta_vdatetime, template_meta_vdatetime_idx, template_meta_vinteger, template_meta_vinteger_idx, template_meta_vfloat, template_meta_vfloat_idx, template_meta_vblob, template_meta_vclob\nFROM mt_template_meta\nWHERE (template_meta_template_id = ?)\nORDER BY template_meta_template_id ASC, template_meta_type ASC\n",
                "id": "rVCfQbiq5Q36E9AD6M22mXsb19o=",
                "identifier": "btjKTutzM9oyJlbV5jnfzjhw0Rk=",
                "structure": '{"select": [{"value": "template_meta_template_id"}, {"value": "template_meta_type"}, {"value": "template_meta_vblob"}, {"value": "template_meta_vchar"}, {"value": "template_meta_vchar_idx"}, {"value": "template_meta_vclob"}, {"value": "template_meta_vdatetime"}, {"value": "template_meta_vdatetime_idx"}, {"value": "template_meta_vfloat"}, {"value": "template_meta_vfloat_idx"}, {"value": "template_meta_vinteger"}, {"value": "template_meta_vinteger_idx"}], "from": "mt_template_meta", "where": {"eq": ["template_meta_template_id", "$v"]}, "orderby": [{"value": "template_meta_template_id", "sort": "asc"}, {"value": "template_meta_type", "sort": "asc"}]}',
            }
        ],
    }


def test_transform_unsupported_query():
    data = transformer.transform(
        {
            "build": {
                "file": "1db8f6cf7923be9c5694945eda20ce50719e19b1",
                "version": "6.7",
                "product_version": "6.7.8",
                "runtime": 0.35336,
                "timestamp": "2021-04-26T00:16:36Z",
                "instance_id": "32b57e3dc152",
                "archive_type": "index",
                "id": "7b28a232f123584b26d2caa4ef53adf4a9823975",
            },
            "logs": [
                {
                    "runtime": 0.405,
                    "package": "MT::Template",
                    "line": 408,
                    "query": "INSERT INTO mt_entry (entry_title) VALUES ('a')",
                }
            ],
        }
    )

    assert data == {
        "builds": [
            {
                "file": "1db8f6cf7923be9c5694945eda20ce50719e19b1",
                "version": "6.7",
                "product_version": "6.7.8",
                "runtime": 0.35336,
                "timestamp": "2021-04-26T00:16:36Z",
                "instance_id": "32b57e3dc152",
                "archive_type": "index",
                "id": "7b28a232f123584b26d2caa4ef53adf4a9823975",
                "logs": [
                    {
                        "runtime": 0.405,
                        "package": "MT::Template",
                        "line": 408,
                        "query_id": "9OhE2nWQ3p06nGcdcyql3O2Vt+4=",
                    }
                ],
            }
        ],
        "queries": [
            {
                "query": "INSERT INTO mt_entry (entry_title) VALUES ('a')",
                "id": "9OhE2nWQ3p06nGcdcyql3O2Vt+4=",
                "identifier": "9OhE2nWQ3p06nGcdcyql3O2Vt+4=",
                "structure": "{}",
            }
        ],
    }
