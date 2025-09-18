import { escape } from '../utils/string';
class TextParser {
  source: any;

  constructor(source: any) {
    this.source = source;
  }

  toHTML() {
    let html = escape(this.source);
    html = html
      .replace(/\n/g, '</p><p>')
      .replace(/<p><\/p>/g, '<p><br /></p>')
      .replace(/^\s/, '&nbsp;')
      .replace(/\s$/, '&nbsp;')
      .replace(/\s\s/g, ' &nbsp;');
    if (html.includes('</p><p>')) {
      html = '<p>'.concat(html, '</p>');
    }
    return html;
  }
}
export default TextParser;
