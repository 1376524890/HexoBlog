'use strict';

const fs = require('node:fs');
const path = require('node:path');
const escape = value => String(value).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

hexo.extend.generator.register('novels', function () {
  const book = JSON.parse(fs.readFileSync(path.join(this.base_dir, 'novels/tingcheng/book.json'), 'utf8'));
  const chapters = book.parts.flatMap(part => part.chapters.map(chapter => ({ ...chapter, part: part.title })));
  if (chapters.length !== 51 || chapters.some((chapter, index) => chapter.number !== index)) {
    throw new Error('《听城》章号必须从0到50连续排列，共51章。');
  }
  const base = `/novels/${book.slug}/`;
  const url = chapter => `${base}${String(chapter.number).padStart(3, '0')}/`;
  const anchor = (href, title, attrs = '') => `<a href="${href}" ${attrs}>${escape(title)}</a>`;
  const navigation = (index, position) => `<nav class="novel-navigation" aria-label="${position}章节导航">
    ${index > 0 ? anchor(url(chapters[index - 1]), '← 上一章', 'rel="prev"') : '<span aria-disabled="true">全书开篇</span>'}
    ${anchor(base, '目录')}
    ${index < chapters.length - 1 ? anchor(url(chapters[index + 1]), '下一章 →', 'rel="next"') : anchor(base, '已读至末章 · 返回目录')}
  </nav>`;
  const route = (url, title, content) => ({
    path: `${url.replace(/^\//, '')}index.html`, layout: 'page',
    data: { layout: 'page', title, subtitle: '小说 · 听城', content, comments: false,
      banner_img_height: 22, anchorjs: false, description: book.description,
      canonical_path: `${url.replace(/^\//, '')}index.html` }
  });
  const resume = `<a class="novel-resume" data-novel-resume="${book.slug}" hidden>继续上次阅读</a>`;
  const routes = [route('/novels/', '小说', `<section class="novel-library"><p class="novel-eyebrow">MARKTOM · 小说</p><h1>小说</h1>
    <article class="novel-book"><p class="novel-eyebrow">三部 · 51章（含第零章）</p><h2>${anchor(base, '听城')}</h2>
    <p>第一部　锈沟 / 第二部　名字 / 第三部　灰刀</p><div class="novel-actions">${anchor(base, '查看目录', 'class="novel-primary"')}${anchor(url(chapters[0]), '从头阅读')}${resume}</div></article></section>`),
    route(base, '《听城》章节目录', `<section class="novel-catalog"><p class="novel-eyebrow">${anchor('/novels/', '小说')} / 听城</p>
      <h1>听城</h1><p class="novel-muted">三部 · 51章 · 按章号顺序阅读</p>
      <div class="novel-actions">${anchor(url(chapters[0]), '从头阅读', 'class="novel-primary"')}${resume}</div>
      ${book.parts.map(part => `<section class="novel-volume"><h2>${escape(part.title)}</h2><ol class="novel-chapters">${part.chapters.map(chapter => `<li>${anchor(url(chapter), chapter.title)}</li>`).join('')}</ol></section>`).join('')}
    </section>`)
  ];
  chapters.forEach((chapter, index) => {
    const raw = fs.readFileSync(path.join(this.base_dir, 'novels', book.slug, chapter.file), 'utf8');
    const body = raw.replace(/^#\s+[^\r\n]+\r?\n/, '');
    const html = this.render.renderSync({ text: body, engine: 'md' });
    routes.push(route(url(chapter), `${chapter.title} · 听城`, `<section class="novel-reader" data-novel="${book.slug}" data-chapter="${chapter.number}" data-title="${escape(chapter.title)}">
      <p class="novel-eyebrow">${anchor(base, '听城')} / ${escape(chapter.part)}</p><h1>${escape(chapter.title)}</h1>
      ${navigation(index, '顶部')}
      <div class="novel-toolbar" role="group" aria-label="阅读设置"><span>字号</span><button type="button" data-font="-1" aria-label="缩小字号">A−</button><output id="novel-font-size" aria-live="polite">18</output><button type="button" data-font="1" aria-label="放大字号">A＋</button><button type="button" data-font="reset">重置</button><button type="button" data-novel-theme>切换深浅色</button></div>
      <div class="novel-body markdown-body">${html}</div>
      ${navigation(index, '底部')}<p class="novel-muted novel-end">${index === chapters.length - 1 ? '已读至当前目录的最后一章。' : escape(chapters[index + 1].title)}</p>
    </section>`));
  });
  return routes;
});
