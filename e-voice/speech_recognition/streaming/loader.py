"""FunASR 模型加载工具。"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from loguru import logger

try:
    import torch  # type: ignore
except Exception:  # pragma: no cover - 环境可能未安装 torch
    torch = None

try:  # pragma: no cover - 依赖环境不同
    from funasr import AutoModel  # type: ignore
except ImportError:  # pragma: no cover
    AutoModel = None
    logger.warning("FunASR AutoModel 未安装，Streaming 模型将以占位模式运行")


# 配置文件路径
CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


def load_funasr_config(filename: str = "realtime_funasr.yml") -> Dict[str, Any]:
    """加载 FunASR 实时配置。"""
    config_path = CONFIG_DIR / filename
    if not config_path.exists():
        logger.warning(f"FunASR 配置文件不存在: {config_path}，使用默认配置")
        return {}
    with config_path.open("r", encoding="utf-8") as fp:
        return yaml.safe_load(fp) or {}


@dataclass(slots=True)
class FunASRModelBundle:
    """FunASR 模型包。"""
    model_asr: Any  # 离线 ASR
    model_asr_online: Any  # 在线流式 ASR
    model_vad: Any  # VAD
    model_punc: Any  # 标点
    config: Dict[str, Any]  # 配置
    load_time_ms: float  # 加载耗时（毫秒）
    
    @property
    def is_valid(self) -> bool:
        """检查是否至少有一个可用的模型。"""
        return self.model_asr_online is not None or self.model_asr is not None


# 向后兼容别名
ModelBundle = FunASRModelBundle


class ModelLoader:
    """统一管理 FunASR 模型的加载与生命周期。"""

    _instance: "ModelLoader | None" = None

    def __init__(self) -> None:
        self._bundle: Optional[FunASRModelBundle] = None
        self._config: Dict[str, Any] = load_funasr_config()

    @classmethod
    def current(cls) -> "ModelLoader":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset(cls) -> None:
        """重置单例（用于测试）。"""
        cls._instance = None

    def load(self) -> FunASRModelBundle:
        """加载 FunASR 模型包。"""
        return self.load_funasr()

    def load_funasr(self) -> FunASRModelBundle:
        """
        加载 FunASR 模型包。
        
        基于 realtime_funasr.yml 配置加载模型，与 funasr_wss_server.py 使用相同的参数。
        """
        if self._bundle is not None:
            return self._bundle
        
        start_time = time.time()
        config = self._config
        
        # 获取资源配置
        resources = config.get("resources", {})
        ngpu = resources.get("ngpu", 1)
        ncpu = resources.get("ncpu", 4)
        device = resources.get("device", "cuda")

        # 记录运行设备/加速信息，方便确认是否走 GPU
        if torch:
            logger.info(
                f"加载 FunASR 模型前设备配置: device={device}, ngpu={ngpu}, torch_cuda_available={torch.cuda.is_available()}, cuda_devices={torch.cuda.device_count()}"
            )
        else:
            logger.warning("torch 未安装，无法检测 GPU，可将 resources.device 设置为 cpu")
        
        # 获取模型配置
        models_config = config.get("models", {})
        features = config.get("features", {})
        
        logger.info("开始加载 FunASR 模型...")
        
        # 加载离线 ASR 模型
        asr_config = models_config.get("asr", {})
        model_asr = self._create_model(
            model=asr_config.get("model"),
            revision=asr_config.get("revision"),
            ngpu=ngpu,
            ncpu=ncpu,
            device=device,
            model_type="离线 ASR",
        )
        
        # 加载在线流式 ASR 模型
        asr_online_config = models_config.get("asr_online", {})
        model_asr_online = self._create_model(
            model=asr_online_config.get("model"),
            revision=asr_online_config.get("revision"),
            ngpu=ngpu,
            ncpu=ncpu,
            device=device,
            model_type="在线流式 ASR",
        )
        
        # 加载 VAD 模型
        model_vad = None
        if features.get("enable_vad", True):
            vad_config = models_config.get("vad", {})
            model_vad = self._create_model(
                model=vad_config.get("model"),
                revision=vad_config.get("revision"),
                ngpu=ngpu,
                ncpu=ncpu,
                device=device,
                model_type="VAD",
            )
        
        # 加载标点模型
        model_punc = None
        if features.get("enable_punc", True):
            punc_config = models_config.get("punc", {})
            model_punc = self._create_model(
                model=punc_config.get("model"),
                revision=punc_config.get("revision"),
                ngpu=ngpu,
                ncpu=ncpu,
                device=device,
                model_type="标点",
            )
        
        load_time_ms = (time.time() - start_time) * 1000
        logger.info(f"FunASR 模型加载完成，耗时 {load_time_ms:.0f}ms")
        
        self._bundle = FunASRModelBundle(
            model_asr=model_asr,
            model_asr_online=model_asr_online,
            model_vad=model_vad,
            model_punc=model_punc,
            config=config,
            load_time_ms=load_time_ms,
        )
        
        return self._bundle

    def _create_model(
        self,
        model: Optional[str],
        revision: Optional[str],
        ngpu: int,
        ncpu: int,
        device: str,
        model_type: str = "",
    ) -> Any:
        """
        创建 FunASR 模型。
        
        与 funasr_wss_server.py 使用相同的参数。
        """
        if not model or AutoModel is None:
            if model:
                logger.warning(f"{model_type} 模型 {model} 无法加载：AutoModel 未安装")
            return None
        
        logger.info(f"加载 {model_type} 模型: {model} (revision={revision})")
        start = time.time()
        
        try:
            m = AutoModel(
                model=model,
                model_revision=revision,
                ngpu=ngpu,
                ncpu=ncpu,
                device=device,
                disable_pbar=True,
                disable_log=True,
            )
            elapsed = (time.time() - start) * 1000
            logger.info(f"{model_type} 模型加载成功，耗时 {elapsed:.0f}ms")
            return m
        except Exception as exc:
            logger.error(f"加载 {model_type} 模型 {model} 失败: {exc}")
            return None

    def get_bundle(self) -> FunASRModelBundle:
        """获取模型包。"""
        if self._bundle is None:
            return self.load()
        return self._bundle

    # 向后兼容别名
    get_funasr_bundle = get_bundle

    @property
    def config(self) -> Dict[str, Any]:
        """获取配置。"""
        return self._config

    # 向后兼容别名
    @property
    def funasr_config(self) -> Dict[str, Any]:
        """获取 FunASR 配置。"""
        return self._config

    def is_funasr_enabled(self) -> bool:
        """检查是否启用了 FunASR 流式引擎。"""
        features = self._config.get("features", {})
        return features.get("use_funasr_streamer", True)  # 默认启用

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查。
        
        返回模型加载状态和配置信息。
        """
        result = {
            "funasr_enabled": self.is_funasr_enabled(),
            "models": {},
            "config": {},
        }
        
        if self._bundle:
            result["models"] = {
                "asr": self._bundle.model_asr is not None,
                "asr_online": self._bundle.model_asr_online is not None,
                "vad": self._bundle.model_vad is not None,
                "punc": self._bundle.model_punc is not None,
            }
            result["load_time_ms"] = self._bundle.load_time_ms
        
        if self._config:
            result["config"] = {
                "mode": self._config.get("mode", {}).get("default", "2pass"),
                "chunk_interval": self._config.get("audio", {}).get("chunk_interval", 10),
                "features": self._config.get("features", {}),
            }
        
        return result


# 向后兼容：导出旧的函数名
def load_realtime_config(filename: str = "realtime_funasr.yml") -> Dict[str, Any]:
    """向后兼容的配置加载函数。"""
    return load_funasr_config(filename)
