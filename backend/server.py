from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import sys
from pathlib import Path
from typing import Dict

# 将项目根目录添加到 python path，以便导入 utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_utils import get_file_content

app = FastAPI(title="文件内容提取服务")

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, str]:
    """
    上传文件并提取内容
    """
    try:
        # 保存上传的文件
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 提取内容
        try:
            content = get_file_content(Path(file_path))
            return {"filename": file.filename, "content": content}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文件解析失败: {str(e)}")
        finally:
            # 清理临时文件
            if os.path.exists(file_path):
                os.remove(file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "文件提取服务正在运行"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
