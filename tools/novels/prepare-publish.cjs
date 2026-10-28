'use strict';
// Overlay generated pages onto an existing gh-pages checkout without deleting static files.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
if (!process.argv[2]) throw new Error('用法：node tools/novels/prepare-publish.cjs /发布分支目录');
const target = fs.realpathSync(process.argv[2]);
if (!fs.existsSync(path.join(target, '.git')) || target === root) throw new Error('目标必须是独立的发布分支检出目录。');
const publicDir = path.join(root, 'public');
if (!fs.existsSync(path.join(publicDir, 'novels/tingcheng/050/index.html'))) throw new Error('请先生成并验证小说页面。');
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
copy(publicDir);
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
