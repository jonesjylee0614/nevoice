from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from loguru import logger

from config.config import conf

es_conf = conf["es"]

# 连接到 Elasticsearch
es = Elasticsearch(
    hosts=[es_conf["host"]],  # ES 地址
    http_auth=(es_conf["username"], es_conf["password"]),  # 如果有认证
    verify_certs=False,  # 如果是自签名证书
    request_timeout=30,
    max_retries=10,
    retry_on_timeout=True,
)


def create_index(index_name: str, mapping):
    try:
        # 创建索引
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name, body=mapping)
            print(f"索引 {index_name} 创建成功")
    except Exception as e:
        logger.error(f"创建索引 {index_name} 失败：{e}")


# 删除单个文档
def delete_by_id(index_name, doc_id):
    try:
        response = es.delete(index=index_name, id=doc_id)
        return response
    except Exception as e:
        print(f"删除失败: {e}")


# 批量删除文档
def delete_by_ids(index_name, doc_ids):
    """
    批量删除文档

    Args:
        index_name (str): 索引名称
        doc_ids (list): 要删除的文档ID列表

    Returns:
        dict: 批量删除结果
    """
    actions = []
    for doc_id in doc_ids:
        action = {"_op_type": "delete", "_index": index_name, "_id": doc_id}
        actions.append(action)

    try:
        response = bulk(es, actions, max_retries=3)
        return {"success": True, "items_count": len(response[1]), "errors": []}
    except Exception as e:
        return {"success": False, "items_count": 0, "errors": [str(e)]}
