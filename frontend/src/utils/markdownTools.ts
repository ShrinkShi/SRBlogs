export type MarkdownToolbarCommand =
  | { type: 'bold' }
  | { type: 'italic' }
  | { type: 'strike' }
  | { type: 'ordered-list' }
  | { type: 'quote' }
  | { type: 'inline-code' }
  | { type: 'code-block' }
  | { type: 'table' }
  | { type: 'link' }
  | { type: 'image' }
  | { type: 'color'; color: string }

export type MarkdownToolbarCommandType = MarkdownToolbarCommand['type']

export interface MarkdownToolbarItem {
  type: MarkdownToolbarCommandType
  label: string
  title: string
}

export interface MarkdownInsertion {
  text: string
  selectFrom?: number
  selectTo?: number
}

export const markdownToolbarItems: MarkdownToolbarItem[] = [
  { type: 'bold', label: 'B', title: '加粗' },
  { type: 'italic', label: 'I', title: '斜体' },
  { type: 'strike', label: 'S', title: '删除线' },
  { type: 'ordered-list', label: '1.', title: '有序列表' },
  { type: 'quote', label: '>', title: '引用' },
  { type: 'inline-code', label: '`', title: '行内代码' },
  { type: 'code-block', label: '{}', title: '代码块' },
  { type: 'table', label: '表', title: '表格' },
  { type: 'link', label: '链', title: '链接' },
  { type: 'image', label: '图', title: '图片' },
  { type: 'color', label: '色', title: '颜色' }
]

export const markdownColorPresets = ['#67e8f9', '#a78bfa', '#f472b6', '#22c55e', '#facc15', '#fb7185', '#ffffff']

export function normalizeMarkdownColor(color: string) {
  const normalized = color.trim()
  return /^#[0-9a-fA-F]{6}$/.test(normalized) ? normalized : ''
}

export function buildMarkdownInsertion(
  command: MarkdownToolbarCommand,
  getSelectedText: (fallback: string) => string
): MarkdownInsertion | null {
  const wrap = (prefix: string, suffix = prefix, fallback = '文本'): MarkdownInsertion => {
    const text = getSelectedText(fallback)
    return {
      text: `${prefix}${text}${suffix}`,
      selectFrom: prefix.length,
      selectTo: prefix.length + text.length
    }
  }

  switch (command.type) {
    case 'bold':
      return wrap('**', '**', '加粗文字')
    case 'italic':
      return wrap('*', '*', '斜体文字')
    case 'strike':
      return wrap('~~', '~~', '删除线文字')
    case 'ordered-list': {
      const text = getSelectedText('列表项')
      return { text: `${text.split('\n').map((line, index) => `${index + 1}. ${line || '列表项'}`).join('\n')}\n` }
    }
    case 'quote': {
      const text = getSelectedText('引用内容')
      return { text: `${text.split('\n').map((line) => `> ${line || '引用内容'}`).join('\n')}\n` }
    }
    case 'inline-code':
      return wrap('`', '`', '代码')
    case 'code-block': {
      const text = getSelectedText('console.log("hello")')
      const prefix = '\n```ts\n'
      const suffix = '\n```\n'
      return { text: `${prefix}${text}${suffix}`, selectFrom: prefix.length, selectTo: prefix.length + text.length }
    }
    case 'table':
      return { text: '\n| 标题 | 内容 |\n| --- | --- |\n| 示例 | 文本 |\n' }
    case 'link':
      return wrap('[', '](https://example.com)', '链接文本')
    case 'image':
      return { text: '\n![图片描述](https://example.com/image.png)\n' }
    case 'color': {
      const color = normalizeMarkdownColor(command.color)
      if (!color) return null
      return wrap(`<span style="color:${color}">`, '</span>', '彩色文字')
    }
    default:
      return null
  }
}
