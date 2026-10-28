'use strict';
// Overlay generated pages onto an existing gh-pages checkout without deleting static files.
const fs = require('node:fs');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const root = path.resolve(__dirname, '../..');
if (!process.argv[2]) throw new Error('用法：node tools/novels/prepare-publish.cjs /发布分支目录');
const target = fs.realpathSync(process.argv[2]);
if (!fs.existsSync(path.join(target, '.git')) || target === root) throw new Error('目标必须是独立的发布分支检出目录。');
const publicDir = path.join(root, 'public');
if (!fs.existsSync(path.join(publicDir, 'novels/tingcheng/050/index.html'))) throw new Error('请先生成并验证小说页面。');
// Pages recursively checks out submodules before it serves static files. The old
// publishing branch contained four gitlinks without a .gitmodules configuration.
if (!fs.existsSync(path.join(target, '.gitmodules'))) {
  const entries = execFileSync('git', ['-C', target, 'ls-files', '--stage', '-z']).toString().split('\0');
  for (const entry of entries) {
    if (!entry.startsWith('160000 ')) continue;
    const name = entry.slice(entry.indexOf('\t') + 1);
    execFileSync('git', ['-C', target, 'update-index', '--force-remove', '--', name]);
  }
}
fs.writeFileSync(path.join(target, '.nojekyll'), '');
let written = 0;
function copy(directory, relative = '') {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const next = path.join(relative, entry.name);
    if (entry.isDirectory()) copy(path.join(directory, entry.name), next);
    else if (entry.isFile()) {
      const content = fs.readFileSync(path.join(publicDir, next));
      const output = path.join(target, next);
      if (fs.existsSync(output) && fs.readFileSync(output).equals(content)) continue;
      fs.mkdirSync(path.dirname(output), { recursive: true });
      fs.writeFileSync(output, content); written++;
    }
  }
}
// Deploy only the novel feature. Old posts and their publication state are retained.
for (const relative of ['novels', 'categories/novels', 'tags/听城', 'tags/小说', 'archives/2026/10']) {
  copy(path.join(publicDir, relative), relative);
}
for (const relative of ['css/novels.css', 'js/novels.js']) {
  const output = path.join(target, relative);
  fs.mkdirSync(path.dirname(output), { recursive: true });
  fs.copyFileSync(path.join(publicDir, relative), output); written++;
}
function patch(relative, transform) {
  const file = path.join(target, relative);
  if (!fs.existsSync(file)) throw new Error(`发布分支缺少 ${relative}`);
  const content = fs.readFileSync(file, 'utf8');
  const next = transform(content);
  if (next !== content) fs.writeFileSync(file, next);
}
const introduction = '/novels/tingcheng-introduction/';
const home = fs.readFileSync(path.join(publicDir, 'index.html'), 'utf8');
const card = home.match(/<div class="row mx-auto index-card">[\s\S]*?<\/article>\s*<\/div>/)?.[0];
if (!card || !card.includes(introduction)) throw new Error('未找到小说首页入口。');
patch('index.html', content => content.includes(introduction) ? content : content.replace('<div class="row mx-auto index-card">', `${card}\n<div class="row mx-auto index-card">`));
patch('categories/index.html', content => content.includes('href="/categories/novels/"') ? content : content.replace('<div class="category-list">', `<div class="category-list"><div class="category row nomargin-x"><a class="category-item list-group-item category-item-action col-10 col-md-11 col-xm-11" href="/categories/novels/">小说</a><a class="category-count col-2 col-md-1 col-xm-1" href="/categories/novels/"><i class="iconfont icon-articles"></i><span>1</span></a></div>`));
patch('tags/index.html', content => content.includes('/tags/%E5%90%AC%E5%9F%8E/') ? content : content.replace('<div class="text-center tagcloud">', '<div class="text-center tagcloud"><a href="/tags/%E5%90%AC%E5%9F%8E/" style="font-size:15px">听城</a> <a href="/tags/%E5%B0%8F%E8%AF%B4/" style="font-size:15px">小说</a> '));
for (const relative of ['archives/index.html', 'archives/2026/index.html']) {
  patch(relative, content => {
    if (content.includes(introduction)) return content;
    return content.replace(/共计 (\d+) 篇文章/, (_, count) => `共计 ${Number(count) + 1} 篇文章`)
      .replace('<p class="h5">2026</p>', `<p class="h5">2026</p><a href="${introduction}" class="list-group-item list-group-item-action"><time>10-28</time><div class="list-group-item-title">《听城》小说阅读入口</div></a>`);
  });
}
let navigation = 0;
function addNavigation(directory) {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    if (entry.name.startsWith('.') || ['node_modules', 'venv'].includes(entry.name)) continue;
    const file = path.join(directory, entry.name);
    if (entry.isDirectory()) addNavigation(file);
    else if (entry.isFile() && entry.name.endsWith('.html')) {
      const content = fs.readFileSync(file, 'utf8');
      const patched = content.replace(/(<nav id="navbar"[\s\S]*?)(<\/ul>)/, (match, before, end) => {
        if (before.includes('href="/novels/"')) return match;
        navigation++;
        return `${before}<li class="nav-item"><a class="nav-link" href="/novels/"><i class="iconfont icon-book"></i><span>小说</span></a></li>${end}`;
      });
      if (patched !== content) fs.writeFileSync(file, patched);
    }
  }
}
addNavigation(target);
console.log(`已更新/新增 ${written} 个生成文件，为 ${navigation} 个旧页面补充小说导航；未删除文件。`);
