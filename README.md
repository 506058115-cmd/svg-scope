# svg-scope

离线扫描 UTF-8 SVG 文本中常见的活动内容和资源引用，包括脚本元素、事件处理器、`javascript:` 属性、非片段链接、CSS `url()` 和 `@import`。工具不解析 XML、不执行 SVG 脚本，也不会访问外部资源或改写文件。扫描上限为 32 MiB。

## 使用

需要 Python 3.8+，不安装依赖。

~~~sh
python svg_scope.py ./image.svg
~~~

输出只包含扫描数量和各类命中数，不回显文件内容。发现命中时退出状态为 1；读取错误、编码错误、文件过大或未找到 SVG 标记时返回 2；未发现已识别项目时返回 0。

这是基于文本模式的静态提示器，不是 XML 验证器、消毒器，也不能证明文件安全。它可能把注释或文本中的标记误报为命中，也可能漏掉实体编码、CSS 转义或其他浏览器语法。允许的内容也可能被标记，例如数据 URI、站内链接或交互动画。请只在可信的 SVG 查看器中打开不可信文件。

## 许可

MIT，见 [LICENSE](LICENSE)。

## Linux x86_64 下载

- [单文件版](https://github.com/506058115-cmd/svg-scope/releases/download/v1.0.1/svg-scope-linux-x86_64-onefile.tar.gz)
- [目录版](https://github.com/506058115-cmd/svg-scope/releases/download/v1.0.1/svg-scope-linux-x86_64-onedir.tar.gz)
- [v1.0.1 Release 页面](https://github.com/506058115-cmd/svg-scope/releases/tag/v1.0.1)

压缩包附带构建信息和依赖许可证；Release 另附 SHA-256 校验文件。构建目标为 GNU/Linux x86_64。较旧 Linux 发行版可能需要兼容的 glibc。
