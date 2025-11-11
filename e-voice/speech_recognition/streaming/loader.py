"""FunASR 模型加载工具。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from loguru import logger

try:  # pragma: no cover - 依赖环境不同
    from funasr import AutoModel  # type: ignore
except ImportError:  # pragma: no cover
    AutoModel = None
    logger.warning("FunASR AutoModel 未安装，Streaming 模型将以占位模式运行")

from config import load_realtime_config


@dataclass(slots=True)
class ModelBundle:
    vad: Any
    online_asr: Any
    offline_asr: Any
    punc: Any
    itn: Any
    meta: Dict[str, Any]


class ModelLoader:
    """统一管理 FunASR 模型的加载与生命周期。"""

    _instance: "ModelLoader | None" = None

    def __init__(self) -> None:
        self._bundle: Optional[ModelBundle] = None
        self._config: Dict[str, Any] = load_realtime_config()

    @classmethod
    def current(cls) -> "ModelLoader":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def load(self) -> ModelBundle:
        if self._bundle is not None:
            return self._bundle

        models = self._config.get("models", {})
        device = self._config.get("resources", {}).get("device", "auto")
        ngpu = 1 if device in {"auto", "gpu", "cuda"} else 0
        ncpu = self._config.get("resources", {}).get("offline_thread_pool", 4)

        vad_model = self._create_model(models.get("vad"), ngpu=ngpu, ncpu=ncpu, device=device)
        online_model = self._create_model(
            models.get("online_asr"), ngpu=ngpu, ncpu=ncpu, device=device
        )
        offline_model = self._create_model(
            models.get("offline_asr"), ngpu=ngpu, ncpu=ncpu, device=device
        )
        punc_model = self._create_model(models.get("punc"), ngpu=ngpu, ncpu=ncpu, device=device)
        itn_model = self._create_model(models.get("itn"), ngpu=0, ncpu=ncpu, device="cpu")

        self._bundle = ModelBundle(
            vad=vad_model,
            online_asr=online_model,
            offline_asr=offline_model,
            punc=punc_model,
            itn=itn_model,
            meta={"models": models},
        )
        return self._bundle

    def _create_model(self, model_name: Optional[str], *, ngpu: int, ncpu: int, device: str) -> Any:
        if not model_name or AutoModel is None:
            return None
        logger.info(f"加载 FunASR 模型: {model_name}")
        try:
            return AutoModel(
                model=model_name,
                ngpu=ngpu,
                ncpu=ncpu,
                device=None if device == "auto" else device,
                disable_pbar=True,
                disable_log=True,
            )
        except Exception as exc:  # pragma: no cover - 依赖 ModelScope 环境
            logger.error("加载模型 %s 失败: %s", model_name, exc)
            return None

    def get_bundle(self) -> ModelBundle:
        if self._bundle is None:
            return self.load()
        return self._bundle

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

