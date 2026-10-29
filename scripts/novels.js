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
  const artBase = `/img/novels/${book.slug}/`;
  const galleryUrl = `${base}art/`;
  const cover = `<a class="novel-cover" href="${base}" aria-label="查看《听城》目录"><img src="${artBase}cover.webp" alt="《听城》封面：雨夜里的义臂修理铺与工业街巷" width="1024" height="1536" fetchpriority="high" decoding="async"></a>`;
  const artworks = [
    { file: 'xiugou', title: '锈沟', kind: '世界观概念图', width: 1672, height: 941, alt: '潮湿的工业街巷，两侧是义肢修理铺和面摊，远处工厂烟囱林立' },
    { file: 'sentinel-arm', title: '哨兵义臂', kind: '道具概念图', width: 1536, height: 1024, alt: '暖色台灯下的旧机械义臂，拆开的外壳露出线路与传动结构' },
    { file: 'wangxiangtai', title: '望乡台', kind: '人物场景概念图', width: 1536, height: 1024, alt: '工业城夜景前，两个人坐在高处，围着小炉吃烤红薯' }
  ];
  const routes = [route('/novels/', '小说', `<section class="novel-library"><p class="novel-eyebrow">MARKTOM · 小说</p><h1>小说</h1>
    <article class="novel-book novel-book-with-cover">${cover}<div class="novel-book-info"><p class="novel-eyebrow">三部 · 51章（含第零章）</p><h2>${anchor(base, '听城')}</h2>
    <p>第一部　锈沟 / 第二部　名字 / 第三部　灰刀</p><div class="novel-actions">${anchor(base, '查看目录', 'class="novel-primary"')}${anchor(url(chapters[0]), '从头阅读')}${resume}${anchor(galleryUrl, '概念图集 →')}</div></div></article></section>`),
    route(base, '《听城》章节目录', `<section class="novel-catalog"><p class="novel-eyebrow">${anchor('/novels/', '小说')} / 听城</p>
      <div class="novel-book-with-cover novel-catalog-hero">${cover}<div class="novel-book-info"><h1>听城</h1><p class="novel-muted">三部 · 51章 · 按章号顺序阅读</p>
      <p class="novel-muted">第一部　锈沟 / 第二部　名字 / 第三部　灰刀</p>
      <div class="novel-actions">${anchor(url(chapters[0]), '从头阅读', 'class="novel-primary"')}${resume}${anchor(galleryUrl, '概念图集 →')}</div></div></div>
      ${book.parts.map(part => `<section class="novel-volume"><h2>${escape(part.title)}</h2><ol class="novel-chapters">${part.chapters.map(chapter => `<li>${anchor(url(chapter), chapter.title)}</li>`).join('')}</ol></section>`).join('')}
    </section>`),
    route(galleryUrl, '《听城》概念图集', `<section class="novel-catalog novel-gallery"><p class="novel-eyebrow">${anchor('/novels/', '小说')} / ${anchor(base, '听城')} / 概念图集</p>
      <h1>听城 · 概念图集</h1><p class="novel-muted">街巷、旧物与城里的人。三张概念图，取自《听城》的世界。</p>
      <div class="novel-actions">${anchor(base, '返回章节目录', 'class="novel-primary"')}${resume}</div>
      ${artworks.map(art => `<figure class="novel-artwork"><a href="${artBase}${art.file}.webp" target="_blank" rel="noopener" aria-label="查看${escape(art.title)}大图"><img src="${artBase}${art.file}.webp" alt="${escape(art.alt)}" width="${art.width}" height="${art.height}" loading="lazy" decoding="async"></a><figcaption><span class="novel-eyebrow">${escape(art.kind)}</span><h2>${escape(art.title)}</h2></figcaption></figure>`).join('')}
      <div class="novel-actions">${anchor(base, '← 返回章节目录')}</div>
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
