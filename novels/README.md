# 小说阅读区

《听城》正文保存在 `novels/tingcheng/`，`book.json` 保存分卷和章节顺序。
`source/_posts/tingcheng-reading.md` 是小说分类和博客首页的入口文章。

## 更新原稿

在博客目录执行：

```sh
npm run sync:novel -- "/原稿目录/听城"
npm run build
npm run server
```

同步工具只读取三部目录内编号为00到50的章节Markdown，不会导入全文汇总、衔接核查或伏笔文档。正文逐字节复制，不润色原文。同步前检查51章完整且章号连续。

目录页、章节页和前后章导航由 `scripts/novels.js` 在Hexo生成时自动创建，不进入博文流；分类由入口文章提供。站点仍使用Fluid主题，样式和交互分别在 `source/css/novels.css`、`source/js/novels.js`。

字号和阅读位置保存在当前浏览器的localStorage；无法访问存储时仍可正常阅读。继续阅读通过目录或小说入口的按钮恢复。深浅色复用Fluid的切换按钮。

## 发布

检查本地预览后提交源码到master，再将Hexo生成的public部署至原有gh-pages分支。发布前核对线上分支。也可在独立的gh-pages检出目录执行 `node tools/novels/prepare-publish.cjs /发布分支目录`，只加入小说相关页面和入口、补充旧页面导航，保留旧博文和静态资源。

发布工具还会写入 `.nojekyll`，并在发布分支缺少 `.gitmodules` 时移除无效的子仓库索引引用，避免GitHub Pages在拉取阶段失败。原始源码仓库中的子仓库引用不受影响。
