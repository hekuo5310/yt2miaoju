# yt2miaoju

自动从 YouTube 下载视频并上传到 miaoju 平台。

## 特别鸣谢

- [猫](https://cnb.cool/u/smallcat) 把api文档和写好的手动搬运脚本给了我
- [SDCOM](https://cnb.cool/u/SDCOM) 全能程序员
- [Foxcode](https://foxcode.rjj.cc/auth/register?aff=BO9IXM) 非常便宜的claude code渠道喵！推荐使用喵！

## 友情链接

- [喵聚|Miaoju](https://miaoju.top/) 
- [山梨字幕组](https://yamanasub.cn/) 帮助超500万人看懂世界
- [HKMC云](https://cloud.hkmc.online/) 记得选择销售猫猫，喵！

## 用前须知

**路径被写死了！需要自己修改！**

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

- 支持系统代理设置
- 视频上传后需等待平台审核

## 文件说明

- `youtube_uploader.py` - 主程序
- `config.json` - 账号配置
- `README.md` - 说明文档
