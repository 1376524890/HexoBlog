'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const read = name => fs.readFileSync(path.join(root, 'public', name), 'utf8');
const book = JSON.parse(fs.readFileSync(path.join(root, 'novels/tingcheng/book.json')));
const chapters = book.parts.flatMap(part => part.chapters);
const chapterUrl = number => `/novels/tingcheng/${String(number).padStart(3, '0')}/`;
const catalog = read('novels/tingcheng/index.html');
const gallery = read('novels/tingcheng/art/index.html');
assert.ok(catalog.includes('/img/novels/tingcheng/cover.webp'));
assert.ok(catalog.includes('href="/novels/tingcheng/art/"'));
for (const asset of ['cover', 'xiugou', 'sentinel-arm', 'wangxiangtai']) {
  assert.ok(fs.existsSync(path.join(root, 'public/img/novels/tingcheng', `${asset}.webp`)));
  if (asset !== 'cover') assert.ok(gallery.includes(`/img/novels/tingcheng/${asset}.webp`));
}
assert.equal(chapters.length, 51);
assert.equal((catalog.match(/<li><a href="\/novels\/tingcheng\/\d{3}\//g) || []).length, 51);
for (const [index, chapter] of chapters.entries()) {
  assert.equal(chapter.number, index);
  const html = read(`${chapterUrl(index).slice(1)}index.html`);
  assert.ok(html.includes('class="novel-body markdown-body"'));
  assert.ok(!html.includes('/img/novels/tingcheng/'), `章节${index}不应插入封面或概念图`);
  assert.ok(html.includes(`data-chapter="${index}"`));
  assert.ok(html.includes('/css/novels.css') && html.includes('/js/novels.js'));
  assert.equal((html.match(/rel="prev"/g) || []).length, index ? 2 : 0);
  assert.equal((html.match(/rel="next"/g) || []).length, index < 50 ? 2 : 0);
  if (index) assert.ok(html.includes(`href="${chapterUrl(index - 1)}"`));
  if (index < 50) assert.ok(html.includes(`href="${chapterUrl(index + 1)}"`));
  assert.ok(html.includes(`https://blog.plk161211.top${chapterUrl(index)}`));
}
for (const page of ['index.html', 'categories/novels/index.html', 'novels/index.html']) {
  assert.ok(read(page).includes('听城'));
}
assert.ok(!read('index.html').includes('class="novel-reader"'));
// Every novel link emitted on novel pages must resolve to a generated HTML page.
const pages = ['novels/index.html', 'novels/tingcheng/index.html', 'novels/tingcheng/art/index.html', ...chapters.map(c => `${chapterUrl(c.number).slice(1)}index.html`)];
for (const page of pages) {
  for (const [, href] of read(page).matchAll(/href="(\/novels\/[^"#?]*)"/g)) {
    assert.ok(fs.existsSync(path.join(root, 'public', href.slice(1), 'index.html')), `${page}: broken link ${href}`);
  }
}
console.log('通过：51章、三部分卷、首尾与跨卷导航、所有小说链接、分类和首页入口、封面与概念图集，章节页无插图。');
