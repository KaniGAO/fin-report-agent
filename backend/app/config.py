"""全局配置"""
from pathlib import Path

# 模糊匹配阈值（0-100），达到该分数才视为匹配
MATCH_THRESHOLD = 85

# 上传限制
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
ALLOWED_DOCX = {".docx"}
ALLOWED_EXCEL = {".xlsx", ".xls"}

# 临时目录（存放上传文件与生成结果）
TMP_DIR = Path(__file__).resolve().parent.parent / "tmp"
TMP_DIR.mkdir(exist_ok=True)
