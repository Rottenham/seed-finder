# 种子寻找器

## 编译环境

- Python 3.8.0
- PyInstaller 5.3

## 编译步骤
生成 `seed_finder.spec` :
```cmd
pyinstaller --onefile -F -w seed_finder.py --icon=favicon.ico
```

修改 `seed_finder.spec` :
```
binaries=[('seedFinder.pyd','./')]
```

再次编译:

```cmd
pyinstaller seed_finder.spec
```

使用 `Enigma Virtual Box 9.90` 打包图标。
