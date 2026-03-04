#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube视频搬运工具 - 完整版
"""
import os
import sys
import json
import time
import hashlib
import subprocess
import tempfile
import requests
from pathlib import Path

CONFIG_FILE = "config.json"

class YouTubeUploader:
    def __init__(self, base_url: str = "https://miaoju.hydun.com"):
        self.base_url = base_url.rstrip('/')
        self.token = None
        self.session = requests.Session()
        self.session.trust_env = True  # 使用系统代理
        self.yt_dlp = r"C:\Users\hekuo\AppData\Local\Python\pythoncore-3.14-64\Scripts\yt-dlp.exe"

    def login(self, email: str, password: str) -> bool:
        """登录"""
        url = f"{self.base_url}/api/v1/auth/login"
        payload = {"email": email, "password": password}

        try:
            response = self.session.post(url, json=payload)
            data = response.json()

            if data.get("code") == 200:
                self.token = data["data"]["token"]
                print(f"登录成功")
                return True
            else:
                print(f"登录失败：{data.get('msg')}")
                return False
        except Exception as e:
            print(f"登录异常：{e}")
            return False

    def get_auth_headers(self):
        return {"Authorization": self.token or "", "Content-Type": "application/json"}

    def calculate_file_hash(self, file_path: str) -> str:
        """计算MD5"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def upload_image(self, image_path: str):
        """上传封面图片"""
        url = f"{self.base_url}/api/v1/upload/image"

        try:
            # 如果是 webp，转换为 jpg
            if image_path.endswith('.webp'):
                from PIL import Image
                img = Image.open(image_path)
                jpg_path = image_path.replace('.webp', '.jpg')
                img.convert('RGB').save(jpg_path, 'JPEG')
                image_path = jpg_path

            with open(image_path, 'rb') as f:
                files = {'image': f}
                headers = {"Authorization": self.token or ""}
                response = self.session.post(url, files=files, headers=headers)
                data = response.json()

                if data.get("code") == 200:
                    cover_url = data["data"]["url"]
                    print(f"封面上传成功: {cover_url}")
                    return cover_url
                else:
                    print(f"封面上传失败：{data.get('msg')}，将使用空封面")
                    return ""
        except Exception as e:
            print(f"封面上传异常：{e}，将使用空封面")
            return ""

    def download_youtube(self, url: str, output_dir: str):
        """下载YouTube视频"""
        video_path = os.path.join(output_dir, "video.mp4")

        print(f"下载视频: {url}")
        cmd = [self.yt_dlp, "-f", "best[ext=mp4]", "-o", video_path, url]
        subprocess.run(cmd, check=True, capture_output=True)

        print("下载封面...")
        cmd = [self.yt_dlp, "--write-thumbnail", "--skip-download", "--convert-thumbnails", "jpg", "-o", os.path.join(output_dir, "cover"), url]
        subprocess.run(cmd, capture_output=True)

        print("获取元数据...")
        cmd = [self.yt_dlp, "-j", url]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        metadata = json.loads(result.stdout)

        title = metadata.get("title", "Untitled")
        desc = metadata.get("description", "")

        # 找到下载的封面文件
        cover_file = None
        for f in os.listdir(output_dir):
            if f.startswith("cover") and (f.endswith('.jpg') or f.endswith('.webp') or f.endswith('.png')):
                cover_file = os.path.join(output_dir, f)
                break

        print(f"下载完成: {title}")
        return video_path, cover_file, title, desc

    def upload_video_chunk(self, video_path: str, file_hash: str,
                          chunk_index: int, total_chunks: int,
                          chunk_size: int = 5 * 1024 * 1024) -> bool:
        """上传分片"""
        url = f"{self.base_url}/api/v1/upload/chunkVideo"

        try:
            with open(video_path, 'rb') as f:
                f.seek(chunk_index * chunk_size)
                chunk_data = f.read(chunk_size)

            files = {'video': ('chunk', chunk_data, 'application/octet-stream')}
            data = {
                'hash': file_hash,
                'name': os.path.basename(video_path),
                'chunkIndex': chunk_index,
                'totalChunks': total_chunks
            }

            headers = {"Authorization": self.token or ""}
            response = self.session.post(url, files=files, data=data, headers=headers)
            result = response.json()

            return result.get("code") == 200
        except:
            return False

    def merge_video_chunks(self, file_hash: str) -> bool:
        """合并分片"""
        url = f"{self.base_url}/api/v1/upload/mergeVideo"
        payload = {"hash": file_hash}

        try:
            response = self.session.post(url, json=payload, headers=self.get_auth_headers())
            data = response.json()
            return data.get("code") == 200
        except:
            return False

    def create_video_resource(self, file_hash: str):
        """创建视频资源"""
        url = f"{self.base_url}/api/v1/upload/video"
        payload = {"hash": file_hash}

        try:
            response = self.session.post(url, json=payload, headers=self.get_auth_headers())
            data = response.json()

            if data.get("code") == 200:
                return data["data"]["resource"]
            return None
        except:
            return None

    def upload_video_info(self, vid: int, title: str, cover: str,
                         desc: str = "", partition_id: int = 2) -> bool:
        """上传视频信息"""
        url = f"{self.base_url}/api/v1/video/uploadVideoInfo"
        payload = {
            "vid": vid,
            "title": title,
            "cover": cover,
            "desc": desc,
            "copyright": False,
            "tags": "",
            "partitionId": partition_id
        }

        try:
            response = self.session.post(url, json=payload, headers=self.get_auth_headers())
            data = response.json()

            if data.get("code") == 200:
                print(f"视频信息上传成功")
                return True
            else:
                print(f"视频信息上传失败：{data.get('msg')}")
                return False
        except Exception as e:
            print(f"异常：{e}")
            return False

    def upload_from_youtube(self, youtube_url: str):
        """从YouTube下载并上传"""
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # 下载
                video_path, cover_path, title, desc = self.download_youtube(youtube_url, tmpdir)

                # 上传封面
                cover_url = ""
                if cover_path and os.path.exists(cover_path):
                    print("上传封面...")
                    cover_url = self.upload_image(cover_path) or ""

                # 计算hash
                print(f"\n开始上传: {Path(video_path).name}")
                file_hash = self.calculate_file_hash(video_path)
                print(f"Hash: {file_hash}")

                # 上传分片
                file_size = os.path.getsize(video_path)
                chunk_size = 5 * 1024 * 1024
                total_chunks = (file_size + chunk_size - 1) // chunk_size

                for i in range(total_chunks):
                    print(f"   上传分片 {i + 1}/{total_chunks}...", end=" ")
                    if self.upload_video_chunk(video_path, file_hash, i, total_chunks, chunk_size):
                        print("成功")
                    else:
                        print("失败")
                        raise Exception("分片上传失败")
                    time.sleep(0.1)

                # 合并
                print("合并视频分片...")
                if not self.merge_video_chunks(file_hash):
                    raise Exception("合并失败")
                print("合并成功")

                # 创建资源
                print("创建视频资源...")
                resource = self.create_video_resource(file_hash)
                if not resource:
                    raise Exception("创建资源失败")
                vid = resource["vid"]
                print(f"视频ID: {vid}")

                # 等待视频处理完成
                print("等待视频处理（15秒）...")
                time.sleep(15)

                # 上传元数据
                print("上传视频信息...")
                self.upload_video_info(vid, title, cover_url, desc[:200])

                print(f"完成！视频链接: {self.base_url}/video/{vid}")
                return True

        except Exception as e:
            print(f"错误: {e}")
            return False


def main():
    print("=" * 60)
    print("YouTube视频搬运工具")
    print("=" * 60)

    # 加载配置
    if not os.path.exists(CONFIG_FILE):
        print("config.json not found")
        sys.exit(1)

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # 初始化
    uploader = YouTubeUploader()

    # 登录
    print("\n登录中...")
    if not uploader.login(config["email"], config["password"]):
        print("登录失败")
        sys.exit(1)

    # 主循环
    while True:
        url = input("\n输入YouTube链接 (或 'quit' 退出): ").strip()
        if url.lower() == 'quit':
            break

        if not url:
            continue

        uploader.upload_from_youtube(url)


if __name__ == "__main__":
    main()

