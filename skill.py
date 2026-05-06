#!/usr/bin/env python3
"""
Skill兼容入口

新结构请使用：
  python -m skill <command>
  或直接调用 skill/skill.py

本文件保持兼容。
"""
import sys
from pathlib import Path

# 添加父目录到路径，让skill目录可导入
sys.path.insert(0, str(Path(__file__).parent))

# 导入实际的skill模块
from skill.skill import search, query_history

if __name__ == "__main__":
    # 重新执行到skill子目录
    import subprocess
    import os
    script_path = Path(__file__).parent / "skill" / "skill.py"
    os.execv(sys.executable, [sys.executable, str(script_path)] + sys.argv[1:])
