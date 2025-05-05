"""
标准指标名称解析器模块
提供基于ChromaDB向量库的标准指标名称解析功能
"""

import os
import re
import time
import hashlib
import asyncio
import json
from datetime import datetime
from functools import lru_cache
from typing import Dict, List, Any, Optional, Set, Tuple
import chromadb
from chromadb.utils import embedding_functions
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient


class TargetExtractor:
    """标准指标名称解析器

    使用ChromaDB向量库对文档进行向量化，然后基于检索结果校准指标名称
    支持缓存机制和增量更新文档
    """

    def __init__(
        self,
        llm_config: Dict[str, Any],
        docs_dir: str,
        db_path: str = "./chroma_db",
        cache_size: int = 100,
        cache_ttl: int = 3600,
    ):
        """初始化标准指标名称解析器

        Args:
            llm_config: 语言模型配置，包含API密钥、基础URL等
            docs_dir: 文档目录路径
            db_path: ChromaDB数据库路径
            cache_size: 缓存大小，默认100条
            cache_ttl: 缓存过期时间，默认3600秒（1小时）
        """
        self.llm_config = llm_config
        self.docs_dir = docs_dir
        self.db_path = db_path
        self.cache_size = cache_size
        self.cache_ttl = cache_ttl

        # 初始化缓存
        self.query_cache = {}
        self.cache_timestamps = {}

        # 文档元数据缓存
        self.doc_metadata = {}
        self.metadata_file = os.path.join(db_path, "doc_metadata.json")
        self._load_metadata()

        # 创建模型客户端
        model_client = OpenAIChatCompletionClient(
            model=llm_config.get("model", "gpt-4o"),
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("base_url"),
            temperature=llm_config.get("temperature", 0.0),
            model_info=llm_config.get("model_info"),
        )

        # 创建标准指标名称解析智能体
        self.target_agent = AssistantAgent(
            name="target_extractor_agent",
            description="标准指标名称关键词识别器",
            system_message="""你是一个标准指标名称关键词识别器，可以对用户的输入进行校准，返回"标准指标"对应的名称。

根据检索到的语料知识库的上下文和用户的输入、找到最匹配的**标准名称**并且回复，你必须选择其中一个！

注意：
1. 只能返回检索到的"标准指标"名称后紧跟的指标名称
2. 禁止回复其他内容，不要给用户选择
""",
            model_client=model_client,
        )

        # 初始化ChromaDB客户端
        # self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        #     api_key=llm_config.get("api_key"), model_name="text-embedding-ada-002"
        # )

        # shibing624/text2vec-base-chinese：专门针对中文优化的语义向量模型，支持中文文本相似度计算
        # moka-ai/m3e-base：国内团队开发的多语言语义向量模型，对中文有很好的支持
        # BAAI/bge-small-zh：北京智源研究院开发的中文语义向量模型，性能优秀
        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="BAAI/bge-small-zh"
            )
        )

        # 创建数据库目录（如果不存在）
        os.makedirs(db_path, exist_ok=True)

        self.client = chromadb.PersistentClient(path=db_path)

        # 检查并创建集合
        try:
            self.collection = self.client.get_collection(
                name="target_docs", embedding_function=self.embedding_function
            )
            # 检查是否需要增量更新
            self._check_for_updates()
        except Exception as e:
            print(f"Collection not found, creating new one: {e}")
            # 集合不存在，需要创建并初始化
            self.collection = self.client.create_collection(
                name="target_docs", embedding_function=self.embedding_function
            )
            self._initialize_collection()

    def _load_metadata(self):
        """加载文档元数据"""
        try:
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    self.doc_metadata = json.load(f)
        except Exception as e:
            print(f"Error loading metadata: {e}")
            self.doc_metadata = {}

    def _save_metadata(self):
        """保存文档元数据"""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self.doc_metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving metadata: {e}")

    def _get_file_hash(self, file_path: str) -> str:
        """计算文件的MD5哈希值

        Args:
            file_path: 文件路径

        Returns:
            文件的MD5哈希值
        """
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _check_for_updates(self):
        """检查文档目录是否有更新，并进行增量更新"""
        # 获取当前文档列表
        current_files = {}
        new_files = []
        updated_files = []
        removed_files = []

        # 遍历文档目录，检查新增和更新的文件
        for filename in os.listdir(self.docs_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(self.docs_dir, filename)
                try:
                    # 计算文件的哈希值
                    file_hash = self._get_file_hash(file_path)
                    current_files[filename] = file_hash

                    # 检查文件是否已存在于元数据中
                    if filename not in self.doc_metadata:
                        # 新文件
                        new_files.append(filename)
                    elif self.doc_metadata[filename]["hash"] != file_hash:
                        # 文件已更新
                        updated_files.append(filename)
                except Exception as e:
                    print(f"Error checking file {filename}: {e}")

        # 检查已删除的文件
        for filename in self.doc_metadata:
            if filename not in current_files and filename.endswith(".md"):
                removed_files.append(filename)

        # 如果有变更，进行增量更新
        if new_files or updated_files or removed_files:
            print(
                f"Found changes: {len(new_files)} new, {len(updated_files)} updated, {len(removed_files)} removed"
            )
            self._update_collection(
                new_files, updated_files, removed_files, current_files
            )
        else:
            print("No document changes detected")

    def _update_collection(
        self,
        new_files: List[str],
        updated_files: List[str],
        removed_files: List[str],
        current_files: Dict[str, str],
    ):
        """更新向量库集合

        Args:
            new_files: 新增文件列表
            updated_files: 更新文件列表
            removed_files: 删除文件列表
            current_files: 当前文件哈希值字典
        """
        # 处理删除的文件
        if removed_files:
            ids_to_remove = []
            for filename in removed_files:
                if filename in self.doc_metadata:
                    ids_to_remove.append(self.doc_metadata[filename]["id"])
                    del self.doc_metadata[filename]

            if ids_to_remove:
                self.collection.delete(ids=ids_to_remove)
                print(f"Removed {len(ids_to_remove)} documents from the collection")

        # 处理新增和更新的文件
        files_to_process = new_files + updated_files
        if files_to_process:
            documents = []
            metadatas = []
            ids = []

            for filename in files_to_process:
                file_path = os.path.join(self.docs_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 如果是更新的文件，使用原来的ID
                    if filename in self.doc_metadata:
                        doc_id = self.doc_metadata[filename]["id"]
                        # 先删除旧文档
                        self.collection.delete(ids=[doc_id])
                    else:
                        # 新文件生成新ID
                        doc_id = f"doc_{int(time.time())}_{len(ids)}"

                    # 添加到集合
                    documents.append(content)
                    metadatas.append({"source": filename})
                    ids.append(doc_id)

                    # 更新元数据
                    self.doc_metadata[filename] = {
                        "id": doc_id,
                        "hash": current_files[filename],
                        "updated_at": datetime.now().isoformat(),
                    }
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

            # 批量添加到集合
            if documents:
                self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
                print(f"Added/Updated {len(documents)} documents in the collection")

        # 保存元数据
        self._save_metadata()

        # 清除缓存
        self.query_cache = {}
        self.cache_timestamps = {}

    def _split_document(self, content, max_chunk_size=1000):
        """将文档按空行分割成多个块

        Args:
            content: 文档内容
            max_chunk_size: 最大块大小

        Returns:
            List[str]: 分割后的文档块列表
        """
        # 按空行分割文档
        paragraphs = re.split(r"\n\s*\n", content)

        # 过滤空段落
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        # 合并小段落，避免过度分割
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            # 如果当前块加上新段落不超过最大大小，则添加到当前块
            if len(current_chunk) + len(para) < max_chunk_size:
                if current_chunk:
                    current_chunk += "\n\n"
                current_chunk += para
            else:
                # 如果当前块不为空，添加到chunks
                if current_chunk:
                    chunks.append(current_chunk)
                # 开始新块
                current_chunk = para

        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)

        # 确保每个块都包含有意义的内容
        chunks = [chunk for chunk in chunks if len(chunk) > 50]  # 忽略过小的块

        return chunks

    def _initialize_collection(self):
        """初始化集合，加载文档并向量化"""
        documents = []
        metadatas = []
        ids = []
        current_files = {}

        # 遍历文档目录
        for filename in os.listdir(self.docs_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(self.docs_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # 计算文件的哈希值
                    file_hash = self._get_file_hash(file_path)
                    current_files[filename] = file_hash

                    # 分割文档内容
                    chunks = self._split_document(content)

                    # 为每个块创建ID和元数据
                    base_time = int(time.time())
                    for i, chunk in enumerate(chunks):
                        chunk_id = f"doc_{base_time}_{filename}_{i}"
                        documents.append(chunk)
                        metadatas.append(
                            {
                                "source": filename,
                                "chunk_index": i,
                                "total_chunks": len(chunks),
                            }
                        )
                        ids.append(chunk_id)

                    # 更新元数据 - 只保存文件级别的元数据
                    self.doc_metadata[filename] = {
                        "id_prefix": f"doc_{base_time}_{filename}",
                        "hash": file_hash,
                        "updated_at": datetime.now().isoformat(),
                        "chunks": len(chunks),
                    }
                except Exception as e:
                    print(f"Error processing {filename}: {e}")

        # 批量添加到集合
        if documents:
            self.collection.add(documents=documents, metadatas=metadatas, ids=ids)
            print(
                f"Added {len(documents)} chunks from {len(self.doc_metadata)} documents to the collection"
            )

            # 保存元数据
            self._save_metadata()

    async def extract_target_async(
        self, query_text: str, top_k: int = 5, bypass_cache: bool = False
    ) -> str:
        """异步从文本中提取标准指标名称

        Args:
            query_text: 用户查询文本
            top_k: 检索结果数量
            bypass_cache: 是否绕过缓存

        Returns:
            str: 提取的标准指标名称
        """
        # 查询规范化（去除多余空格等）
        normalized_query = " ".join(query_text.split()).lower()

        # 检查缓存
        current_time = time.time()
        if not bypass_cache and normalized_query in self.query_cache:
            cache_time = self.cache_timestamps.get(normalized_query, 0)
            # 检查缓存是否过期
            if current_time - cache_time < self.cache_ttl:
                print(f"Cache hit for query: {normalized_query}")
                return self.query_cache[normalized_query]
            else:
                # 缓存过期，删除
                del self.query_cache[normalized_query]
                del self.cache_timestamps[normalized_query]

        # 增加检索数量，因为我们是按块检索的
        query_results = self.collection.query(
            query_texts=[normalized_query],
            n_results=top_k * 2,  # 增加检索数量，确保有足够的上下文
            include=["metadatas", "documents"],
        )

        # 构建上下文，按文档源分组并重新组织
        context = ""
        if query_results and query_results["documents"]:
            # 按源文件分组
            docs_by_source = {}
            for i, (doc, metadata) in enumerate(
                zip(query_results["documents"][0], query_results["metadatas"][0])
            ):
                source = metadata["source"]
                if source not in docs_by_source:
                    docs_by_source[source] = []
                docs_by_source[source].append((doc, metadata))

            # 为每个源文件构建上下文
            for source, docs in docs_by_source.items():
                # 按块索引排序
                docs.sort(key=lambda x: x[1].get("chunk_index", 0))

                # 合并同一文档的块
                source_content = "\n\n".join([doc[0] for doc in docs])
                context += f"文档 {source}:\n{source_content}\n\n"

                # 限制上下文长度
                if len(context) > 4000:
                    context = context[:4000] + "...(内容已截断)"
                    break

        # 构建提示词
        prompt = f"""检索到的上下文是：
{context}

## 角色
你是一个标准指标名称关键词识别器，可以对用户的输入进行校准，返回"标准指标"对应的名称

## 能力
根据检索到的语料知识库的上下文和用户的输入，进行分析比较语义，找到最匹配的**标准名称**并且回复，你必须选择其中一个！

注意：
1. 只能返回检索到的"标准指标"名称后紧跟的指标名称！
2. 禁止回复其他内容，不要让用户进行选择

用户输入: "{query_text}"
"""

        # 异步调用标准指标名称解析智能体
        result = await self.target_agent.run(task=prompt)

        # 从 TaskResult 对象中获取响应内容
        response = result.messages[-1].content

        # 清理响应，确保只返回标准指标名称
        response = response.strip()

        # 更新缓存
        self._update_cache(normalized_query, response)

        return response

    def _update_cache(self, query: str, response: str):
        """更新查询缓存

        Args:
            query: 规范化后的查询文本
            response: 响应结果
        """
        # 检查缓存大小，如果超过限制，删除最早的条目
        if len(self.query_cache) >= self.cache_size:
            # 找到最早的缓存项
            oldest_query = min(self.cache_timestamps.items(), key=lambda x: x[1])[0]
            del self.query_cache[oldest_query]
            del self.cache_timestamps[oldest_query]

        # 添加新缓存
        self.query_cache[query] = response
        self.cache_timestamps[query] = time.time()

    def extract_target(
        self, query_text: str, top_k: int = 3, bypass_cache: bool = False
    ) -> str:
        """同步从文本中提取标准指标名称（兼容旧版接口）

        Args:
            query_text: 用户查询文本
            top_k: 检索结果数量
            bypass_cache: 是否绕过缓存

        Returns:
            str: 提取的标准指标名称
        """
        # 使用事件循环运行异步方法
        return asyncio.run(self.extract_target_async(query_text, top_k, bypass_cache))
