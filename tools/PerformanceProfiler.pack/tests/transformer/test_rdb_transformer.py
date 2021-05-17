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
                        "query_id": None,
                    }
                ],
            }
        ],
        "queries": [
            {
                "query": "SELECT template_meta_template_id, template_meta_type, template_meta_vchar, template_meta_vchar_idx, template_meta_vdatetime, template_meta_vdatetime_idx, template_meta_vinteger, template_meta_vinteger_idx, template_meta_vfloat, template_meta_vfloat_idx, template_meta_vblob, template_meta_vclob\nFROM mt_template_meta\nWHERE (template_meta_template_id = ?)\nORDER BY template_meta_template_id ASC, template_meta_type ASC\n",
                "id": "rVCfQbiq5Q36E9AD6M22mXsb19o=",
                "identifier": "MdG5Nfn324F5KfGGnY3Il3clCT4=",
            }
        ],
    }
