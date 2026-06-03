export type TagColorMap = Record<string, string>

export function normalizeTagColor(value: unknown, fallback = '#334155') {
  const text = String(value || '').trim()
  if (/^#[0-9a-fA-F]{6}$/.test(text)) return text
  if (/^#[0-9a-fA-F]{3}$/.test(text)) {
    return `#${text.slice(1).split('').map((char) => `${char}${char}`).join('')}`
  }
  return fallback
}

export function readableTagTextColor(color: string) {
  const hex = normalizeTagColor(color).slice(1)
  const red = parseInt(hex.slice(0, 2), 16)
  const green = parseInt(hex.slice(2, 4), 16)
  const blue = parseInt(hex.slice(4, 6), 16)
  const luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255
  return luminance > 0.58 ? '#050505' : '#ffffff'
}

export function tagStyle(tag: string, colors?: TagColorMap) {
  const background = normalizeTagColor(colors?.[tag])
  return {
    backgroundColor: background,
    borderColor: background,
    color: readableTagTextColor(background)
  }
}
