#!/usr/bin/env node
'use strict';
// Copy manuscripts verbatim; the site generator creates the table of contents and navigation.
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const input = process.argv[2];
if (!input) throw new Error('用法：npm run sync:novel -- /原稿/听城');
const source = path.resolve(input);
const output = path.join(root, 'novels/tingcheng');
const folders = ['第一部-锈沟', '第二部-名字', '第三部-灰刀'];
const staged = [];
const parts = folders.map(folder => ({ title: folder.replace('-', '　'), chapters:
  fs.readdirSync(path.join(source, folder)).filter(file => /^\d{2}-.+\.md$/.test(file)).sort().map(file => {
    const relative = `${folder}/${file}`;
    const content = fs.readFileSync(path.join(source, relative));
    const match = content.toString('utf8').match(/^#\s+([^\r\n]+)/);
    if (!match || !content.length) throw new Error(`原稿缺少章节标题：${relative}`);
    staged.push({ relative, content });
    return { number: Number(file.slice(0, 2)), title: match[1].trim(), file: relative };
  })
}));
const chapters = parts.flatMap(part => part.chapters);
if (chapters.length !== 51 || chapters.some((chapter, index) => chapter.number !== index)) {
  throw new Error('需要第零章至第五十章，共51章；未写入任何文件。');
}
for (const { relative, content } of staged) {
  const target = path.join(output, relative);
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.writeFileSync(target, content);
}
fs.writeFileSync(path.join(output, 'book.json'), JSON.stringify({ title: '听城', slug: 'tingcheng',
  description: '《听城》分卷目录与章节阅读。', parts }, null, 2) + '\n');
console.log(`已同步 ${chapters.length} 章，原文未改动。`);
