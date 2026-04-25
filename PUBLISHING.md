# 发布到 PyPI 指南 / Publishing to PyPI Guide

## 准备工作 / Prerequisites

1. 注册 PyPI 账号 / Register a PyPI account:
   - 正式版：https://pypi.org/account/register/
   - 测试版：https://test.pypi.org/account/register/

2. 安装发布工具 / Install publishing tools:
   ```bash
   pip install build twine
   ```

## 发布步骤 / Publishing Steps

### 1. 更新版本号 / Update Version

编辑 `healthy_pet/__init__.py` 和 `pyproject.toml` 中的版本号：
```python
__version__ = "0.1.0"  # 修改为新版本
```

### 2. 构建包 / Build Package

```bash
python -m build
```

这会在 `dist/` 目录生成两个文件：
- `healthy_pet-0.1.0.tar.gz` (源码包)
- `healthy_pet-0.1.0-py3-none-any.whl` (wheel 包)

### 3. 测试上传（可选）/ Test Upload (Optional)

先上传到测试服务器：
```bash
python -m twine upload --repository testpypi dist/*
```

测试安装：
```bash
pip install --index-url https://test.pypi.org/simple/ healthy-pet
```

### 4. 正式上传 / Official Upload

```bash
python -m twine upload dist/*
```

输入你的 PyPI 用户名和密码。

### 5. 验证 / Verify

```bash
pip install healthy-pet
healthy-pet
```

## 注意事项 / Notes

1. **版本号不能重复**：每次发布必须使用新的版本号
2. **包名唯一**：`healthy-pet` 这个名字在 PyPI 上必须是唯一的
3. **资源文件**：确保 `MANIFEST.in` 包含了所有需要的资源文件
4. **测试**：发布前在本地充分测试

## 版本号规范 / Version Numbering

遵循语义化版本 (Semantic Versioning)：
- `0.1.0` - 初始版本
- `0.1.1` - Bug 修复
- `0.2.0` - 新功能
- `1.0.0` - 稳定版本

## 清理 / Cleanup

发布后清理构建文件：
```bash
rm -rf build/ dist/ *.egg-info/
```

Windows:
```cmd
rmdir /s /q build dist
del /s /q *.egg-info
```
