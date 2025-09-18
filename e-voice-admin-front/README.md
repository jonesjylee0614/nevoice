##  GoFly单服务版 -业务前端代码
你开发的业务代码在这里编写，这里的超级管理账号admin端“业务端管理”里的账号添加和编辑。
### 快速运行项目
建议使用 pnpm

```shell
# 初始化安装依赖
pnpm i
```
```shell
# 运行项目
pnpm run dev

```
```shell
# 打包项目
pnpm run build
```

### 配置插件
根目录下新建`.env.local`文件,录入以下内容

```
# 这个位置是你的编辑器可执行文件路径，用于code-inspector-plugin插件唤醒
CODE_EDITOR=/home/leozy/.local/share/JetBrains/Toolbox/apps/intellij-idea-ultimate/bin/idea

```

打包注意事项：
1.如果您是独立域名部署，打包时候需要修改两个地方：
（1）、config/vite.config.prod.ts中的mergeConfig下的：base:""。
（2）、src/router/index.ts中的createRouter下的： history: createWebHashHistory('') 。
2.如果您是部署在后端代码二级目录下，同样打包时候需要修改两个地方（例如业务端webbusiness，按照您的需求替换“webbusiness”）：
（1）、config/vite.config.prod.ts中的mergeConfig下的：base: process.env.NODE_ENV === 'production' ? '/webbusiness/' : ''。
（2）、src/router/index.ts中的createRouter下的：history: createWebHashHistory(process.env.NODE_ENV === 'production' ? '/webbusiness/' : '')。

### 开发说明
您在开发时候请您参考文档说明 https://doc.goflys.cn/docview?id=25

 