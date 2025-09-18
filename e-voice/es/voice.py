# 创建带有向量字段的索引

from elasticsearch.helpers import bulk

from es.conn import es, create_index, delete_by_id
from pipeline.spk_v_pipeline import embeddings

# 定义索引映射，包含向量字段
mapping = {
    "mappings": {
        "properties": {
            "username": {"type": "text"},
            "userid": {"type": "integer"},
            "wav_path": {"type": "text"},
            "create_time": {"type": "long"},
            "embeddings": {
                "type": "dense_vector",
                "index": True,
                "similarity": "cosine",  # 使用cosine
                "dims": 192  # 向量维度 与向量模型保持一致
            },
            "metadata": {
                "type": "object"
            }
        }
    }
}

index_name = "voice_print"
create_index(index_name, mapping)


# 插入单条数据
def insert_voice(username, userid, wav_path, txt, create_time, eb, doc_id=None, metadata=None):
    # 将numpy数组转换为普通Python列表以避免NumPy 2.0兼容性问题
    eb = eb.tolist() if hasattr(eb, 'tolist') else eb
    document = {
        "username": username,
        "userid": userid,
        "wav_path": wav_path,
        "txt": txt,
        "create_time": create_time,
        "embeddings": eb,
        "metadata": metadata or {}
    }

    response = es.index(
        id=doc_id,  # 如果不指定，则会自动生成一个id
        index=index_name,
        document=document
    )
    return response


# 批量插入数据
def insert_documents(documents):
    """
    批量插入文档到Elasticsearch
    
    Args:
        index_name (str): 索引名称
        documents (list): 文档列表，每个文档应包含id, title, content, img, type, embeddings, metadata等字段
    
    Returns:
        dict: 批量插入结果
    """
    actions = []
    for doc in documents:
        eb = doc.get("eb")
        eb = eb.tolist() if hasattr(eb, 'tolist') else eb

        action = {
            "_index": index_name,
            "_id": doc.get("id"),
            "_source": {
                "id": doc.get("id"),
                "username": doc.get("username"),
                "userid": doc.get("userid"),
                "wav_path": doc.get("wav_path"),
                "txt": doc.get("txt"),
                "create_time": doc.get("create_time"),
                "embeddings": eb,
                "metadata": doc.get("metadata", {})
            }
        }
        actions.append(action)

    try:
        response = bulk(es, actions, max_retries=3)
        return {
            "success": True,
            "items_count": len(response[1]),
            "errors": []
        }
    except Exception as e:
        return {
            "success": False,
            "items_count": 0,
            "errors": [str(e)]
        }


_source = ["id", "username", "userid", "wav_path", "txt", "create_time"]


# 向量相似度搜索
def search_voice_vector(query_vector, top_k=5):
    query_vector = query_vector.tolist() if hasattr(query_vector, 'tolist') else query_vector

    """
    使用L2距离进行向量搜索

    Args:
        index_name (str): 索引名称
        query_vector (list or np.ndarray): 查询向量
        top_k (int): 返回结果数量
    Returns:
        dict: 搜索结果
    """
    query = {
        "knn": {
            "field": "embeddings",
            "query_vector": query_vector,
            "k": top_k,
            "num_candidates": 100
        },
        "_source": _source,
        "min_score": "0.6"
    }

    # knn搜索和query混合使用
    # POST test-index/_search
    # {
    #   "query": {
    #     "match": {
    #       "title": {
    #         "query": "mountain lake",
    #         "boost": 0.9
    #       }
    #     }
    #   },
    #   "knn": {
    #     "field": "embeddings",
    #     "query_vector": [54, 10, -2],
    #     "k": 5,
    #     "num_candidates": 50,
    #     "boost": 0.1
    #   },
    #   "size": 10
    # }

    response = es.search(index=index_name, body=query)
    return deal_es_search_response(response)


def multi_search_voice_vector(query_vectors, top_k=5):
    """
       使用多个向量进行KNN搜索
       Args:
           query_vectors (list): 查询向量列表
           top_k (int): 返回结果数量

       Returns:
           dict: 搜索结果
       """
    # 构建多个knn查询
    knn_queries = []
    for vector in query_vectors:
        vector = vector.tolist() if hasattr(vector, 'tolist') else vector

        knn_queries.append({
            "field": "embeddings",
            "query_vector": vector.tolist() if hasattr(vector, 'tolist') else vector,
            "k": top_k,
            "num_candidates": 100
        })

    query = {
        "knn": knn_queries,
        "_source": _source,
        "min_score": 0.6 * len(query_vectors),
    }

    response = es.search(index=index_name, body=query)
    return deal_es_search_response(response)


def deal_es_search_response(response):
    result = []
    if response.meta.status == 200:
        if response.body['hits'] and response.body['hits']['hits']:

            for item in response.body['hits']['hits']:
                src = item['_source']
                src['_score'] = item['_score']
                src['id'] = item['_id']
                result.append(src)

    return result


def list_by_userid(userid, page: int = 1, limit: int = 10):
    response = es.search(
        index=index_name,
        query={
            "match": {
                "userid": userid
            }
        },
        from_=(page - 1) * limit,
        size=limit,
        _source=_source,

    )

    result = {
        "total": response.body['hits']['total']['value'],
        "data": deal_es_search_response(response)
    }

    return result


if __name__ == '__main__':
    ebs = embeddings([
        "../resource/audio_data/0/014.wav",
        "../resource/audio_data/0/015.wav",
        "../resource/audio_data/1/005.wav",
        "../resource/audio_data/1/067.wav",
        "../resource/audio_data/3/1.wav",
        "../resource/audio_data/3/3.wav"
    ])

    # 将numpy数组转换为普通Python列表以避免NumPy 2.0兼容性问题
    ebs_list = [eb.tolist() if hasattr(eb, 'tolist') else eb for eb in ebs]

    insert_voice("username1", 1, "img1", "type1", 1753841500185, ebs_list[0], 1)
    insert_voice("username1", 1, "img1", "type1", 1753841500185, ebs_list[1], 2)
    insert_voice("username2", 2, "img1", "type1", 1753841500185, ebs_list[2], 3)
    insert_voice("username2", 2, "img1", "type1", 1753841500185, ebs_list[3], 4)
    insert_voice("username3", 3, "img1", "type1", 1753841500185, ebs_list[4], 5)
    insert_voice("username3", 3, "img1", "type1", 1753841500185, ebs_list[5], 6)

    res = search_voice_vector(ebs_list[4])
    print(res)

    res = search_voice_vector(ebs_list[3])
    print(res)

    res = search_voice_vector(ebs_list[0])
    print(res)

    res = list_by_userid(1)
    print(res)

    res = delete_by_id(index_name, 1)
    print(res)

    res = multi_search_voice_vector([ebs_list[0], ebs_list[1]])
    print(res)
