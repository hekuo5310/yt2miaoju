# yt2miaoju

自动从 YouTube 下载视频并上传到 miaoju 平台。

## 功能

- 自动下载 YouTube 视频和封面
- 自动提取标题和简介
- 分片上传视频（支持大文件）
- 自动转换封面格式（webp -> jpg）
- 支持系统代理

## 安装

```bash
pip install yt-dlp requests Pillow
```

## 配置

编辑 `config.json`：

```json
{
  "email": "your_email@example.com",
  "password": "your_password"
}
```

## 使用

```bash
python youtube_uploader.py
```

输入 YouTube 链接，程序会自动完成下载和上传。

输入 `quit` 退出程序。

## 注意事项

- 需要系统安装 yt-dlp
- 支持系统代理设置
- 视频上传后需等待平台审核

## 文件说明

- `youtube_uploader.py` - 主程序
- `config.json` - 账号配置
- `README.md` - 说明文档
