# main.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import requests
from urllib.parse import urlparse

app = FastAPI()

@app.get("/proxy/video")
async def video_proxy(request: Request):
    return await proxy_video(request, download=False)

@app.get("/proxy/download")
async def dwn_proxy(request: Request):
    return await proxy_video(request, download=True)

async def proxy_video(request: Request, download: bool = False):
    video_url = request.query_params.get("url")
    if not video_url:
        raise HTTPException(status_code=400, detail="Missing 'url' parameter")

    # 解析URL，确保只代理特定域名的请求
    parsed_url = urlparse(video_url)
    if not (parsed_url.netloc.endswith(".akamaized.net") or parsed_url.netloc.endswith(".bilivideo.com")):
        raise HTTPException(status_code=403, detail="URL not allowed")

    # 设置需要的请求头，模拟浏览器请求
    headers = {
        "Referer": "https://www.bilibili.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    }

    # 发起对目标视频的请求
    response = requests.get(video_url, headers=headers, stream=True)

    # 如果请求失败，返回错误信息
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to retrieve video")

    # 返回流响应给前端
    def iterfile():
        for chunk in response.iter_content(chunk_size=1024):
            yield chunk

    content_disposition = "attachment; filename=\"{}\"".format(parsed_url.path.split('/')[-1]) if download else "inline"
    return StreamingResponse(iterfile(), media_type=response.headers.get("Content-Type", "application/octet-stream"), headers={"Content-Disposition": content_disposition})
